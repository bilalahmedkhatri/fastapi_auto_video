"""
Auto Migration System for FastAPI SQLModel
Automatically detects and adds missing columns to existing tables based on model definitions.
"""

from sqlalchemy import text, inspect, MetaData
from sqlmodel import SQLModel
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AutoMigration:
    """
    Automatically migrates database schema to match SQLModel definitions.
    Adds missing columns to existing tables.
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.inspector = inspect(engine)
    
    def get_model_fields(self, model_class) -> Dict[str, Any]:
        """Extract field definitions from SQLModel class"""
        fields = {}
        
        # Get table columns from SQLModel metadata
        if hasattr(model_class, '__table__'):
            for column in model_class.__table__.columns:
                field_info = {
                    'name': column.name,
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'default': column.default,
                    'foreign_key': None
                }
                
                # Check for foreign keys
                if column.foreign_keys:
                    fk = list(column.foreign_keys)[0]
                    field_info['foreign_key'] = str(fk.target_fullname)
                
                fields[column.name] = field_info
        
        return fields
    
    def get_database_columns(self, table_name: str) -> Dict[str, Any]:
        """Get existing columns with their types from database table"""
        try:
            columns_info = {}
            columns = self.inspector.get_columns(table_name)
            for col in columns:
                columns_info[col['name']] = {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': col.get('default'),
                    'autoincrement': col.get('autoincrement', False)
                }
            return columns_info
        except Exception as e:
            logger.warning(f"Could not get columns for table {table_name}: {e}")
            return {}
    
    def generate_column_sql(self, field_name: str, field_info: Dict[str, Any]) -> str:
        """Generate SQL for adding a column"""
        sql_type = field_info['type']
        
        # Convert SQLAlchemy types to PostgreSQL types
        type_mapping = {
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT',
            'INTEGER': 'INTEGER',
            'BOOLEAN': 'BOOLEAN',
            'TIMESTAMP': 'TIMESTAMP',
            'DATETIME': 'TIMESTAMP',
            'UUID': 'UUID',
            'FLOAT': 'REAL',
            'NUMERIC': 'NUMERIC'
        }
        
        # Extract base type (remove length specifications)
        base_type = sql_type.split('(')[0].upper()
        pg_type = type_mapping.get(base_type, sql_type)
        
        # Build column definition
        column_def = f"{field_name} {pg_type}"
        
        # Add nullable/not null
        if not field_info['nullable']:
            # For existing tables, we can't add NOT NULL columns without defaults
            # So we make them nullable and let application handle it
            pass  # Keep nullable for safety
        
        # Add foreign key reference if exists
        if field_info['foreign_key']:
            column_def += f" REFERENCES {field_info['foreign_key']}"
        
        return column_def
    
    def add_missing_column(self, table_name: str, field_name: str, field_info: Dict[str, Any]) -> bool:
        """Add a missing column to the table"""
        try:
            column_sql = self.generate_column_sql(field_name, field_info)
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_sql}"
            
            with self.engine.connect() as conn:
                conn.execute(text(alter_sql))
                conn.commit()
                logger.info(f"✅ Added column '{field_name}' to table '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add column '{field_name}' to table '{table_name}': {e}")
            return False
    
    def normalize_type(self, db_type: str) -> str:
        """Normalize database type for comparison"""
        # Convert to uppercase and remove length specifications
        normalized = str(db_type).upper().split('(')[0]
        
        # Map common type variations
        type_mapping = {
            'INTEGER': 'INTEGER',
            'INT': 'INTEGER',
            'BIGINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT',
            'STRING': 'VARCHAR',
            'BOOLEAN': 'BOOLEAN',
            'BOOL': 'BOOLEAN',
            'TIMESTAMP': 'TIMESTAMP',
            'DATETIME': 'TIMESTAMP',
            'UUID': 'UUID',
            'FLOAT': 'FLOAT',
            'REAL': 'FLOAT',
            'NUMERIC': 'NUMERIC',
            'DECIMAL': 'NUMERIC'
        }
        
        return type_mapping.get(normalized, normalized)
    
    def types_are_compatible(self, model_type: str, db_type: str) -> bool:
        """Check if model type and database type are compatible"""
        model_normalized = self.normalize_type(model_type)
        db_normalized = self.normalize_type(db_type)
        
        # Direct match
        if model_normalized == db_normalized:
            return True
        
        # Compatible type pairs
        compatible_types = [
            ('INTEGER', 'BIGINT'),
            ('VARCHAR', 'TEXT'),
            ('TIMESTAMP', 'DATETIME'),
            ('FLOAT', 'REAL'),
            ('NUMERIC', 'DECIMAL'),
            ('BOOLEAN', 'BOOL')
        ]
        
        for type1, type2 in compatible_types:
            if (model_normalized == type1 and db_normalized == type2) or \
               (model_normalized == type2 and db_normalized == type1):
                return True
        
        return False
    
    def can_convert_data(self, table_name: str, field_name: str, target_type: str) -> bool:
        """Check if existing data can be safely converted to target type"""
        try:
            with self.engine.connect() as conn:
                # Check if table has any data
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = count_result.scalar()
                
                if count == 0:
                    return True  # No data, conversion is safe
                
                # Check if conversion would succeed on existing data
                target_normalized = self.normalize_type(target_type)
                test_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} IS NOT NULL"
                
                # Try a test conversion on non-null values
                if target_normalized in ('INTEGER', 'BIGINT', 'SMALLINT'):
                    # For integer types, check if all values are numeric
                    test_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} IS NOT NULL AND {field_name}::text !~ '^[0-9]+$'"
                elif target_normalized == 'BOOLEAN':
                    # For boolean, check if values are convertible
                    test_sql = f"SELECT COUNT(*) FROM {table_name} WHERE {field_name} IS NOT NULL AND {field_name}::text NOT IN ('true', 'false', 't', 'f', '1', '0', 'yes', 'no')"
                
                incompatible_result = conn.execute(text(test_sql))
                incompatible_count = incompatible_result.scalar()
                
                return incompatible_count == 0
                
        except Exception as e:
            logger.warning(f"[WARNING] Cannot validate data conversion for '{field_name}': {e}")
            return False  # Safer to skip if we can't validate
    
    def update_column_type(self, table_name: str, field_name: str, field_info: Dict[str, Any], 
                          current_db_type: str) -> bool:
        """Update column type if it has changed"""
        try:
            new_type_sql = self.normalize_type(field_info['type'])
            
            # Check if data can be converted safely
            if not self.can_convert_data(table_name, field_name, new_type_sql):
                logger.warning(f"[SKIP] Cannot convert '{field_name}' in '{table_name}' - incompatible existing data (contains non-numeric values)")
                return False
            
            # Generate ALTER COLUMN SQL
            alter_sql = f"ALTER TABLE {table_name} ALTER COLUMN {field_name} TYPE {new_type_sql}"
            
            # For PostgreSQL, we might need USING clause for incompatible type conversions
            if not self.types_are_compatible(field_info['type'], current_db_type):
                # Add USING clause for safe conversion
                alter_sql += f" USING {field_name}::{new_type_sql}"
            
            with self.engine.connect() as conn:
                conn.execute(text(alter_sql))
                conn.commit()
                logger.info(f"[OK] Updated column '{field_name}' type from {current_db_type} to {new_type_sql} in table '{table_name}'")
                return True
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to update column type '{field_name}' in table '{table_name}': {e}")
            return False
    
    def migrate_table(self, model_class) -> Dict[str, Any]:
        """Migrate a single table to match its model"""
        if not hasattr(model_class, '__tablename__'):
            return {'status': 'skipped', 'reason': 'No table name defined'}
        
        table_name = model_class.__tablename__
        migration_result = {
            'table': table_name,
            'status': 'success',
            'added_columns': [],
            'updated_columns': [],
            'errors': []
        }
        
        # Check if table exists
        if table_name not in self.inspector.get_table_names():
            migration_result['status'] = 'skipped'
            migration_result['reason'] = 'Table does not exist (will be created by create_all)'
            return migration_result
        
        # Get model fields and existing columns
        model_fields = self.get_model_fields(model_class)
        existing_columns = self.get_database_columns(table_name)
        
        # Find missing columns
        missing_columns = []
        type_changes = []
        
        for field_name, field_info in model_fields.items():
            if field_name not in existing_columns:
                # Column doesn't exist - add it
                missing_columns.append((field_name, field_info))
            else:
                # Column exists - check if type changed
                current_db_info = existing_columns[field_name]
                if not self.types_are_compatible(field_info['type'], current_db_info['type']):
                    type_changes.append((field_name, field_info, current_db_info['type']))
        
        # Add missing columns
        for field_name, field_info in missing_columns:
            if self.add_missing_column(table_name, field_name, field_info):
                migration_result['added_columns'].append(field_name)
            else:
                migration_result['errors'].append(f"Failed to add {field_name}")
        
        # Update column types that have changed
        for field_name, field_info, current_type in type_changes:
            if self.update_column_type(table_name, field_name, field_info, current_type):
                migration_result['updated_columns'].append({
                    'column': field_name,
                    'from': current_type,
                    'to': field_info['type']
                })
            else:
                migration_result['errors'].append(f"Failed to update type for {field_name}")
        
        # Determine final status
        if migration_result['errors']:
            migration_result['status'] = 'partial'
        elif not migration_result['added_columns'] and not migration_result['updated_columns']:
            migration_result['status'] = 'no_changes'
        
        return migration_result
    
    def run_auto_migration(self) -> Dict[str, Any]:
        """Run automatic migration for all SQLModel classes"""
        logger.info("[PROCESSING] Starting automatic database migration...")
        
        migration_summary = {
            'total_tables': 0,
            'migrated_tables': 0,
            'total_columns_added': 0,
            'total_columns_updated': 0,
            'results': [],
            'errors': []
        }
        
        # Get all SQLModel classes
        model_classes = []
        for cls in SQLModel.__subclasses__():
            if hasattr(cls, '__tablename__'):
                model_classes.append(cls)
        
        migration_summary['total_tables'] = len(model_classes)
        
        # Migrate each table
        for model_class in model_classes:
            try:
                result = self.migrate_table(model_class)
                migration_summary['results'].append(result)
                
                if result['status'] in ['success', 'partial']:
                    migration_summary['migrated_tables'] += 1
                    migration_summary['total_columns_added'] += len(result.get('added_columns', []))
                    migration_summary['total_columns_updated'] += len(result.get('updated_columns', []))
                
            except Exception as e:
                error_msg = f"Error migrating {getattr(model_class, '__tablename__', 'unknown')}: {e}"
                migration_summary['errors'].append(error_msg)
                logger.error(error_msg)
        
        # Log summary
        total_changes = migration_summary['total_columns_added'] + migration_summary['total_columns_updated']
        if total_changes > 0:
            logger.info(f"[COMPLETE] Migration completed: Added {migration_summary['total_columns_added']} columns, updated {migration_summary['total_columns_updated']} column types across {migration_summary['migrated_tables']} tables")
        else:
            logger.info("[INFO] No migrations needed - database schema is up to date")
        
        if migration_summary['errors']:
            logger.warning(f"[WARNING] {len(migration_summary['errors'])} errors occurred during migration")
        
        return migration_summary

def run_auto_migration(engine) -> Dict[str, Any]:
    """
    Convenience function to run auto migration.
    Returns migration summary.
    """
    migrator = AutoMigration(engine)
    return migrator.run_auto_migration()

# Example usage and testing
if __name__ == "__main__":
    from db_models import engine
    
    # Test the migration system
    result = run_auto_migration(engine)
    
    print("\n📊 Migration Summary:")
    print(f"Tables checked: {result['total_tables']}")
    print(f"Tables migrated: {result['migrated_tables']}")
    print(f"Columns added: {result['total_columns_added']}")
    
    if result['errors']:
        print("\n❌ Errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("\n📋 Detailed Results:")
    for table_result in result['results']:
        status_emoji = {
            'success': '✅',
            'partial': '⚠️',
            'no_changes': 'ℹ️',
            'skipped': '⏭️'
        }.get(table_result['status'], '❓')
        
        print(f"{status_emoji} {table_result['table']}: {table_result['status']}")
        if table_result.get('added_columns'):
            for col in table_result['added_columns']:
                print(f"    + Added column: {col}")
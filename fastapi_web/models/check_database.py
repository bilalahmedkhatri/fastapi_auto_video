import psycopg2

try:
    # First try to connect to postgres database to create our database
    conn = psycopg2.connect(
        dbname='postgres',
        user='admin',
        password='admin',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Try to create the database
    try:
        cur.execute('CREATE DATABASE auto_video_db')
        print('Database auto_video_db created successfully')
    except Exception as e:
        print(f'Could not create database: {e}')
    
    conn.close()
    
    # Now connect to our database and list tables
    conn = psycopg2.connect(
        dbname='auto_video_db',
        user='admin',
        password='admin',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    
    # List all tables in the database
    cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public'
    """)
    
    tables = cur.fetchall()
    print("Tables in auto_video_db:")
    for table in tables:
        print(f"- {table[0]}")
        
        # For each table, list its columns
        cur.execute(f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table[0]}' AND table_schema = 'public'
        """)
        
        columns = cur.fetchall()
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
    
    conn.close()
except Exception as e:
    print(f"Connection error: {e}")

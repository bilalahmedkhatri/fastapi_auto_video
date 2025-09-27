"""
OpenRouter Models API Client

This module provides a class to fetch AI model information from OpenRouter's API 
and save it to the local database.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlmodel import Session, select

# Import database models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.db_models import AIModel, engine


logger = logging.getLogger(__name__)
class OpenRouterModelsAPI:
    """
    Client class for fetching AI models from OpenRouter API and saving them to database.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter API client.
        
        Args:
            api_key: Optional OpenRouter API key. If not provided, will look for OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = requests.Session()
        
        # Set default headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenRouter-Models-Fetcher/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        self.session.headers.update(headers)

    def fetch_models(self) -> List[Dict[str, Any]]:
        """
        Fetch all available models from OpenRouter API.
        
        Returns:
            List of model dictionaries
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            logger.info("Fetching models from OpenRouter API...")
            
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            
            data = response.json()
            models = data.get('data', [])
            
            logger.info(f"Successfully fetched {len(models)} models from OpenRouter")
            return models
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch models from OpenRouter: {e}")
            raise

    def parse_model_data(self, raw_model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw model data from OpenRouter API into our database schema format.
        
        Args:
            raw_model: Raw model data from OpenRouter API
            
        Returns:
            Parsed model data ready for database insertion
        """
        # Extract pricing information
        pricing = raw_model.get('pricing', {})
        prompt_price = float(pricing.get('prompt', 0)) if pricing.get('prompt') else None
        completion_price = float(pricing.get('completion', 0)) if pricing.get('completion') else None
        
        # Determine if model is free
        is_free = (prompt_price == 0.0 and completion_price == 0.0) or prompt_price is None
        
        # Extract capabilities
        architecture = raw_model.get('architecture', {})
        capabilities = {
            'modality': architecture.get('modality', ''),
            'input_modalities': architecture.get('input_modalities', []),
            'output_modalities': architecture.get('output_modalities', []),
            'tokenizer': architecture.get('tokenizer', ''),
            'instruct_type': architecture.get('instruct_type')
        }
        
        # Extract provider from model ID (e.g., "openai/gpt-4" -> "openai")
        model_id = raw_model.get('id', '')
        provider = model_id.split('/')[0] if '/' in model_id else None
        
        # Calculate a simple quality score based on context length and pricing
        context_length = raw_model.get('context_length', 0)
        quality_score = None
        if context_length > 0:
            # Higher context length = higher score, lower price = higher score
            base_score = min(context_length / 100000, 10)  # Normalize context length
            if prompt_price and prompt_price > 0:
                price_penalty = min(prompt_price * 1000, 5)  # Penalty for higher prices
                quality_score = max(0, base_score - price_penalty)
            else:
                quality_score = base_score
        
        # Determine if model should be recommended (free models or high quality)
        is_recommended = is_free or (quality_score and quality_score > 7)
        
        # Create tags based on model characteristics
        tags = []
        if is_free:
            tags.append('free')
        if 'gpt' in model_id.lower():
            tags.append('openai')
        if 'claude' in model_id.lower():
            tags.append('anthropic')
        if 'llama' in model_id.lower():
            tags.append('meta')
        if 'gemini' in model_id.lower():
            tags.append('google')
        if architecture.get('modality', '').count('->') > 0:
            tags.append('multimodal')
        if context_length > 100000:
            tags.append('long-context')
        
        return {
            'provider': provider,
            'model_name': model_id,
            'display_name': raw_model.get('name', model_id),
            'is_free': is_free,
            'quality_score': quality_score,
            'context_length': raw_model.get('context_length'),
            'pricing_prompt': prompt_price,
            'pricing_completion': completion_price,
            'capabilities': json.dumps(capabilities),
            'tags': json.dumps(tags),
            'is_recommended': is_recommended,
            'last_checked': datetime.utcnow(),
            'raw_metadata': json.dumps(raw_model),
            'active': True
        }

    def save_models_to_db(self, models_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Save models data to the database.
        
        Args:
            models_data: List of parsed model data dictionaries
            
        Returns:
            Dictionary with counts of created, updated, and skipped records
        """
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with Session(engine) as session:
            for model_data in models_data:
                try:
                    model_name = model_data['model_name']
                    
                    # Check if model already exists
                    statement = select(AIModel).where(AIModel.model_name == model_name)
                    existing_model = session.exec(statement).first()
                    
                    if existing_model:
                        # Update existing model
                        for key, value in model_data.items():
                            if hasattr(existing_model, key):
                                setattr(existing_model, key, value)
                        
                        session.add(existing_model)
                        stats['updated'] += 1
                        logger.debug(f"Updated model: {model_name}")
                    else:
                        # Create new model
                        new_model = AIModel(**model_data)
                        session.add(new_model)
                        stats['created'] += 1
                        logger.debug(f"Created model: {model_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing model {model_data.get('model_name', 'unknown')}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Commit all changes
            try:
                session.commit()
                logger.info(f"Database update complete: {stats}")
            except Exception as e:
                logger.error(f"Failed to commit changes to database: {e}")
                session.rollback()
                raise
        
        return stats

    def mark_inactive_models(self, active_model_names: List[str]) -> int:
        """
        Mark models as inactive if they're no longer available in OpenRouter.
        
        Args:
            active_model_names: List of model names that are currently active
            
        Returns:
            Number of models marked as inactive
        """
        with Session(engine) as session:
            # Find models that are currently active but not in the active list
            statement = select(AIModel).where(
                AIModel.active == True,
                AIModel.model_name.notin_(active_model_names)
            )
            inactive_models = session.exec(statement).all()
            
            count = 0
            for model in inactive_models:
                model.active = False
                model.last_checked = datetime.utcnow()
                session.add(model)
                count += 1
                logger.debug(f"Marked model as inactive: {model.model_name}")
            
            session.commit()
            logger.info(f"Marked {count} models as inactive")
            return count

    def sync_models(self) -> Dict[str, int]:
        """
        Complete synchronization of models from OpenRouter API to database.
        
        Returns:
            Dictionary with sync statistics
        """
        logger.info("Starting OpenRouter models synchronization...")
        
        try:
            # Fetch models from API
            raw_models = self.fetch_models()
            
            if not raw_models:
                logger.warning("No models received from OpenRouter API")
                return {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'deactivated': 0}
            
            # Parse model data
            parsed_models = []
            active_model_names = []
            
            for raw_model in raw_models:
                try:
                    parsed_model = self.parse_model_data(raw_model)
                    parsed_models.append(parsed_model)
                    active_model_names.append(parsed_model['model_name'])
                except Exception as e:
                    logger.error(f"Failed to parse model {raw_model.get('id', 'unknown')}: {e}")
                    continue
            
            # Save to database
            sync_stats = self.save_models_to_db(parsed_models)
            
            # Mark inactive models
            deactivated_count = self.mark_inactive_models(active_model_names)
            sync_stats['deactivated'] = deactivated_count
            
            logger.info(f"Synchronization complete: {sync_stats}")
            return sync_stats
            
        except Exception as e:
            logger.error(f"Failed to synchronize models: {e}")
            raise

    def get_models_summary(self) -> Dict[str, Any]:
        """
        Get a summary of models in the database.
        
        Returns:
            Dictionary with model statistics
        """
        with Session(engine) as session:
            total_models = session.exec(select(AIModel)).all()
            active_models = session.exec(select(AIModel).where(AIModel.active == True)).all()
            free_models = session.exec(select(AIModel).where(AIModel.is_free == True, AIModel.active == True)).all()
            recommended_models = session.exec(select(AIModel).where(AIModel.is_recommended == True, AIModel.active == True)).all()
            
            providers = {}
            for model in active_models:
                provider = model.provider or 'unknown'
                providers[provider] = providers.get(provider, 0) + 1
            
            return {
                'total_models': len(total_models),
                'active_models': len(active_models),
                'free_models': len(free_models),
                'recommended_models': len(recommended_models),
                'providers': providers,
                'last_sync': max([m.last_checked for m in total_models]) if total_models else None
            }


def main():
    """
    Main function for command-line usage.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync OpenRouter models to database')
    parser.add_argument('--api-key', help='OpenRouter API key (or set OPENROUTER_API_KEY env var)')
    parser.add_argument('--summary', action='store_true', help='Show models summary instead of syncing')
    
    args = parser.parse_args()
    
    client = OpenRouterModelsAPI(api_key=args.api_key)
    
    if args.summary:
        summary = client.get_models_summary()
        print("\n=== OpenRouter Models Summary ===")
        print(f"Total models: {summary['total_models']}")
        print(f"Active models: {summary['active_models']}")
        print(f"Free models: {summary['free_models']}")
        print(f"Recommended models: {summary['recommended_models']}")
        print(f"Last sync: {summary['last_sync']}")
        print("\nProviders:")
        for provider, count in sorted(summary['providers'].items()):
            print(f"  {provider}: {count}")
    else:
        stats = client.sync_models()
        print("\n=== Synchronization Results ===")
        print(f"Created: {stats['created']}")
        print(f"Updated: {stats['updated']}")
        print(f"Deactivated: {stats['deactivated']}")
        print(f"Errors: {stats['errors']}")


if __name__ == '__main__':
    main()

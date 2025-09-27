#!/usr/bin/env python3
"""
Test script for OpenRouter Models API
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from cron_job.open_router.open_router_models_api import OpenRouterModelsAPI

def test_basic_functionality():
    """Test basic functionality of the OpenRouter API client."""
    print("Testing OpenRouter Models API...")
    
    try:
        # Initialize client (no API key needed for public models endpoint)
        client = OpenRouterModelsAPI()
        
        # Test fetching models
        print("1. Testing model fetching...")
        models = client.fetch_models()
        print(f"   ✓ Fetched {len(models)} models")
        
        # Test parsing a model
        print("2. Testing model parsing...")
        if models:
            sample_model = models[0]
            parsed = client.parse_model_data(sample_model)
            print(f"   ✓ Parsed model: {parsed['display_name']}")
            print(f"   ✓ Provider: {parsed['provider']}")
            print(f"   ✓ Is free: {parsed['is_free']}")
            print(f"   ✓ Quality score: {parsed['quality_score']}")
        
        # Test database operations (just first few models to avoid overwhelming)
        print("3. Testing database operations...")
        test_models = models[:5]  # Only test with first 5 models
        parsed_test_models = [client.parse_model_data(m) for m in test_models]
        
        stats = client.save_models_to_db(parsed_test_models)
        print(f"   ✓ Database stats: {stats}")
        
        # Test getting summary
        print("4. Testing summary...")
        summary = client.get_models_summary()
        print(f"   ✓ Total models in DB: {summary['total_models']}")
        print(f"   ✓ Active models: {summary['active_models']}")
        print(f"   ✓ Free models: {summary['free_models']}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_sync():
    """Test full synchronization."""
    print("\nTesting full synchronization...")
    
    try:
        client = OpenRouterModelsAPI()
        stats = client.sync_models()
        
        print(f"✅ Full sync completed!")
        print(f"   Created: {stats['created']}")
        print(f"   Updated: {stats['updated']}")
        print(f"   Deactivated: {stats['deactivated']}")
        print(f"   Errors: {stats['errors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_functionality()
    
    if success:
        print("\n" + "="*50)
        user_input = input("Run full sync test? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            test_full_sync()
    
    print("\nTest completed!")
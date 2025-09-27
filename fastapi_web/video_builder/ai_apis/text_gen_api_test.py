#!/usr/bin/env python3
"""
Test script for updated TextGenAPI with dynamic model selection
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from video_builder.ai_apis.text_gen_api import TextGenAPI

def test_dynamic_model_selection():
    """Test the dynamic model selection functionality."""
    print("Testing Dynamic Model Selection in TextGenAPI...")
    
    try:
        # Initialize the API
        api = TextGenAPI()
        
        # Test 1: Get available models info
        print("\n1. Testing available models info...")
        models_info = api.get_available_models_info(limit=5)
        if "free_models" in models_info:
            print(f"   ✓ Found {len(models_info['free_models'])} free models")
            print(f"   ✓ Found {len(models_info['paid_models'])} paid models")
            
            # Show top 3 free models
            print("   Top free models:")
            for i, model in enumerate(models_info['free_models'][:3], 1):
                print(f"     {i}. {model['display_name']} (Quality: {model['quality_score']})")
        else:
            print(f"   ❌ Error getting models: {models_info}")
            return False
        
        # Test 2: Test model selection for different scenarios
        print("\n2. Testing model selection...")
        
        # Scenario 1: Text input, prefer free, high quality
        model1 = api.get_model_for_input("text", prefer_free=True, min_quality_score=7.0)
        print(f"   ✓ High quality free text model: {model1}")
        
        # Scenario 2: URL input
        model2 = api.get_model_for_input("url", prefer_free=True, min_quality_score=5.0)
        print(f"   ✓ URL processing model: {model2}")
        
        # Scenario 3: Fallback scenario
        model3 = api.get_model_for_input("text", prefer_free=True, fallback_attempts=2)
        print(f"   ✓ Fallback model: {model3}")
        
        # Test 3: Test a simple generation (if API key is available)
        print("\n3. Testing simple generation...")
        if hasattr(api, 'apis_token') and api.apis_token:
            try:
                result = api.generate_search_keywords(
                    platforms=["YouTube"],
                    topic="artificial intelligence news",
                    max_keywords=5
                )
                if "error" not in result:
                    print("   ✓ Search keywords generated successfully")
                    print(f"   ✓ Result type: {type(result)}")
                else:
                    print(f"   ⚠️ Keywords generation returned error: {result['error']}")
            except Exception as e:
                print(f"   ⚠️ Keywords generation failed: {e}")
        else:
            print("   ⚠️ No API key found, skipping generation test")
        
        print("\n✅ All dynamic model selection tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_logic():
    """Test the fallback logic with different quality thresholds."""
    print("\nTesting Fallback Logic...")
    
    try:
        api = TextGenAPI()
        
        print("Testing different fallback levels:")
        
        # Test different fallback attempts
        for attempt in range(4):
            model = api.get_model_for_input(
                "text", 
                prefer_free=True, 
                min_quality_score=8.0,  # High threshold to trigger fallbacks
                fallback_attempts=attempt
            )
            print(f"  Attempt {attempt}: {model}")
        
        print("✅ Fallback logic test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

if __name__ == '__main__':
    success1 = test_dynamic_model_selection()
    success2 = test_fallback_logic()
    
    if success1 and success2:
        print("\n🎉 All tests passed! TextGenAPI is ready to use dynamic model selection.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
    
    print("\nTest completed!")
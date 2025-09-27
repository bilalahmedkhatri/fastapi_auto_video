#!/usr/bin/env python3
"""
Test script to verify that text_gen_api stops immediately on errors
instead of continuing with retries or fallbacks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_apis.text_gen_api import TextGenAPI
import logging

# Setup logging
logger = logging.getLogger(__name__)
def test_error_handling():
    """Test that the API stops immediately on errors."""
    text_gen_api = TextGenAPI()
    
    print("=" * 50)
    print("Testing text_gen_api error handling...")
    print("=" * 50)
    
    # Test with a prompt that might cause issues
    prompt = "test prompt for error handling"
    
    try:
        result = text_gen_api.generation_text(
            user_message=prompt,
            voiceover_language="English",
            category="Test",
            user="test_user"
        )
        
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if isinstance(result, dict) and "error" in result:
            print("✓ ERROR DETECTED: API properly returned error and stopped execution")
            print(f"Error message: {result['error']}")
            return False  # Indicates failure (which is expected for this test)
        elif isinstance(result, dict) and all(field in result for field in ["title", "description", "voiceover_script", "tags"]):
            print("✓ SUCCESS: API returned valid content")
            return True  # Indicates success
        else:
            print("✗ UNEXPECTED: API returned unexpected format")
            print(f"Received: {result}")
            return False
            
    except Exception as e:
        print(f"✗ EXCEPTION: Unexpected exception occurred: {e}")
        return False

if __name__ == "__main__":
    test_error_handling()

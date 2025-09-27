#!/usr/bin/env python3

"""
Simple test script to verify if the AI API is working correctly
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_ai_api():
    """Test the OpenRouter API connection"""
    print("Testing AI API connection...")
    
    api_key = os.getenv("QWEN_3_KEY_OPENROUTER")
    if not api_key:
        print("❌ ERROR: QWEN_3_KEY_OPENROUTER not found in environment")
        return False
        
    print(f"✅ API Key found: {api_key[:20]}...")
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        print("🔄 Testing API call...")
        
        response = client.chat.completions.create(
            model="qwen/qwen-2.5-7b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate a short 50-word script about the benefits of renewable energy."}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print(f"✅ API Response successful!")
        print(f"📝 Generated content: {content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_ai_api()
#!/usr/bin/env python3
"""
Test script for social media generation with database integration.
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/script-generator"

def test_script_generation():
    """Test script generation"""
    print("🚀 Testing script generation...")
    
    payload = {
        "user_prompt": "Create a video about renewable energy trends in 2025",
        "script_types": ["short", "medium", "long"],
        "voiceover_language": "English",
        "user_id": "test_user_123"
    }
    
    response = requests.post(f"{BASE_URL}/generate", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Scripts generated successfully!")
        print(f"   Generated {len(result['scripts'])} scripts")
        return True
    else:
        print(f"❌ Script generation failed: {response.status_code}")
        print(response.text)
        return False

def test_social_media_generation():
    """Test social media generation"""
    print("\n📱 Testing social media generation...")
    
    payload = {
        "user_id": "test_user_123",
        "script_index": 0,
        "platforms": ["youtube", "instagram", "tiktok", "twitter"]
    }
    
    response = requests.post(f"{BASE_URL}/generate-social-media", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Social media content generated successfully!")
        print(f"   Generated content for {len(result['platform_descriptions'])} platforms")
        return True
    else:
        print(f"❌ Social media generation failed: {response.status_code}")
        print(response.text)
        return False

def test_database_status():
    """Test database status"""
    print("\n🗃️  Testing database status...")
    
    response = requests.get(f"{BASE_URL}/test-db")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Database status:")
        print(f"   Status: {result['database_status']}")
        print(f"   Scripts in DB: {result['script_generations_count']}")
        print(f"   Social media content in DB: {result['social_media_contents_count']}")
        print(f"   Active sessions: {result['current_sessions']}")
        return True
    else:
        print(f"❌ Database test failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Complete Video Script & Social Media Generation System")
    print("=" * 60)
    
    # Test 1: Script generation
    script_success = test_script_generation()
    
    # Test 2: Social media generation (only if scripts succeeded)
    social_success = False
    if script_success:
        social_success = test_social_media_generation()
    
    # Test 3: Database status
    db_success = test_database_status()
    
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary:")
    print(f"   Script Generation: {'✅ PASS' if script_success else '❌ FAIL'}")
    print(f"   Social Media Generation: {'✅ PASS' if social_success else '❌ FAIL'}")
    print(f"   Database Integration: {'✅ PASS' if db_success else '❌ FAIL'}")
    
    if script_success and social_success and db_success:
        print("\n🎉 All tests passed! The system is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

#!/usr/bin/env python3
"""
Test script for Video Display Backend APIs
Run this to test all the new video display endpoints
"""

import requests
import json
import time
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8000"

# Test data
TEST_USER_ID = "test_user_123"
TEST_VIDEO_DATA = {
    "title": "Test Video for Display Component",
    "description": "Testing the new video display functionality",
    "prompt": "Create a video about electric vehicles",
    "duration": 30,
    "resolution": "1920x1080", 
    "format": "mp4",
    "content_type": "educational",
    "style": "modern",
    "audio_type": "voiceover",
    "text_overlay_style": "clean",
    "transitions": "fade",
    "user_id": TEST_USER_ID,
    "frontend_data": {
        "script_data": {
            "title": "Electric Vehicle Revolution",
            "category": "Technology",
            "content": "Electric vehicles are transforming transportation..."
        },
        "voiceover_data": {
            "voice_model": "Professional Male Voice",
            "duration": 28.5,
            "language": "en-US"
        },
        "media_data": {
            "selected_media": [
                {"type": "video", "source": "Pixabay", "description": "Electric car", "duration": 10},
                {"type": "image", "source": "Pixabay", "description": "Charging station", "duration": 8},
                {"type": "video", "source": "Pixabay", "description": "Tesla driving", "duration": 10}
            ]
        },
        "social_media_data": {
            "hashtags": ["#ElectricVehicles", "#Tesla", "#GreenTech"],
            "keywords": ["electric vehicles", "sustainable transport", "tesla"]
        },
        "video_effects_config": {
            "style": "Modern Tech",
            "transitions": "Smooth Fade",
            "color_scheme": "Electric Blue"
        }
    }
}

def test_create_video():
    """Test creating a new video"""
    print("\n🎬 Testing Video Creation...")
    
    # Convert frontend_data to JSON string for content_data field
    test_data = TEST_VIDEO_DATA.copy()
    test_data["content_data"] = test_data.pop("frontend_data")
    
    response = requests.post(f"{BASE_URL}/api/videos", json=test_data)
    
    if response.status_code == 201:
        video_data = response.json()
        video_id = video_data.get("video_id") or video_data.get("id")
        print(f"✅ Video created successfully! ID: {video_id}")
        return video_id
    else:
        print(f"❌ Failed to create video: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_video_details(video_id):
    """Test getting individual video details"""
    print(f"\n📋 Testing Get Video Details for ID: {video_id}")
    
    response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
    
    if response.status_code == 200:
        video_data = response.json()
        print(f"✅ Video details retrieved successfully!")
        print(f"Title: {video_data.get('title')}")
        print(f"Status: {video_data.get('status')}")
        print(f"Video URL: {video_data.get('video_url')}")
        print(f"Has frontend_data: {'frontend_data' in video_data}")
        return video_data
    else:
        print(f"❌ Failed to get video details: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_video_file(video_id):
    """Test getting video file endpoint"""
    print(f"\n📹 Testing Get Video File for ID: {video_id}")
    
    response = requests.get(f"{BASE_URL}/api/videos/{video_id}/file")
    
    if response.status_code in [200, 302, 404]:
        if response.status_code == 200:
            print(f"✅ Video file served successfully! Size: {len(response.content)} bytes")
        elif response.status_code == 302:
            print(f"✅ Video file redirected to: {response.headers.get('Location')}")
        else:
            print(f"ℹ️ Video file not found (expected for test video): {response.status_code}")
    else:
        print(f"❌ Failed to get video file: {response.status_code}")

def test_regenerate_video(video_id):
    """Test video regeneration"""
    print(f"\n🔄 Testing Video Regeneration for ID: {video_id}")
    
    response = requests.post(f"{BASE_URL}/api/videos/{video_id}/regenerate")
    
    if response.status_code == 200:
        result = response.json()
        new_video_id = result.get("new_video_id")
        print(f"✅ Video regeneration started!")
        print(f"Original ID: {result.get('original_video_id')}")
        print(f"New ID: {new_video_id}")
        return new_video_id
    else:
        print(f"❌ Failed to regenerate video: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_update_video_metadata(video_id):
    """Test updating video metadata"""
    print(f"\n✏️ Testing Update Video Metadata for ID: {video_id}")
    
    update_data = {
        "title": "Updated Test Video Title",
        "description": "This video has been updated via API",
        "target_audience": "Tech enthusiasts"
    }
    
    response = requests.put(f"{BASE_URL}/api/videos/{video_id}", json=update_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Video metadata updated successfully!")
        print(f"Updated fields: {result.get('updated_fields')}")
    else:
        print(f"❌ Failed to update video metadata: {response.status_code}")
        print(f"Response: {response.text}")

def test_get_user_videos(user_id):
    """Test getting user's video collection"""
    print(f"\n👤 Testing Get User Videos for User ID: {user_id}")
    
    response = requests.get(f"{BASE_URL}/api/user/{user_id}/videos")
    
    if response.status_code == 200:
        videos = response.json()
        print(f"✅ User videos retrieved successfully!")
        print(f"Total videos: {len(videos)}")
        for i, video in enumerate(videos[:3], 1):  # Show first 3
            print(f"  {i}. {video.get('title')} ({video.get('status')})")
        return videos
    else:
        print(f"❌ Failed to get user videos: {response.status_code}")
        print(f"Response: {response.text}")
        return []

def test_list_all_videos():
    """Test listing all videos"""
    print(f"\n📝 Testing List All Videos")
    
    response = requests.get(f"{BASE_URL}/api/videos?limit=5")
    
    if response.status_code == 200:
        videos = response.json()
        print(f"✅ Videos list retrieved successfully!")
        print(f"Total videos shown: {len(videos)}")
        return videos
    else:
        print(f"❌ Failed to list videos: {response.status_code}")
        return []

def test_health_check():
    """Test backend health"""
    print(f"\n🏥 Testing Backend Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"Status: {health_data.get('status')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print(f"Make sure FastAPI is running on {BASE_URL}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Video Display Backend API Tests")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    # Check if backend is running
    if not test_health_check():
        print("\n❌ Backend is not running. Please start FastAPI first:")
        print("cd fastapi_web && fastapi dev main.py")
        return
    
    # Test video creation
    video_id = test_create_video()
    if not video_id:
        print("\n❌ Cannot proceed without creating a video")
        return
    
    # Wait a moment for video to be processed
    print("\n⏳ Waiting 2 seconds for video processing...")
    time.sleep(2)
    
    # Test all other endpoints
    test_get_video_details(video_id)
    test_get_video_file(video_id)
    test_update_video_metadata(video_id)
    
    # Test regeneration
    new_video_id = test_regenerate_video(video_id)
    
    # Test user video collection
    test_get_user_videos(TEST_USER_ID)
    
    # Test listing all videos
    test_list_all_videos()
    
    print(f"\n🎉 All tests completed!")
    print(f"Original Video ID: {video_id}")
    if new_video_id:
        print(f"Regenerated Video ID: {new_video_id}")
    
    # Frontend integration info
    print(f"\n🔗 Frontend Integration:")
    print(f"Use this video ID in your frontend: {video_id}")
    print(f"Video details endpoint: {BASE_URL}/api/videos/{video_id}")
    print(f"Video file endpoint: {BASE_URL}/api/videos/{video_id}/file")

if __name__ == "__main__":
    main()
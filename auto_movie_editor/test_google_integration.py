"""Test script for Google Search integration with video builder"""

import sys
import os
from pathlib import Path

# Add the tools directory to Python path
sys.path.append(str(Path(__file__).parent / "tools"))

# Import using the actual filename
from run_app import VideoBuildConfig, download_google_images

def test_google_search_only():
    """Test just the Google image search functionality"""
    config = VideoBuildConfig(
        prompt="electric vehicles future technology",
        use_google_search=True,
        google_search_query="electric car tesla future technology",
        google_search_count=10,
        google_social_media="youtube_thumbnail",
        google_fallback_to_local=False
    )
    
    # Mock AI data
    ai_data = {
        "title": "The Future of Electric Vehicles",
        "description": "Revolutionary advances in EV technology and battery innovation"
    }
    
    print("Testing Google image search...")
    images = download_google_images(config, ai_data)
    
    if images:
        print(f"✅ Successfully downloaded {len(images)} images:")
        for i, img_path in enumerate(images[:5]):  # Show first 5
            print(f"  {i+1}. {img_path}")
        if len(images) > 5:
            print(f"  ... and {len(images) - 5} more images")
    else:
        print("❌ Failed to download images")
        
    return images

def test_video_build_with_google():
    """Test full video build with Google images"""
    print("\n" + "="*50)
    print("Testing full video build with Google images...")
    print("="*50)
    
    from run_app import build_video
    
    config = VideoBuildConfig(
        prompt="latest electric vehicle innovations 2025",
        category="Technology",
        voice="am_puck",
        target_format="youtube_short",
        image_dir="media/bikes_test",  # Fallback directory
        faces_dir="media/faces",
        upload_to_youtube=False,  # Don't upload during test
        # Google Search Configuration
        use_google_search=True,
        google_search_query="electric vehicle innovation technology 2025",
        google_search_count=8,
        google_social_media="youtube_thumbnail",
        google_fallback_to_local=True
    )
    
    try:
        result = build_video(config)
        print("✅ Video build successful!")
        print(f"Output path: {result.get('output_path')}")
        print(f"YouTube ID: {result.get('youtube_video_id')}")
        return result
    except Exception as e:
        print(f"❌ Video build failed: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing Google Search Image Integration")
    print("=" * 50)
    
    # Test 1: Google image search only
    images = test_google_search_only()
    
    # Test 2: Full video build (only if image search worked)
    if images:
        user_input = input("\nDo you want to test full video build? (y/n): ").lower().strip()
        if user_input == 'y':
            test_video_build_with_google()
    else:
        print("\n⚠️  Skipping video build test due to image search failure")
        print("Please check:")
        print("1. Environment variables are set correctly")
        print("2. Google Custom Search API is enabled")
        print("3. Internet connection is working")

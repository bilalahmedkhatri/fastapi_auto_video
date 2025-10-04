"""
Test script for media search API integration
Tests both backend API endpoints and Pexels integration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from video_builder.apis.pexel import PexelsAPI, normalize_pexels_photo, normalize_pexels_video


def test_pexels_api():
    """Test Pexels API integration"""
    print("=" * 60)
    print("Testing Pexels API Integration")
    print("=" * 60)
    
    api = PexelsAPI()
    
    if not api.api_key:
        print("❌ PEXELS_API_KEY not found in environment")
        print("   Please add it to your .env file")
        print("   Get your key at: https://www.pexels.com/api/")
        return False
    
    print("✅ Pexels API key configured")
    
    # Test photo search
    print("\n📸 Testing photo search...")
    try:
        photos_result = api.search_photos("technology", per_page=3)
        
        if "error" in photos_result:
            print(f"❌ Photo search error: {photos_result['error']}")
            return False
        
        photos = photos_result.get("photos", [])
        print(f"✅ Found {len(photos)} photos")
        
        if photos:
            sample = normalize_pexels_photo(photos[0])
            print(f"   Sample: {sample['id']}")
            print(f"   Photographer: {sample['photographer']}")
            print(f"   URL: {sample['url'][:50]}...")
            
    except Exception as e:
        print(f"❌ Photo search failed: {e}")
        return False
    
    # Test video search
    print("\n🎥 Testing video search...")
    try:
        videos_result = api.search_videos("nature", per_page=3)
        
        if "error" in videos_result:
            print(f"❌ Video search error: {videos_result['error']}")
            return False
        
        videos = videos_result.get("videos", [])
        print(f"✅ Found {len(videos)} videos")
        
        if videos:
            sample = normalize_pexels_video(videos[0])
            print(f"   Sample: {sample['id']}")
            print(f"   User: {sample['user']}")
            print(f"   Duration: {sample['duration']}s")
            print(f"   Quality: {sample['quality']}")
            
    except Exception as e:
        print(f"❌ Video search failed: {e}")
        return False
    
    print("\n✅ Pexels API tests passed!")
    return True


def test_google_api():
    """Test Google Custom Search API"""
    print("\n" + "=" * 60)
    print("Testing Google Custom Search API")
    print("=" * 60)
    
    api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    cse_id = os.getenv("GOOGLE_SEARCH_ENGINE")
    
    if not api_key or not cse_id:
        print("❌ Google API credentials not found")
        print("   Required environment variables:")
        print("   - GOOGLE_CUSTOM_SEARCH_API_KEY")
        print("   - GOOGLE_SEARCH_ENGINE")
        print("   Get your keys at: https://developers.google.com/custom-search")
        return False
    
    print("✅ Google API credentials configured")
    
    try:
        from video_builder.apis.google_search_api import google_image_search
        
        print("\n🔍 Testing image search...")
        image_urls = google_image_search(
            api_key=api_key,
            cse_id=cse_id,
            search_ai_query="sunset ocean",
            num_results=5
        )
        
        print(f"✅ Found {len(image_urls)} image URLs")
        
        if image_urls:
            print(f"   Sample: {image_urls[0][:60]}...")
            
    except Exception as e:
        print(f"❌ Google search failed: {e}")
        return False
    
    print("\n✅ Google API tests passed!")
    return True


def test_search_endpoint_simulation():
    """Simulate the combined search endpoint logic"""
    print("\n" + "=" * 60)
    print("Simulating Combined Search Endpoint")
    print("=" * 60)
    
    query = "technology innovation"
    platforms = ["pexels", "google"]
    
    print(f"Query: {query}")
    print(f"Platforms: {platforms}")
    
    all_results = []
    errors = {}
    
    # Test Pexels
    if "pexels" in platforms:
        print("\n📦 Searching Pexels...")
        api = PexelsAPI()
        
        if api.api_key:
            # Search photos
            photos_response = api.search_photos(query, per_page=5)
            if "error" in photos_response:
                errors["pexels_photos"] = photos_response["error"]
            else:
                photos = photos_response.get("photos", [])
                all_results.extend([normalize_pexels_photo(p) for p in photos])
                print(f"   ✅ Added {len(photos)} photos")
            
            # Search videos
            videos_response = api.search_videos(query, per_page=5)
            if "error" in videos_response:
                errors["pexels_videos"] = videos_response["error"]
            else:
                videos = videos_response.get("videos", [])
                all_results.extend([normalize_pexels_video(v) for v in videos])
                print(f"   ✅ Added {len(videos)} videos")
        else:
            errors["pexels"] = "API key not configured"
            print("   ⚠️  API key not configured")
    
    # Test Google
    if "google" in platforms:
        print("\n🔍 Searching Google...")
        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        cse_id = os.getenv("GOOGLE_SEARCH_ENGINE")
        
        if api_key and cse_id:
            try:
                from video_builder.apis.google_search_api import google_image_search
                image_urls = google_image_search(api_key, cse_id, query, num_results=5)
                all_results.extend([
                    {
                        "id": f"google-{hash(url)}",
                        "type": "image",
                        "source": "google",
                        "url": url
                    }
                    for url in image_urls
                ])
                print(f"   ✅ Added {len(image_urls)} images")
            except Exception as e:
                errors["google"] = str(e)
                print(f"   ❌ Error: {e}")
        else:
            errors["google"] = "API credentials not configured"
            print("   ⚠️  API credentials not configured")
    
    print("\n" + "=" * 60)
    print(f"📊 Total Results: {len(all_results)}")
    print(f"   Images: {sum(1 for r in all_results if r['type'] == 'image')}")
    print(f"   Videos: {sum(1 for r in all_results if r['type'] == 'video')}")
    
    if errors:
        print(f"\n⚠️  Errors encountered:")
        for platform, error in errors.items():
            print(f"   - {platform}: {error}")
    
    if all_results:
        print("\n✅ Combined search simulation successful!")
        print("\nSample results:")
        for result in all_results[:3]:
            print(f"   - [{result['source']}] {result['type']}: {result.get('name', result['id'])}")
        return True
    else:
        print("\n❌ No results found - check API configurations")
        return False


def main():
    """Run all tests"""
    print("\n" + "🔬 MEDIA SEARCH API INTEGRATION TESTS" + "\n")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    results = []
    
    # Run tests
    results.append(("Pexels API", test_pexels_api()))
    results.append(("Google API", test_google_api()))
    results.append(("Combined Search", test_search_endpoint_simulation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Media search API is ready to use.")
        print("\nNext steps:")
        print("1. Start your FastAPI server: cd fastapi_web && uvicorn main:app --reload")
        print("2. Start your Next.js frontend: cd ui_auto_movie && npm run dev")
        print("3. Test the search in MediaManager component")
    else:
        print("\n⚠️  Some tests failed. Please check:")
        print("1. API keys are set in .env file")
        print("2. .env file is in the fastapi_web directory")
        print("3. API credentials are valid")
        print("\nSee MEDIA_SEARCH_API_SETUP.md for detailed setup instructions")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

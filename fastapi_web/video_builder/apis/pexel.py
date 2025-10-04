"""
Pexels API integration for fetching stock photos and videos.
Free API - 200 requests per hour, attribution required.
API Docs: https://www.pexels.com/api/documentation/
"""

import os
import requests
import logging
from typing import List, Dict, Optional, Literal
from pathlib import Path
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PexelsAPI:
    """Pexels API client for searching and downloading photos and videos"""
    
    BASE_URL = "https://api.pexels.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Pexels API client
        
        Args:
            api_key: Pexels API key (defaults to PEXELS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("PEXELS_API_KEY")
        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": self.api_key
        } if self.api_key else {}
    
    def search_photos(
        self,
        query: str,
        per_page: int = 15,
        page: int = 1,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        size: Optional[Literal["large", "medium", "small"]] = None,
        color: Optional[str] = None,
        locale: str = "en-US"
    ) -> Dict:
        """
        Search for photos on Pexels
        
        Args:
            query: Search query
            per_page: Number of results per page (max 80)
            page: Page number
            orientation: Photo orientation filter
            size: Minimum photo size
            color: Desired photo color (red, orange, yellow, green, turquoise, blue, violet, pink, brown, black, gray, white)
            locale: Locale for search
            
        Returns:
            API response with photos
        """
        if not self.api_key:
            logger.error("Cannot search photos: PEXELS_API_KEY not configured")
            return {"photos": [], "total_results": 0, "error": "API key not configured"}
        
        endpoint = f"{self.BASE_URL}/v1/search"
        
        params = {
            "query": query,
            "per_page": min(per_page, 80),  # Max 80 per Pexels API limit
            "page": page,
            "locale": locale
        }
        
        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size
        if color:
            params["color"] = color
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels photo search failed: {e}")
            return {"photos": [], "total_results": 0, "error": str(e)}
    
    def search_videos(
        self,
        query: str,
        per_page: int = 15,
        page: int = 1,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        size: Optional[Literal["large", "medium", "small"]] = None,
        locale: str = "en-US"
    ) -> Dict:
        """
        Search for videos on Pexels
        
        Args:
            query: Search query
            per_page: Number of results per page (max 80)
            page: Page number
            orientation: Video orientation filter
            size: Minimum video size
            locale: Locale for search
            
        Returns:
            API response with videos
        """
        if not self.api_key:
            logger.error("Cannot search videos: PEXELS_API_KEY not configured")
            return {"videos": [], "total_results": 0, "error": "API key not configured"}
        
        endpoint = f"{self.BASE_URL}/videos/search"
        
        params = {
            "query": query,
            "per_page": min(per_page, 80),
            "page": page,
            "locale": locale
        }
        
        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels video search failed: {e}")
            return {"videos": [], "total_results": 0, "error": str(e)}
    
    def get_photo_by_id(self, photo_id: int) -> Dict:
        """Get a specific photo by ID"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        endpoint = f"{self.BASE_URL}/v1/photos/{photo_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get photo {photo_id}: {e}")
            return {"error": str(e)}
    
    def get_video_by_id(self, video_id: int) -> Dict:
        """Get a specific video by ID"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        endpoint = f"{self.BASE_URL}/videos/videos/{video_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get video {video_id}: {e}")
            return {"error": str(e)}
    
    def download_file(self, url: str, output_path: Path) -> bool:
        """
        Download a photo or video file
        
        Args:
            url: Direct URL to the media file
            output_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Downloaded file to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file from {url}: {e}")
            return False


def normalize_pexels_photo(photo: Dict) -> Dict:
    """
    Normalize Pexels photo response to standardized format
    
    Args:
        photo: Raw photo data from Pexels API
        
    Returns:
        Normalized photo object
    """
    return {
        "id": f"pexels-photo-{photo.get('id')}",
        "type": "image",
        "source": "pexels",
        "url": photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large"),
        "thumbnail": photo.get("src", {}).get("medium"),
        "preview": photo.get("src", {}).get("small"),
        "width": photo.get("width"),
        "height": photo.get("height"),
        "photographer": photo.get("photographer"),
        "photographer_url": photo.get("photographer_url"),
        "alt": photo.get("alt", ""),
        "avg_color": photo.get("avg_color"),
        "license": "Pexels License - Free for commercial use (attribution appreciated)",
        "license_url": "https://www.pexels.com/license/"
    }


def normalize_pexels_video(video: Dict) -> Dict:
    """
    Normalize Pexels video response to standardized format
    
    Args:
        video: Raw video data from Pexels API
        
    Returns:
        Normalized video object
    """
    # Get the best quality video file
    video_files = video.get("video_files", [])
    hd_video = None
    sd_video = None
    
    for vf in video_files:
        quality = vf.get("quality", "").lower()
        if "hd" in quality and not hd_video:
            hd_video = vf
        elif "sd" in quality and not sd_video:
            sd_video = vf
    
    best_video = hd_video or sd_video or (video_files[0] if video_files else {})
    
    return {
        "id": f"pexels-video-{video.get('id')}",
        "type": "video",
        "source": "pexels",
        "url": best_video.get("link", ""),
        "thumbnail": video.get("image"),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration": video.get("duration"),
        "user": video.get("user", {}).get("name"),
        "user_url": video.get("user", {}).get("url"),
        "quality": best_video.get("quality"),
        "file_type": best_video.get("file_type"),
        "license": "Pexels License - Free for commercial use (attribution appreciated)",
        "license_url": "https://www.pexels.com/license/",
        "video_files": video_files  # Include all quality options
    }


# Example usage
if __name__ == "__main__":
    # Test the Pexels API
    api = PexelsAPI()
    
    # Search for photos
    print("Searching for photos...")
    photos_result = api.search_photos("nature", per_page=5)
    
    if "photos" in photos_result and photos_result["photos"]:
        print(f"Found {photos_result['total_results']} photos")
        for photo in photos_result["photos"][:3]:
            normalized = normalize_pexels_photo(photo)
            print(f"  - {normalized['id']}: {normalized['url']}")
    
    # Search for videos
    print("\nSearching for videos...")
    videos_result = api.search_videos("ocean", per_page=5)
    
    if "videos" in videos_result and videos_result["videos"]:
        print(f"Found {videos_result['total_results']} videos")
        for video in videos_result["videos"][:3]:
            normalized = normalize_pexels_video(video)
            print(f"  - {normalized['id']}: {normalized['url']} ({normalized['duration']}s)")

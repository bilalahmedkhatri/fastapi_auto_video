import asyncio
import aiohttp
import os
import logging
import uuid
import hashlib
from pathlib import Path
from typing import List, Optional, Dict
from dotenv import load_dotenv
from PIL import Image
from tomlkit import value
from .text_gen_api import TextGenAPI
from pprint import pprint
import threading

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# Use module-specific logger instead of global configuration
logger = logging.getLogger(__name__)

# Add platform-specific sizes
PLATFORM_SIZES = {
    "youtube_video": (1080, 1920),
    "youtube_short": (1920, 1080),
    "instagram_reel": (1080, 1920),
    "instagram_feed": (1080, 1080),
    "facebook_reel": (1080, 1920),
    "tiktok": (1080, 1920),
    "twitter_post": (1200, 675),
    "linkedin_post": (1200, 627),
    "pinterest_pin": (1000, 1500),
    "snapchat_story": (1080, 1920),
    "whatsapp_status": (1080, 1920),
    # Add more as needed
}

class PixabayAPIError(Exception):
    pass

def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

USER_HASHES_DIR = Path("user_hashes")
USER_HASHES_DIR.mkdir(exist_ok=True)
_user_hashes_lock = threading.Lock()

def _get_user_hash_file(user_id: str, media_type: str) -> Path:
    return USER_HASHES_DIR / f"{user_id}_{media_type}_hashes.txt"

def user_has_file(user_id: str, file_hash: str, media_type: str) -> bool:
    """Check if user already has a file with this hash (file-based)."""
    hash_file = _get_user_hash_file(user_id, media_type)
    if not hash_file.exists():
        return False
    with _user_hashes_lock:
        with open(hash_file, "r") as f:
            for line in f:
                if line.strip() == file_hash:
                    return True
    return False

def add_user_file(user_id: str, file_hash: str, media_type: str) -> None:
    """Record that user has downloaded a file with this hash (file-based)."""
    hash_file = _get_user_hash_file(user_id, media_type)
    with _user_hashes_lock:
        with open(hash_file, "a") as f:
            f.write(f"{file_hash}\n")

class PixabayImageDownloader:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PIXABAY_API_KEY
        self.url = "https://pixabay.com/api/"
        self.video_url = "https://pixabay.com/api/videos/"

    async def search_images(
        self,
        query: str,
        params: Optional[Dict] = None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> List[str]:
        """Search Pixabay for images and return a list of image URLs."""
        if not self.api_key:
            raise PixabayAPIError("Pixabay API key is missing.")
        base_params = {
            "key": self.api_key,
            "q": query,
            "per_page": params.get("per_page", 20) if params else 20,
            "page": params.get("page", 1) if params else 1,
            "image_type": params.get("image_type", "photo") if params else "photo",
            "orientation": params.get("orientation", "horizontal") if params else "horizontal",
            "order": params.get("order", "latest") if params else "latest",
            "safesearch": params.get("safesearch", "true") if params else "true",
            "lang": params.get("lang", "en") if params else "en",
            "min_width": params.get("min_width") if params and "min_width" in params else None,
            "min_height": params.get("min_height") if params and "min_height" in params else None,
            "category": params.get("category") if params and "category" in params else None,
            "pretty": params.get("pretty") if params and "pretty" in params else None
        }
        # Remove None values
        base_params = {k: v for k, v in base_params.items() if v is not None}
        sess = session or aiohttp.ClientSession()
        try:
            async with sess.get(self.url, params=base_params) as response:
                print(f"Pixabay API response status: {response.status}")
                if response.status == 429:
                    raise PixabayAPIError("Pixabay API rate limit exceeded.")
                response.raise_for_status()
                data = await response.json()
                return [item["webformatURL"] for item in data.get("hits", [])]
        except Exception as e:
            logger.warning(f"Pixabay API request failed: {str(e)}")
            return []
        finally:
            if session is None:
                await sess.close()

    async def search_videos(
        self,
        query: str,
        params: Optional[Dict] = None,
        session: Optional[aiohttp.ClientSession] = None
    ) -> List[str]:
        """Search Pixabay for videos and return a list of best available video URLs (large, else medium)."""
        if not self.api_key:
            raise PixabayAPIError("Pixabay API key is missing.")
        if not query or not query.strip():
            logger.warning("Pixabay Video API: Query parameter 'q' is empty.")
            return []
        base_params = {
            "key": self.api_key,
            "q": query,
            "per_page": params.get("per_page", 20) if params else 20,
            "page": params.get("page", 1) if params else 1,
            "safesearch": params.get("safesearch", "true") if params else "true",
            "lang": params.get("lang", "en") if params else "en",
            "min_width": params.get("min_width") if params and "min_width" in params else None,
            "min_height": params.get("min_height") if params and "min_height" in params else None,
            "category": params.get("category") if params and "category" in params else None,
            "pretty": params.get("pretty") if params and "pretty" in params else None
        }
        # Remove None values
        base_params = {k: v for k, v in base_params.items() if v is not None}
        if params and "video_type" in params and params["video_type"] != "all":
            base_params["video_type"] = params["video_type"]
        sess = session or aiohttp.ClientSession()
        try:
            async with sess.get(self.video_url, params=base_params) as response:
                if response.status == 429:
                    raise PixabayAPIError("Pixabay API rate limit exceeded.")
                if response.status != 200:
                    error_text = await response.text()
                    logger.warning(f"Pixabay Video API error {response.status}: {error_text}")
                    return []
                data = await response.json()
                result_urls = []
                for v in data.get("hits", []):
                    large_url = v.get("videos", {}).get("large", {}).get("url")
                    medium_url = v.get("videos", {}).get("medium", {}).get("url")
                    if large_url:
                        result_urls.append(large_url)
                    elif medium_url:
                        result_urls.append(medium_url)
                return result_urls
        except Exception as e:
            logger.warning(f"Pixabay Video API request failed: {str(e)}")
            return []
        finally:
            if session is None:
                await sess.close()

    async def download_images(
        self,
        urls: List[str],
        download_folder: Path = Path("pixabay_images"),
        max_concurrent_downloads: int = 5,
        user_id: Optional[str] = None
    ) -> None:
        """Download images and optionally resize for platforms. Avoid duplicates per user."""
        download_folder.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(max_concurrent_downloads)
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._download_image(
                    session, url, download_folder, semaphore, user_id
                )
                for url in urls
            ]
            await asyncio.gather(*tasks)

    async def download_videos(
        self,
        urls: List[str],
        download_folder: Path = Path("pixabay_videos"),
        max_concurrent_downloads: int = 5,
        user_id: Optional[str] = None
    ) -> None:
        """Download videos from the given URLs to the specified folder. Avoid duplicates per user."""
        download_folder.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(max_concurrent_downloads)
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._download_video(session, url, download_folder, semaphore, user_id)
                for url in urls
            ]
            await asyncio.gather(*tasks)

    async def _download_image(
        self,
        session: aiohttp.ClientSession,
        url: str,
        download_folder: Path,
        semaphore: asyncio.Semaphore,
        user_id: Optional[str] = None
    ) -> None:
        async with semaphore:
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    file_hash = sha256_bytes(content)
                    if user_id and user_has_file(user_id, file_hash, "image"):
                        logger.info(f"User {user_id} already has image: {url}")
                        return
                    file_name = download_folder / f"{uuid.uuid4().hex}.jpg"
                    file_name.write_bytes(content)
                    logger.info(f"Downloaded: {file_name}")
                    if user_id:
                        add_user_file(user_id, file_hash, "image")
            except Exception as e:
                logger.warning(f"Error downloading {url}: {str(e)}")

    async def _download_video(
        self,
        session: aiohttp.ClientSession,
        url: str,
        download_folder: Path,
        semaphore: asyncio.Semaphore,
        user_id: Optional[str] = None,
        max_retries: int = 3
    ) -> None:
        async with semaphore:
            attempt = 0
            while attempt < max_retries:
                try:
                    async with session.get(url) as response:
                        if response.status == 429:
                            wait_time = 2 ** attempt
                            logger.warning(f"429 Too Many Requests for {url}, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            attempt += 1
                            continue
                        response.raise_for_status()
                        content = await response.read()
                        file_hash = sha256_bytes(content)
                        if user_id and user_has_file(user_id, file_hash, "video"):
                            logger.info(f"User {user_id} already has video: {url}")
                            return
                        file_name = download_folder / f"{uuid.uuid4().hex}.mp4"
                        file_name.write_bytes(content)
                        logger.info(f"Downloaded video: {file_name}")
                        if user_id:
                            add_user_file(user_id, file_hash, "video")
                        return
                except Exception as e:
                    logger.warning(f"Error downloading video {url}: {str(e)}")
                    attempt += 1
                    await asyncio.sleep(2 ** attempt)
            logger.error(f"Failed to download video after {max_retries} attempts: {url}")

def get_platform_category(data: dict) -> list:
    """Extract categories from platforms dictionary."""
    categories = []
    
    # Extract categories from nested platforms
    platforms = data.get("platforms", {})
    if isinstance(platforms, dict):
        for platform_name, platform_info in platforms.items():
            if isinstance(platform_info, dict) and "categories" in platform_info:
                # Prioritize Pixabay categories since we're using Pixabay API
                if platform_name == "Pixabay" and isinstance(platform_info["categories"], list):
                    return platform_info["categories"][:3]  # Return top 3 Pixabay categories
                
                # Add categories from other platforms
                if isinstance(platform_info["categories"], list):
                    categories.extend(platform_info["categories"])
    
    # Deduplicate categories
    return list(dict.fromkeys(categories))[:5]  # Return top 5 unique categories

def get_keywords(data: dict) -> list:
    """Extract keywords and all categories from a nested dict."""
    keywords = []

    # Extract top-level keywords
    if "keywords" in data and isinstance(data["keywords"], list):
        keywords.extend(data["keywords"])

    # Extract categories from nested platforms
    platforms = data.get("platforms", {})
    if isinstance(platforms, dict):
        for platform_info in platforms.values():
            if isinstance(platform_info, dict):
                categories = platform_info.get("categories", [])
                if isinstance(categories, list):
                    keywords.extend(categories)

    # print(f"Extracted keywords: {type(keywords)}, {keywords}")
    # print(f"Extracted categories: {type(platforms)}, {platforms}")
    return keywords

# Example usage
# if __name__ == "__main__":
async def get_images_videos(title):
    """
    Generate keywords from title, then search and download images/videos for each keyword.
    Downloads are organized in folders named after the search terms.
    """
    print('checking title for image search', type(title), title)
    user_id = "user_1"
    downloader = PixabayImageDownloader()
    
    # Generate search keywords based on the title
    search_query = TextGenAPI().generate_search_keywords(
        platforms=["Google", "Pixabay", "Unsplash"],
        topic=title,
        max_keywords=8,
    )
    
    if "error" in search_query:
        logger.error(f"Error generating keywords: {search_query['error']}")
        return

    # Extract keywords and categories
    keywords = get_keywords(search_query)
    categories = get_platform_category(search_query)
    
    if not keywords:
        logger.warning("No keywords extracted from search query")
        keywords = [title]  # Use title as fallback

    # Process each keyword individually for better results
    for idx, keyword in enumerate(keywords[:3]):  # Limit to top 3 keywords
        logger.info(f"Processing keyword {idx+1}/{len(keywords[:3])}: {keyword}")
        
        # Create safe folder name
        safe_keyword = "".join(c if c.isalnum() else "_" for c in keyword)
        download_folder = Path(f"media/{safe_keyword}")
        
        # Search and download images
        image_params = {
            "per_page": 5,
            "page": 1,
            "image_type": "photo",
            "orientation": "horizontal",  # For YouTube shorts
            "order": "popular",
            "safesearch": "true",
            "lang": "en",
            "min_width": PLATFORM_SIZES["youtube_short"][0],
            "min_height": PLATFORM_SIZES["youtube_short"][1],
            "category": ",".join(categories[:3]) if categories else None,
            "pretty": "true"
        }
        
        try:
            urls = await downloader.search_images(
                query=keyword,
                params=image_params
            )
            
            if urls:
                await downloader.download_images(
                    urls,
                    download_folder=download_folder / "images",
                    user_id=user_id
                )
                logger.info(f"Downloaded {len(urls)} images for '{keyword}'")
            else:
                logger.warning(f"No images found for keyword: {keyword}")
                
            # Search and download videos
            video_params = {
                "per_page": 3,
                "page": 1,
                "safesearch": "true",
                "lang": "en",
                "min_width": PLATFORM_SIZES["youtube_short"][0],
                "min_height": PLATFORM_SIZES["youtube_short"][1],
                "category": ",".join(categories[:3]) if categories else None,
                "pretty": "true"
            }
            
            video_urls = await downloader.search_videos(
                query=keyword,
                params=video_params
            )
            
            if video_urls:
                await downloader.download_videos(
                    video_urls,
                    download_folder=download_folder / "videos",
                    user_id=user_id
                )
                logger.info(f"Downloaded {len(video_urls)} videos for '{keyword}'")
            else:
                logger.warning(f"No videos found for keyword: {keyword}")
                
        except Exception as e:
            logger.error(f"Error processing keyword '{keyword}': {str(e)}")
    
        logger.info(f"Media download complete for '{title}'")
        return download_folder.parent  # Return the parent directory containing all keyword folders
    
data = """

```json
{
  "keywords": [
    "Elon Musk Grok 1.5",
    "Grok 1.5 AI update",
    "Elon Musk AI news",
    "Grok 1.5 features",
    "Tech world Grok AI",
    "Musk AI announcement",
    "Grok 1.5 release details",
    "AI chatbot Grok update"
  ],
  "platforms": {
    "Google": {
      "categories": ["Technology News", "Artificial Intelligence", "Business Innovations", "Science & Tech"]
    },
    "Pixabay": {
      "categories": ["Technology", "Robotics", "Abstract", "Science"]
    },
    "Unsplash": {
      "categories": ["Technology", "Artificial Intelligence", "Futuristic", "Innovation"]
    }
  }
}
```
"""
# asyncio.run(get_images_videos(data))  

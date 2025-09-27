import asyncio
import aiohttp
import os
from urllib.parse import urlparse
from typing import Dict, List

async def search_searxng(
    query: str,
    categories: str = 'images',
    language: str = 'de-DE'
) -> Dict[int, dict]:
    """Search SearXNG instance and return image results with positions"""
    url = "http://localhost:8888/search"
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
        "safe_search": "moderate",
        "language": language,
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                results = await response.json()
                return {
                    result['positions'][0]: {
                        'title': result.get('title', ''),
                        'website_url': result.get('url', ''),
                        'img_src': result.get('img_src', ''),
                        'resolution': result.get('resolution', '')
                    }
                    for result in results.get('results', [])
                    if result.get('img_src')
                }
        except (aiohttp.ClientError, ValueError) as e:
            print(f"Search error: {str(e)}")
            return {}

async def download_image(session: aiohttp.ClientSession, url: str, username: str, position: int) -> str:
    """Download and save a single image with async handling"""
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError("Invalid URL format")

        # Create user directory if not exists
        download_dir = os.path.join("download", username)
        os.makedirs(download_dir, exist_ok=True)

        # Generate filename from position and URL
        filename = f"{position}_{os.path.basename(parsed_url.path)}" or f"image_{position}.jpg"
        filepath = os.path.join(download_dir, filename)

        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"HTTP Error {response.status}")
            
            # Verify content type is image
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                raise ValueError(f"Non-image content type: {content_type}")

            # Stream content to file
            with open(filepath, 'wb') as f:
                async for chunk in response.content.iter_chunked(1024 * 16):
                    f.write(chunk)

            return f"Downloaded {url} to {filepath}"

    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")
        return f"Error: {url} - {str(e)}"

async def process_images(results: Dict[int, dict], username: str) -> List[str]:
    """Process all images in parallel"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_image(session, result['img_src'], username, position)
            for position, result in results.items()
            if result.get('img_src')
        ]
        return await asyncio.gather(*tasks)

async def main():
    query = "kawasaki h2r"
    username = "motorcycle_enthusiast"
    
    # Perform search
    search_results = await search_searxng(query)
    
    if not search_results:
        print("No images found")
        return

    # Download images
    print(f"Found {len(search_results)} images, downloading...")
    download_results = await process_images(search_results, username)
    
    # Print results
    print("\nDownload results:")
    for result in download_results:
        print(result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        asyncio.get_event_loop().close()
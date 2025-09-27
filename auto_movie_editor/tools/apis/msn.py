import asyncio
import aiohttp
from typing import Tuple, List, Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_news_async(
    categories: List[str],
    max_results_per_category: int = 5,
    request_timeout: int = 10,
    max_concurrent_requests: int = 5
) -> Tuple[List[Dict], List[Dict]]:
    """
    Asynchronously fetches latest news from MSN Free APIs across multiple categories
    using parallel execution with controlled concurrency.

    Args:
        categories: List of news categories to search
        max_results_per_category: Maximum results per category (default: 5)
        request_timeout: Request timeout in seconds (default: 10)
        max_concurrent_requests: Maximum simultaneous API requests (default: 5)

    Returns:
        Tuple containing:
        - List of successful news articles
        - List of error dictionaries with details
    """

    results = []
    errors = []
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_category_news(
                session=session,
                semaphore=semaphore,
                category=category,
                max_results=max_results_per_category,
                timeout=request_timeout
            )
            for category in categories
        ]
        category_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in category_results:
            if isinstance(result, Exception):
                errors.append(_format_error(result))
            else:
                results.extend(result)

    logger.info(f"Completed news fetch with {len(results)} results and {len(errors)} errors")
    return results, errors

async def _fetch_category_news(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    category: str,
    max_results: int,
    timeout: int
) -> List[Dict]:
    """Helper function to fetch news for a single category with error handling"""
    async with semaphore:
        try:
            # Replace with actual MSN API endpoint and parameters
            api_url = f"https://api.msn.com/news/{category}"
            params = {
                "count": max_results,
                "sortBy": "date",
                "safeSearch": "strict"
            }

            headers = {
                "User-Agent": "NewsFetcher/1.0",
                "Accept": "application/json"
            }

            async with session.get(
                api_url,
                params=params,
                headers=headers,
                timeout=timeout
            ) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(
                        f"API request failed with status {response.status}"
                    )

                json_data = await response.json()
                return _parse_news_items(json_data, category)

        except Exception as e:
            error_msg = f"Failed to fetch {category} news: {str(e)}"
            logger.warning(error_msg)
            raise  # Exception will be captured by parent function

def _parse_news_items(raw_data: Dict, category: str) -> List[Dict]:
    """Parse and validate news items from API response"""
    if not isinstance(raw_data.get("articles"), list):
        raise ValueError("Invalid API response format")

    cleaned_articles = []
    for item in raw_data["articles"]:
        try:
            cleaned = {
                "title": item["title"],
                "url": item["url"],
                "published": _parse_datetime(item["publishedAt"]),
                "category": category,
                "source": item.get("source", {}).get("name"),
                "description": item.get("description")
            }
            cleaned_articles.append(cleaned)
        except KeyError as e:
            logger.warning(f"Skipping invalid news item: Missing key {str(e)}")

    return cleaned_articles

def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Safe datetime parser with multiple format support"""
    if not dt_str:
        return None
    try:
        # Add additional datetime formats as needed
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None

def _format_error(error: Exception) -> Dict:
    """Create structured error dictionary"""
    return {
        "error_type": error.__class__.__name__,
        "message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }

# Example usage
if __name__ == "__main__":
    async def main():
        categories = ["technology", "business", "sports"]
        results, errors = await fetch_news_async(
            categories=categories,
            max_results_per_category=3,
            max_concurrent_requests=2
        )
        
        print(f"Successful results: {len(results)}")
        print(f"Errors encountered: {len(errors)}")

    asyncio.run(main())
    
    
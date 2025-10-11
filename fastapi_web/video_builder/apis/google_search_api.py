from googleapiclient.discovery import build
import pprint
from dotenv import load_dotenv
from pathlib import Path
import sys
import os, re, requests, random, time

# Imports from video_builder package
from video_builder.utils import FileDirectory
from video_builder.ai_apis.text_gen_api import TextGenAPI
from PIL import Image

# Load environment variables from .env file
load_dotenv()

def google_image_search(
    api_key: str,
    cse_id: str,
    search_ai_query: str,
    num_results: int = 10,
    delay_range: tuple[float, float] = (0.6, 1.4)
) -> list[str]:
    """
    Search for images using Google Custom Search API with simple pagination.

    Args:
        api_key: Google API key.
        cse_id: Programmable Search Engine ID.
        query: Search term.
        num_results: Total number of image URLs desired (will paginate, max ~100).
        delay_range: (min_seconds, max_seconds) random sleep between page requests.

    Returns:
        List of image URLs (may be fewer if API runs out).
    """
    
    try:
        service = build("customsearch", "v1", developerKey=api_key)
    except Exception as e:
        print(f"Failed to build service: {e}")
        return []

    collected: list[str] = []
    page_size = 10  # Google allows max 10 per request
    start_index = 1  # 1-based
    max_total = min(num_results, 15)  # API only returns first 15 results

    while len(collected) < max_total and start_index <= 15:
        fetch_count = min(page_size, max_total - len(collected))
        try:
            res = service.cse().list(
                q=search_ai_query,
                cx=cse_id,
                searchType='image',
                num=fetch_count,
                start=start_index
            ).execute()
        except Exception as e:
            print(f"Request error (start={start_index}): {e}")
            break

        items = res.get('items', [])
        if not items:
            print("No more items returned by API.")
            break

        for item in items:
            link = item.get('link')
            if link and link not in collected:
                collected.append(link)
                if len(collected) >= max_total:
                    break

        # Prepare next page
        start_index += len(items)
        if len(collected) >= max_total or start_index > 100:
            break

        # Delay between requests
        if delay_range and delay_range[0] >= 0 and delay_range[1] >= delay_range[0]:
            time.sleep(random.uniform(*delay_range))

    return collected
    
def download_images(
    image_urls: list[str],
    query: str,
    subdir: str = "google_custom_search_api",
    social_media: str | None = None,
    ratio_tolerance: float = 0.15
) -> list[Path]:
    """
    Download images and sort them into orientation folders (horizontal / vertical / square).
    Optionally filter returned list by a target social media size/orientation.

    Args:
        image_urls: List of image URLs.
        query: Query string used to name files and subdirectory.
        subdir: Base directory name to store images.
        social_media: Optional social media preset to filter results. Supported:
            instagram_post (1:1 square)
            instagram_story (9:16 vertical)
            tiktok_video_cover (9:16 vertical)
            youtube_thumbnail (16:9 horizontal)
            facebook_cover (820x312 ~ 2.63:1 horizontal)
        ratio_tolerance: Allowed relative deviation from target aspect ratio.

    Returns:
        List[Path]: If social_media provided, only images matching that spec.
                    Otherwise all downloaded image Paths (across all orientations).
    """
    if not image_urls:
        print("No image URLs provided.")
        return []

    # try:
    # except ImportError:
    #     print("Pillow (PIL) not installed. pip install pillow")
    #     return []

    SOCIAL_MEDIA_SPECS: dict[str, dict] = {
        "instagram_post": {"orientation": "square", "aspect_ratio": (1, 1)},
        "instagram_story": {"orientation": "vertical", "aspect_ratio": (9, 16)},
        "tiktok_video_cover": {"orientation": "vertical", "aspect_ratio": (9, 16)},
        "youtube_thumbnail": {"orientation": "horizontal", "aspect_ratio": (16, 9)},
        "facebook_cover": {"orientation": "horizontal", "aspect_ratio": (820, 312)},
    }

    spec = None
    if social_media:
        spec = SOCIAL_MEDIA_SPECS.get(social_media.lower())
        if not spec:
            print(f"Unknown social_media preset '{social_media}'. Ignoring filter.")
            social_media = None

    file_dir = FileDirectory()
    base_dir_list = file_dir.create_directory(Path(subdir))
    base_dir = Path(base_dir_list[0]) if base_dir_list else Path(subdir)

    safe_query = re.sub(r'[^a-zA-Z0-9_-]+', '_', query).strip('_').lower() or "query"
    query_dir = base_dir / safe_query
    query_dir.mkdir(parents=True, exist_ok=True)

    # Orientation subfolders
    orient_dirs = {
        "horizontal": (query_dir / "horizontal"),
        "vertical": (query_dir / "vertical"),
        "square": (query_dir / "square"),
    }
    for p in orient_dirs.values():
        p.mkdir(parents=True, exist_ok=True)

    allowed_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ImageFetcher/1.0)"}

    all_downloaded: list[Path] = []
    matched: list[Path] = []

    for idx, url in enumerate(image_urls, 1):
        try:
            resp = requests.get(url, headers=headers, timeout=20, stream=True)
            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "").lower()
            if not content_type.startswith("image/"):
                print(f"Skipped (not image): {url}")
                continue

            ext = Path(url.split("?")[0]).suffix.lower()
            if ext not in allowed_ext:
                subtype = content_type.split("/")[-1].split(";")[0]
                guess_ext = f".{subtype}"
                ext = guess_ext if guess_ext in allowed_ext else ".jpg"

            filename = f"{safe_query}_{idx:03d}{ext}"
            temp_path = query_dir / filename  # temp before moving to orientation folder

            with open(temp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Determine orientation
            try:
                with Image.open(temp_path) as im:
                    width, height = im.size
            except Exception as ie:
                print(f"Could not open image to determine size ({url}): {ie}")
                temp_path.unlink(missing_ok=True)
                continue

            if height == 0 or width == 0:
                print(f"Invalid image dimensions ({url})")
                temp_path.unlink(missing_ok=True)
                continue

            if abs(width - height) / max(width, height) <= 0.05:
                orientation = "square"
            elif width > height:
                orientation = "horizontal"
            else:
                orientation = "vertical"

            final_path = orient_dirs[orientation] / filename
            temp_path.rename(final_path)
            all_downloaded.append(final_path)

            # Social media filtering
            if spec:
                tgt_w, tgt_h = spec["aspect_ratio"]
                target_ratio = tgt_w / tgt_h
                img_ratio = width / height
                rel_diff = abs(img_ratio - target_ratio) / target_ratio
                orient_match = (
                    (spec["orientation"] == "square" and orientation == "square") or
                    (spec["orientation"] == "horizontal" and orientation == "horizontal") or
                    (spec["orientation"] == "vertical" and orientation == "vertical")
                )
                if orient_match and rel_diff <= ratio_tolerance:
                    matched.append(final_path)

        except Exception as e:
            print(f"Failed to download {url}: {e}")

    if social_media and spec:
        print(f"Matched {len(matched)} images for social preset '{social_media}'.")
        return matched

    return all_downloaded

if __name__ == '__main__':
    # Replace with your own credentials and query
    API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    CSE_ID = os.getenv("GOOGLE_SEARCH_ENGINE")
    SEARCH_QUERY = """
    You are an expert prompt engineer specializing in image search. Your task is to convert a user's natural language description into a single, concise, and highly effective one-line search query for an image API.

    Your internal process will be:

    Deconstruct the Idea: First, mentally break down the user's request into its core components. Identify the Subject (who or what), Action (what is happening), Setting (the environment), Mood (the feeling or atmosphere), and any implied Style/Composition (visual aesthetic).
    Synthesize the Query: Combine the most powerful and descriptive keywords from your analysis into a single, cohesive search query. Prioritize words that capture the essence and emotion of the request.
    The final output MUST be only the search query on a single line. Do not include any labels, explanations, or quotation marks.

    --- USER IDEA ---
    BREAKING NEWS on 2023’s most anticipated motorcycles! In this video, we uncover the latest models shaking up the industry. From Ducati’s track-focused Panigale V4 SP2 to Kawasaki’s Ninja ZX-10RR and Yamaha’s tech-packed MT-09, we break down key specs, performance upgrades, and pricing. Plus: Harley-Davidson’s electric LiveWire S2 Del Mar enters the ring!
    
    """
    if not API_KEY or not CSE_ID:
        print("Error: Missing required environment variables.")
        print("Make sure GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE are set.")
        exit(1)
        
    search_ai_query = TextGenAPI().generate_search_query(SEARCH_QUERY)
    image_urls = google_image_search(API_KEY, CSE_ID, search_ai_query, num_results=20)
    truncated_query = " ".join(search_ai_query.split()[:3])
    downloaded_images = download_images(image_urls, truncated_query)
    if image_urls and downloaded_images:
        print(f"download {len(downloaded_images)} images for '{search_ai_query}':")
        # Pretty print the list of URLs
        pprint.pprint(downloaded_images)
    else:
        print(f"No images found for '{search_ai_query}'.")
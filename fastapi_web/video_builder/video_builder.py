import random, json, asyncio, sys, logging, os
from moviepy import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip
from moviepy.video.fx import Resize
from dotenv import load_dotenv
from video_builder.animation.text import create_first5_words_highlighted_clips
from video_builder.transitions.crossfade import add_transitions
from video_builder.tools.close_clip import close_clip_safe

# created functions - imports from within video_builder package
from .utils import FileDirectory
from .whiper_X_transcription import WhisperTranscriber
from .ai_apis.voice_gen_api import download_voice_replicate
from .ai_apis.youtube_api import async_upload_video_to_youtube
from .ai_apis.text_gen_api import TextGenAPI
from .ai_apis.pixabay_api import get_images_videos
from .ai_apis.api_utils import ErrorLogger
from .ai_audio import AudioManager
from .apis.google_search_api import google_image_search, download_images

from .core.config import base_dir
from celery.utils.log import get_task_logger

# Load environment variables - ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24
load_dotenv()

# Create logger instance for video generation using Celery's task logger
logger = get_task_logger(__name__)

logger.info(f"📁 Video generation module initialized")

file_directory = FileDirectory()

# Video configuration
TARGET_SIZE = {
    "youtube_short": (1920, 1080),
    "instagram_feed": (1080, 1080),
    "instagram_story": (1080, 1920),
    "facebook": (1200, 630)
}
CURRENT_SIZE = TARGET_SIZE["youtube_short"]
IMAGE_VIEW_DURATION = 5  # seconds per image
TRANSITION_DURATION = 1  # seconds between images
ZOOM_RATIO = 0.80  # 80% zoom effect

def fit_to_screen(clip, min_zoom=1.0):
    """Resize image to fill screen with aspect ratio preservation, considering minimum zoom."""
    target_w, target_h = CURRENT_SIZE
    # Pre-scale by the minimum zoom factor
    scale = max(target_w / clip.w, target_h / clip.h) * min_zoom
    # print('fit_to_screen scale:', scale)
    return clip.resized(scale).with_position('center')


def create_base_composite_clip(
    image_clip,
    duration,
    background_color=(0, 0, 0),
    overlays=None,
    size=CURRENT_SIZE
):
    """
    Create a base composite video clip with a background, the main image, and optional overlays.
    """
    try:
        # Ensure the main image is centered and has the correct duration
        main_image = image_clip.with_position('center').with_duration(duration)

        # Create the background color clip
        background = ColorClip(
            size=size, color=background_color, duration=duration)

        # Compose the list of layers: background, main image, then overlays
        layers = [background, main_image]
        if overlays:
            layers.extend(overlays)

        composite = CompositeVideoClip(
            layers, size=size).with_duration(duration)
        return composite
    except Exception as e:
        logging.error(f"Error creating base composite clip: {e}")
        return image_clip.with_duration(duration)

def add_face_overlay(audio_duration):
    """Add animated face overlay with MoviePy 2.x syntax"""
    face_paths = file_directory.get_image_files(
        base_dir().joinpath('media', 'faces'), load_clips=False)
    if not face_paths:
        return None

    try:
        return (
            ImageClip(random.choice(face_paths))
            .with_duration(audio_duration)
            .with_effects(Resize(height=200))
            .with_position(('right', 'bottom'))
            .with_layer(2)
        )
    except Exception as e:
        logging.error(f"Face overlay error: {e}")
        return None


def download_google_images(ai_data, num_images=15):
    """
    Download images from Google Search API using AI generated content.
    ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24
    """
    try:
        # Get Google API credentials from environment
        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        cse_id = os.getenv("GOOGLE_SEARCH_ENGINE")
        
        if not api_key or not cse_id:
            logging.warning("Google API credentials not found. Skipping Google image search.")
            return []
            
        # Generate search query from AI data
        text_gen_api = TextGenAPI()
        
        # Create search query from title and description
        search_prompt = f"""
        You are an expert prompt engineer specializing in image search. Your task is to convert a user's natural language description into a single, concise, and highly effective one-line search query for an image API.

        Your internal process will be:
        1. Deconstruct the Idea: First, mentally break down the user's request into its core components
        2. Synthesize the Query: Combine the most powerful and descriptive keywords into a single, cohesive search query

        The final output MUST be only the search query on a single line.

        --- USER CONTENT ---
        Title: {ai_data.get('title', '')}
        Description: {ai_data.get('description', '')}
        Category: {ai_data.get('category', '')}
        """
        
        search_query = text_gen_api.generate_search_query(search_prompt)
        if not search_query:
            logging.warning("Failed to generate search query from AI data.")
            return []
            
        logging.info(f"Searching Google Images for: {search_query}")
        
        # Search for images
        image_urls = google_image_search(
            api_key=api_key,
            cse_id=cse_id, 
            search_ai_query=search_query,
            num_results=num_images
        )
        
        if not image_urls:
            logging.warning("No image URLs found from Google search.")
            return []
            
        # Download images
        # Use first 3 words of search query for directory name
        query_short = " ".join(search_query.split()[:3])
        downloaded_paths = download_images(
            image_urls=image_urls,
            query=query_short,
            subdir="google_search_temp"
        )
        
        logging.info(f"Downloaded {len(downloaded_paths)} images from Google.")
        return downloaded_paths
        
    except Exception as e:
        logging.error(f"Error downloading Google images: {e}")
        return []


def parse_ai_response(response):
    """Parse the AI API response, handling both JSON string and dict."""
    if isinstance(response, dict):
        return response
    try:
        return json.loads(response)
    except Exception as e:
        logging.error(f"Error parsing AI response: {e}")
        return {}


async def upload_to_youtube(video_path, ai_data):
    """Upload the video to YouTube using the YouTube API and AI metadata."""
    try:
        title = ai_data["title"]
        description = ai_data["description"]
        tags = ai_data["tags"]

        response = await async_upload_video_to_youtube(
            video_path,
            title=title,
            description=description,
            tags=tags,
        )
        if response and 'id' in response:
            logging.info(f"Watch it at: https://youtu.be/{response['id']}")
            return response['id']
        else:
            logging.error("Upload failed or no video ID returned.", response)
            return None
    except Exception as e:
        logging.error(f"Error uploading video to YouTube: {e}")
        return None

def main():
    """Main processing function with MoviePy 2.x resource management"""
    clips_to_close = []
    audio_clip = None
    final = None
    output_path = None
    voice = "am_puck"
    prompt = "current news about new era of genAI"
    text_gen_api = TextGenAPI()

    # Generate AI content and check for errors
    ai_data = text_gen_api.generation_text(
        user_message=prompt,
        voiceover_language="English",
        category="Breaking News",
        user="user 2",
    )
    
    # Check if AI generation failed and stop execution
    if isinstance(ai_data, dict) and "error" in ai_data:
        logging.error(f"AI content generation failed: {ai_data['error']}")
        return  # Stop execution completely
    
    # Validate that ai_data has required fields
    required_fields = ["title", "description", "voiceover_script", "tags"]
    if not isinstance(ai_data, dict) or not all(field in ai_data for field in required_fields):
        logging.error("AI response is missing required fields. Stopping execution.")
        logging.error(f"AI data received: {ai_data}")
        return  # Stop execution completely
    
    ai_gen_file_path = str(
        base_dir() / f"ai_voice_gen_{''.join(random.choices('123456789', k=3))}.mp3")
    voice_segments = None
    replicate_audio_dir = None

    # --- Image sourcing - ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24 ---
    google_image_paths = []
    try:
        # Download images from Google Search API
        google_image_paths = download_google_images(ai_data, num_images=15)
        logging.info(f"Google Search downloaded {len(google_image_paths)} images")
    except Exception as e:
        logging.error(f"Error with Google image search: {e}")
        
    # Keep original Pixabay functionality
    try:
        asyncio.run(get_images_videos(ai_data))
        logging.info("Pixabay images download completed")
    except Exception as e:
        logging.error(f"Error with Pixabay: {e}")
    
    # --- Voiceover generation resource selection ---
    ai_genrated_script = ai_data.get("voiceover_script")
    replicate_audio_dir = asyncio.run(download_voice_replicate(
        text=ai_genrated_script, output_path=ai_gen_file_path, voice=voice))
    # for testing purpose commented orignal function
    # replicate_audio_dir = r'G:\Development\auto_movie_editor\tools\ai_voice_gen_985.mp3'
    try:
        transcriber = WhisperTranscriber(language="en")
        if replicate_audio_dir:
            # This returns a dict with "segments"
            voice_segments = transcriber.transcribe_audio_to_json(
                replicate_audio_dir, max_words=5)
    except Exception as e:
        logging.error(f"Error generating Kokoro voiceover: {e}")
        logging.error(f"Error during Whisper transcription: {e}")
        error_line = sys.exc_info()[-1].tb_lineno if sys.exc_info()[-1] else 0
        # Log error details using ErrorLogger
        ErrorLogger.log_ai_response_error(
            error=e,
            response=str(e),
            user="unknown",
            # error_line=sys._getframe().f_lineno,
            error_line=error_line,
            file_name=__file__
        )

    try:
        # Load and process images - ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24
        image_paths = []
        
        # First, try to use Google downloaded images
        if google_image_paths:
            image_paths = google_image_paths[:10]  # Use max 10 Google images
            logging.info(f"Using {len(image_paths)} Google images")
        
        # If not enough Google images, supplement with local images
        if len(image_paths) < 5:  # Minimum 5 images needed
            local_image_paths = file_directory.get_image_files(
                base_dir().joinpath('media', 'bikes_test'), load_clips=False)
            
            if local_image_paths:
                needed_images = 8 - len(image_paths)  # Target 8 total images
                image_paths.extend(local_image_paths[:needed_images])
                logging.info(f"Supplemented with {min(len(local_image_paths), needed_images)} local images")
        
        # Final fallback - use only local images if no Google images
        if not image_paths:
            image_paths = file_directory.get_image_files(
                base_dir().joinpath('media', 'bikes_test'), load_clips=False)
            logging.info("Using local images as fallback")
            
        if not image_paths:
            raise ValueError("No images found - neither from Google search nor local directory")

        # logging.info(f"Total images to process: {len(image_paths)}")

        # Create ImageClip objects with base composite
        raw_clips = []
        for p in image_paths:
            try:
                img_clip = ImageClip(p)
                img_clip = fit_to_screen(img_clip)
                base_clip = create_base_composite_clip(
                    img_clip,
                    duration=IMAGE_VIEW_DURATION,
                    background_color=(0, 0, 0),
                    overlays=None,
                    size=CURRENT_SIZE
                )
                raw_clips.append(base_clip)
                clips_to_close.append(img_clip)
                clips_to_close.append(base_clip)
            except Exception as e:
                logging.error(f"Error processing image {p}: {e}")

        if not raw_clips:
            raise ValueError("No valid image clips could be created.")

        audio_duration = AudioManager.get_audio_duration(replicate_audio_dir)
        final_clips = add_transitions(raw_clips)
        clips_to_close.extend(final_clips)

        # Create main video
        try:
            main_video = CompositeVideoClip(final_clips, size=CURRENT_SIZE)
            clips_to_close.append(main_video)
        except Exception as e:
            logging.error(f"Error creating main video composite: {e}")
            return

        # Add face overlay
        face_clip = add_face_overlay(audio_duration)
        overlays = []
        if face_clip:
            print('face clip :', face_clip)
            clips_to_close.append(face_clip)
            overlays.append(face_clip.with_layer(1))

        # Add first 5 words from each segment as phrase with highlight
        # transcript_path = base_dir() / 'ds_movie_voice.json'
        font_style = base_dir() / 'fonts/opensans/opensans.ttf'
        # Use the "segments" key from the whisper output
        if not voice_segments or "segments" not in voice_segments:
            print("Error: 'segments' not found in Whisper transcription output.")
            raise ValueError(
                "'segments' missing in Whisper transcription output.")
        word_clips = create_first5_words_highlighted_clips(
            voice_segments["segments"], size=CURRENT_SIZE, font=str(font_style))
        print('word reading start...')
        for txt_clip in word_clips:
            overlays.append(txt_clip)
            clips_to_close.append(txt_clip)

        # Compose main video with overlays
        try:
            main_video = CompositeVideoClip(
                [*final_clips, *overlays], size=CURRENT_SIZE)
            clips_to_close.append(main_video)
        except Exception as e:
            logging.error(f"Error creating main video composite: {e}")
            return

        try:
            audio_clip = AudioFileClip(replicate_audio_dir)
            # audio_clip = random.choice(audio_paths)
            audio_clip = audio_clip.with_duration(audio_duration)
            clips_to_close.append(audio_clip)
        except Exception as e:
            logging.error(f"Error loading audio: {e}")
            audio_clip = None

        # Final composition
        try:
            final = main_video.with_audio(
                audio_clip) if audio_clip else main_video
        except Exception as e:
            logging.error(f"Error attaching audio: {e}")
            final = main_video

        # Export video
        output_name = f"output_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))}.mp4"
        output_path = str(base_dir() / output_name)
        try:
            final.write_videofile(
                output_path,
                fps=10,
                codec="libx264",
                preset='fast',
                ffmpeg_params=[
                    '-crf', '18',
                    '-movflags', '+faststart',
                    '-pix_fmt', 'yuv420p'
                ]
            )

            # Use AI-generated metadata
            # print("Using AI-generated metadata for upload.", ai_data)
            asyncio.run(upload_to_youtube(
                video_path=output_path,
                ai_data=ai_data
            ))
        except Exception as e:
            logging.error(f"Error exporting video: {e}")
    except Exception as main_e:
        logging.error(f"Fatal error: {main_e}")
    finally:
        # Cleanup resources
        for clip in clips_to_close:
            close_clip_safe(clip)
        if final and hasattr(final, 'close'):
            close_clip_safe(final)
        if audio_clip and hasattr(audio_clip, 'close'):
            close_clip_safe(audio_clip)


if __name__ == "__main__":
    main()

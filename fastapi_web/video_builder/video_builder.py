import random, json, asyncio, sys, logging, os
# from unicodedata import category
import numpy as np
from pathlib import Path
from moviepy import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip
from moviepy.video.fx import CrossFadeIn, CrossFadeOut, Resize
from dotenv import load_dotenv
from video_builder.animation.text import create_first5_words_highlighted_clips
from video_builder.transitions.crossfade import add_transitions

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

from .core.config import LoggerConfig, base_dir

from .effects.ken_burns import ken_burns_effect

# Load environment variables - ye images ko online search kerne ke liye change kiya gaya hay 2025-09-03 13:30:24
load_dotenv()

# Create logger instance for video generation
logger_config = LoggerConfig(user_name='video_generation', log_user='video_processor')
logger_config.set_debug()  # Set to DEBUG level for detailed logs
logger_config.set_error()
logger_config.set_info()
logger_config.set_warning()
logger = logger_config.get_logger()

logger.info(f"📁 Video generation logs will be saved to logs directory")

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

# def add_transitions_with_config(clips, image_duration=5, transition_duration=1, 
#                                 transition_type='crossfade', transition_intensity=1.0,
#                                 ken_burns_enabled=True, ken_burns_zoom=0.8, 
#                                 ken_burns_direction='zoom_in', slide_direction='left', video_size=(1080,1920)):
#     """
#     Add transitions between clips using user-selected configuration.
    
#     Args:
#         clips: List of video clips
#         image_duration: Duration each image is displayed (seconds)
#         transition_duration: Duration of transition effect (seconds)
#         transition_type: Type of transition ('crossfade', 'slide', 'zoom', 'dissolve')
#         transition_intensity: Intensity of transition effect (0.0-1.0, default 1.0)
#         ken_burns_enabled: Whether to apply Ken Burns pan/zoom effect
#         ken_burns_zoom: Zoom ratio for Ken Burns (0.7-1.0, where <1.0 zooms in)
#         ken_burns_direction: Direction of Ken Burns ('zoom_in', 'zoom_out', 'pan_left', 'pan_right')
    
#     Returns:
#         List of processed clips with transitions
#     """
#     if len(clips) <= 1:
#         return clips

#     final_clips = []
    
#     # Calculate actual fade duration based on intensity
#     actual_fade_duration = transition_duration * transition_intensity
    
#     logging.info(f"🎬 Applying transitions with user config:")
#     logging.info(f"   - Transition Type: {transition_type}")
#     logging.info(f"   - Image Duration: {image_duration}s")
#     logging.info(f"   - Transition Duration: {transition_duration}s (intensity: {transition_intensity})")
#     logging.info(f"   - Actual Fade Duration: {actual_fade_duration}s")
#     logging.info(f"   - Ken Burns: {'Enabled' if ken_burns_enabled else 'Disabled'}")

#     for i, clip in enumerate(clips):
#         try:
#             # Set start time for each clip based on user-selected duration
#             start_time = i * (image_duration - transition_duration)
#             processed_clip = clip.with_start(start_time).with_duration(image_duration)

#             # Apply Ken Burns effect if enabled by user
#             if ken_burns_enabled and ken_burns_zoom >= 0.01:
#                 try:
#                     processed_clip = ken_burns_effect(processed_clip, ken_burns_zoom)
#                     logging.debug(f"Applied Ken Burns effect to clip {i+1}")
#                 except Exception as e:
#                     logging.error(f"Warning: Could not apply Ken Burns effect to clip {i+1}: {e}")



#             # Apply user-selected transition type
#             if transition_type == 'slide' and i > 0:
#                 # Use SliderTransition for slide effect
#                 try:
#                     from video_builder.transitions.slider import SliderTransition
#                     prev_clip = final_clips[-1]
#                     transition = SliderTransition(direction=slide_direction).apply(
#                         prev_clip,
#                         processed_clip,
#                         actual_fade_duration,
#                         video_size
#                     )
#                     # Replace previous clip with transition composite
#                     final_clips[-1] = transition
#                     logging.debug(f"Applied slide transition to clip {i+1} (direction: {slide_direction})")
#                 except Exception as e:
#                     logging.error(f"Warning: Could not apply slide transition to clip {i+1}: {e}")
#                 final_clips.append(processed_clip)
#             else:
#                 # All other transitions (crossfade, zoom, dissolve, fallback)
#                 effects = []
#                 if transition_type == 'crossfade':
#                     if i > 0:
#                         effects.append(CrossFadeIn(actual_fade_duration))
#                     if i < len(clips) - 1:
#                         effects.append(CrossFadeOut(actual_fade_duration))
#                 elif transition_type == 'zoom':
#                     if i > 0:
#                         effects.append(CrossFadeIn(actual_fade_duration))
#                     if i < len(clips) - 1:
#                         effects.append(CrossFadeOut(actual_fade_duration))
#                 elif transition_type == 'dissolve':
#                     if i > 0:
#                         effects.append(CrossFadeIn(actual_fade_duration))
#                     if i < len(clips) - 1:
#                         effects.append(CrossFadeOut(actual_fade_duration))
#                 else:
#                     logging.warning(f"Unknown transition type '{transition_type}', using crossfade")
#                     if i > 0:
#                         effects.append(CrossFadeIn(actual_fade_duration))
#                     if i < len(clips) - 1:
#                         effects.append(CrossFadeOut(actual_fade_duration))
#                 if effects:
#                     try:
#                         processed_clip = processed_clip.with_effects(effects)
#                         logging.debug(f"Applied {transition_type} effects to clip {i+1}")
#                     except Exception as e:
#                         logging.error(f"Warning: Could not apply {transition_type} to clip {i+1}: {e}")
#                 final_clips.append(processed_clip)
#         except Exception as e:
#             logging.error(f"Error processing clip {i+1}: {e}")

#     logging.info(f"✅ Processed {len(final_clips)} clips with {transition_type} transitions")
#     return final_clips


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


# def add_vignette_effect(clip, intensity=0.5):
#     """
#     Apply vignette effect (darkened edges) to a clip.
#     Custom implementation for MoviePy 2.x compatibility.
    
#     Args:
#         clip: The video clip to apply vignette to
#         intensity: Darkness of the vignette (0.0-1.0), default 0.5
    
#     Returns:
#         Clip with vignette effect applied
#     """
#     try:
#         from PIL import Image as PILImage, ImageDraw
        
#         w, h = clip.size
        
#         # Create vignette mask
#         mask = PILImage.new('L', (w, h), 255)
#         draw = ImageDraw.Draw(mask)
        
#         # Create radial gradient for vignette
#         for i in range(int(min(w, h) * 0.4)):
#             alpha = int(255 * (1 - (i / (min(w, h) * 0.4)) * intensity))
#             draw.ellipse(
#                 [i, i, w-i, h-i],
#                 fill=alpha
#             )
        
#         mask_array = np.array(mask) / 255.0
        
#         def apply_vignette(get_frame, t):
#             frame = get_frame(t)
#             # Apply vignette by darkening edges
#             vignette_frame = (frame * mask_array[:, :, np.newaxis]).astype('uint8')
#             return vignette_frame
        
#         return clip.transform(apply_vignette)
#     except Exception as e:
#         logging.warning(f"Could not apply vignette effect: {e}")
#         return clip


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


# def close_clip_safe(clip):
#     """Safely close a MoviePy clip, catching exceptions."""
#     try:
#         if hasattr(clip, 'close'):
#             clip.close()
#     except Exception as e:
#         logging.error(f"Error closing clip: {e}")


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


# def generate_video_from_frontend(script_data: dict, voiceover_data: dict, 
#                                 social_media_data: dict, media_data: dict,
#                                 video_effects_config: dict = None,
#                                 user_id: str = None, video_id: str = None, 
#                                 progress_callback=None):
#     """
#     Generate video using frontend-provided data instead of generating from scratch.
    
#     Args:
#         script_data: Selected script information (title, content, etc.)
#         voiceover_data: Generated voiceover audio file and transcript
#         social_media_data: Social media content and hashtags
#         media_data: Selected media files (images/videos)
#         video_effects_config: User-selected video effects configuration (NEW)
#             - videoConfig: aspect ratio, duration settings
#             - visualEffects: transitions, Ken Burns, color grading
#             - textStyles: text overlays, colors, fonts
#             - audioSettings: volume, background music
#         user_id: User ID for file organization
#         video_id: Video process ID
#         progress_callback: Function to call for progress updates
        
#     Returns:
#         str: Path to generated video file
#     """
#     clips_to_close = []
#     audio_clip = None
#     final = None
    
#     try:
#         if progress_callback:
#             progress_callback(1, "Starting video generation with frontend data...")

#         # ========== Extract Video Effects Configuration ========== 
#         # Get user-selected effects with safe defaults
#         video_config = video_effects_config.get('videoConfig', {}) if video_effects_config else {}
#         visual_effects = video_effects_config.get('visualEffects', {}) if video_effects_config else {}
#         text_styles = video_effects_config.get('textStyles', {}) if video_effects_config else {}
#         audio_settings = video_effects_config.get('audioSettings', {}) if video_effects_config else {}

#         # Video Configuration
#         aspect_ratio = video_config.get('aspectRatio', 'youtube_short')
#         image_duration = video_config.get('imageDuration', 5)
#         transition_duration = video_config.get('transitionDuration', 1)

#         # Visual Effects - Transitions
#         transition_type = visual_effects.get('transitions', {}).get('type', 'crossfade')
#         transition_intensity = visual_effects.get('transitions', {}).get('intensity', 0.5)
#         transition_duration_effect = visual_effects.get('transitions', {}).get('duration', 1.0)
#         slide_direction = visual_effects.get('transitions', {}).get('slideDirection', 'left')

#         # Visual Effects - Ken Burns
#         ken_burns_enabled = visual_effects.get('kenBurns', {}).get('enabled', True)
#         ken_burns_zoom = visual_effects.get('kenBurns', {}).get('zoomRatio', 0.8)
#         ken_burns_direction = visual_effects.get('kenBurns', {}).get('direction', 'zoom_in')

#         # Visual Effects - Color Grading
#         color_grading_enabled = visual_effects.get('colorGrading', {}).get('enabled', False)
#         brightness = visual_effects.get('colorGrading', {}).get('brightness', 0)
#         contrast = visual_effects.get('colorGrading', {}).get('contrast', 0)
#         saturation = visual_effects.get('colorGrading', {}).get('saturation', 0)
#         warmth = visual_effects.get('colorGrading', {}).get('warmth', 0)
        
#         # Visual Effects - Overlays
#         face_overlay_enabled = visual_effects.get('overlays', {}).get('faceOverlay', True)
#         particles_enabled = visual_effects.get('overlays', {}).get('particles', False)
#         vignette_enabled = visual_effects.get('overlays', {}).get('vignette', False)
        
#         # Text Styling
#         text_enabled = text_styles.get('enabled', True)
#         text_position = text_styles.get('position', 'top')
#         text_font_size = text_styles.get('fontSize', 100)
#         text_font_family = text_styles.get('fontFamily', 'Arial')
#         text_base_color = text_styles.get('baseColor', '#ffffff')
#         text_highlight_color = text_styles.get('highlightColor', '#ffe066')
#         text_highlight_text_color = text_styles.get('highlightTextColor', '#000000')
#         text_border_color = text_styles.get('borderColor', '#ffae00')
#         text_border_width = text_styles.get('borderWidth', 4)
        
#         # Audio Settings
#         background_music_enabled = audio_settings.get('backgroundMusic', False)
#         music_volume = audio_settings.get('musicVolume', 0.3)
#         voice_volume = audio_settings.get('voiceVolume', 1.0)
        
#         # Calculate video dimensions based on aspect ratio
#         aspect_ratio_dimensions = {
#             'youtube_short': (1080, 1920),      # 9:16
#             'instagram_feed': (1080, 1080),     # 1:1
#             'instagram_story': (1080, 1920),    # 9:16
#             'facebook': (1200, 630)             # 16:9
#         }
#         video_width, video_height = aspect_ratio_dimensions.get(aspect_ratio, (1080, 1920))
        
#         # Log configuration for debugging
#         logging.info(f"🎨 Video Effects Config Applied:")
#         logging.info(f"  - Aspect Ratio: {aspect_ratio} ({video_width}x{video_height})")
#         logging.info(f"  - Image Duration: {image_duration}s")
#         logging.info(f"  - Transition: {transition_type} ({transition_duration}s)")
#         logging.info(f"  - Ken Burns: {'Enabled' if ken_burns_enabled else 'Disabled'} ({ken_burns_direction}, {ken_burns_zoom})")
#         logging.info(f"  - Color Grading: {'Enabled' if color_grading_enabled else 'Disabled'}")
#         logging.info(f"  - Text Overlay: {'Enabled' if text_enabled else 'Disabled'} at {text_position}")
        
#         # ========== End of Configuration Extraction ==========
        
#         # Use frontend data instead of generating
#         ai_data = {
#             "title": script_data.get('title', 'Generated Video'),
#             "description": script_data.get('content', ''),
#             "voiceover_script": script_data.get('voiceover_script', script_data.get('content', '')),
#             "tags": social_media_data.get('tags', [])
#         }
        
#         if progress_callback:
#             progress_callback(2, "Processing frontend voiceover data...")
        
#         # Use frontend voiceover data
#         voiceover_file_path = voiceover_data.get('audio_file_path')
#         voice_segments = voiceover_data.get('transcript', {})
        
#         if not voiceover_file_path:
#             raise ValueError("No voiceover file provided in frontend data")
        
#         if progress_callback:
#             progress_callback(3, "Processing frontend media files...")
        
#         # Use frontend media files
#         image_paths = []
#         for media_item in media_data.get('selected_media', []):
#             if media_item.get('type') == 'image' and media_item.get('file_path'):
#                 image_paths.append(media_item['file_path'])
        
#         if not image_paths:
#             raise ValueError("No image files provided in frontend data")
        
#         if progress_callback:
#             progress_callback(4, "Creating video clips from images...")
        
#         # Create ImageClip objects with base composite using user-selected settings
#         raw_clips = []
#         for i, p in enumerate(image_paths):
#             try:
#                 img_clip = ImageClip(p)
#                 img_clip = fit_to_screen(img_clip)
                
#                 # Use user-selected image duration and video size
#                 base_clip = create_base_composite_clip(
#                     img_clip,
#                     duration=image_duration,  # User-selected duration
#                     background_color=(0, 0, 0),
#                     overlays=None,
#                     size=(video_width, video_height)  # User-selected aspect ratio
#                 )
#                 raw_clips.append(base_clip)
#                 clips_to_close.extend([img_clip, base_clip])
#             except Exception as e:
#                 logging.error(f"Error processing image {p}: {e}")
        
#         if not raw_clips:
#             raise ValueError("No valid image clips could be created.")
        
#         if progress_callback:
#             progress_callback(5, "Applying transitions and effects...")
        
#         # Apply transitions and effects with user settings
#         audio_duration = AudioManager.get_audio_duration(voiceover_file_path)
        
#         # Use user-selected transition settings instead of global constants
#         final_clips = add_transitions_with_config(
#             raw_clips, 
#             image_duration=image_duration,
#             transition_duration=transition_duration,
#             transition_type=transition_type,
#             transition_intensity=transition_intensity,  # Add intensity
#             ken_burns_enabled=ken_burns_enabled,
#             ken_burns_zoom=ken_burns_zoom,
#             ken_burns_direction=ken_burns_direction,
#             slide_direction=slide_direction,
#             video_size=(video_width, video_height)
#         )
#         clips_to_close.extend(final_clips)
        
#         if progress_callback:
#             progress_callback(6, "Creating video composition...")
        
#         # Create main video with user-selected aspect ratio
#         main_video = CompositeVideoClip(final_clips, size=(video_width, video_height))
#         clips_to_close.append(main_video)
        
#         # Apply vignette effect if enabled by user (MoviePy 2.x compatible)
#         if vignette_enabled:
#             try:
#                 logging.info("✨ Applying vignette effect (dark edges)")
#                 main_video = add_vignette_effect(main_video, intensity=0.5)  # 0.5 = medium intensity
#             except Exception as e:
#                 logging.error(f"⚠️  Could not apply vignette effect: {e}")
        
#         # Add overlays (only if enabled by user)
#         overlays = []
        
#         # Add face overlay (only if enabled)
#         if face_overlay_enabled:
#             face_clip = add_face_overlay(audio_duration)
#             if face_clip:
#                 clips_to_close.append(face_clip)
#                 overlays.append(face_clip.with_layer(1))
        
#         if progress_callback:
#             progress_callback(7, "Adding text overlays and synchronization...")
        
#         # Add text overlays if transcript available (only if enabled by user)
#         logging.info(f"📝 Text Overlay Debug - Checking conditions:")
#         logging.info(f"   - text_enabled: {text_enabled}")
#         logging.info(f"   - voice_segments exists: {voice_segments is not None}")
#         logging.info(f"   - voice_segments type: {type(voice_segments)}")
#         if voice_segments:
#             logging.info(f"   - voice_segments keys: {voice_segments.keys()}")
#             logging.info(f"   - 'segments' in voice_segments: {'segments' in voice_segments}")
#             if 'segments' in voice_segments:
#                 logging.info(f"   - Number of segments: {len(voice_segments['segments'])}")
#                 logging.info(f"   - First segment sample: {voice_segments['segments'][0] if voice_segments['segments'] else 'None'}")
        
#         if text_enabled and voice_segments and "segments" in voice_segments:
#             font_style = base_dir() / 'fonts/opensans/opensans.ttf'
#             logging.info(f"🎨 Applying custom text colors: base={text_base_color}, highlight={text_highlight_color}, border={text_border_color}")
#             logging.info(f"🎨 Text config: fontSize={text_font_size}, position={text_position}, borderWidth={text_border_width}")
#             # Function is already imported at top of file
#             word_clips = create_first5_words_highlighted_clips(
#                 voice_segments["segments"], 
#                 size=(video_width, video_height), 
#                 font=str(font_style),
#                 font_size=text_font_size,  # Use user's font size
#                 base_color=text_base_color,  # Use user's base color
#                 highlight_color=text_highlight_color,  # Use user's highlight bg color
#                 highlight_text_color=text_highlight_text_color,  # Use user's highlight text color
#                 border_color=text_border_color,  # Use user's border color
#                 border_width=text_border_width,  # Use user's border width
#                 position=('center', text_position)  # Use user's position
#             )
#             logging.info(f"✅ Text overlay function returned {len(word_clips)} clips")
#             if word_clips:
#                 logging.info(f"   - First clip type: {type(word_clips[0])}")
#                 logging.info(f"   - First clip duration: {word_clips[0].duration if hasattr(word_clips[0], 'duration') else 'N/A'}")
#                 logging.info(f"   - First clip start: {word_clips[0].start if hasattr(word_clips[0], 'start') else 'N/A'}")
#             for txt_clip in word_clips:
#                 overlays.append(txt_clip)
#                 clips_to_close.append(txt_clip)
#         else:
#             logging.warning(f"⚠️  Text overlays NOT applied - conditions not met")
#             if not text_enabled:
#                 logging.warning(f"   - Reason: text_enabled is False")
#             if not voice_segments:
#                 logging.warning(f"   - Reason: voice_segments is None/empty")
#             elif "segments" not in voice_segments:
#                 logging.warning(f"   - Reason: 'segments' key not found in voice_segments")
        
#         # Compose final video with overlays using user-selected size
#         logging.info(f"🎬 Composing final video:")
#         logging.info(f"   - Number of final_clips: {len(final_clips)}")
#         logging.info(f"   - Number of overlays: {len(overlays)}")
#         logging.info(f"   - Video size: {video_width}x{video_height}")
#         if overlays:
#             logging.info(f"   - Creating CompositeVideoClip with {len(final_clips)} base clips + {len(overlays)} overlays")
#             main_video = CompositeVideoClip([*final_clips, *overlays], size=(video_width, video_height))
#             clips_to_close.append(main_video)
#         else:
#             logging.info(f"   - No overlays to add, using base final_clips only")
        
#         if progress_callback:
#             progress_callback(8, "Adding audio track...")
        
#         # Add audio
#         try:
#             audio_clip = AudioFileClip(voiceover_file_path)
#             audio_clip = audio_clip.with_duration(audio_duration)
#             clips_to_close.append(audio_clip)
#             final = main_video.with_audio(audio_clip)
#         except Exception as e:
#             logging.error(f"Error loading audio: {e}")
#             final = main_video
        
#         if progress_callback:
#             progress_callback(9, "Exporting final video...")
        
#         # Export video
#         output_name = f"frontend_video_{video_id}_{user_id}.mp4"
#         output_path = str(base_dir() / output_name)
        
#         final.write_videofile(
#             output_path,
#             fps=10,
#             codec="libx264",
#             preset='fast',
#             ffmpeg_params=[
#                 '-crf', '18',
#                 '-movflags', '+faststart',
#                 '-pix_fmt', 'yuv420p'
#             ]
#         )
        
#         if progress_callback:
#             progress_callback(10, "Video generation completed successfully!")
        
#         return output_path
        
#     except Exception as e:
#         logging.error(f"Error in frontend video generation: {e}")
#         if progress_callback:
#             progress_callback(-1, f"Error: {str(e)}")
#         raise
#     finally:
#         # Cleanup resources
#         for clip in clips_to_close:
#             close_clip_safe(clip)
#         if final and hasattr(final, 'close'):
#             close_clip_safe(final)
#         if audio_clip and hasattr(audio_clip, 'close'):
#             close_clip_safe(audio_clip)


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

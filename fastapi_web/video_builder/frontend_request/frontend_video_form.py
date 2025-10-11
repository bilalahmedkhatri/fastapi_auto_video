from video_builder.core.config import base_dir
from video_builder.video_builder import AudioManager, fit_to_screen
from video_builder.effects.face_overlay import add_face_overlay
from video_builder.effects.vignette import add_vignette_effect
from moviepy import CompositeVideoClip, AudioFileClip, ImageClip
from video_builder.core.create_video_base import create_base_composite_clip
from video_builder.transitions.crossfade import add_transitions_with_config
from video_builder.animation.text import create_first5_words_highlighted_clips
from video_builder.tools.close_clip import close_clip_safe
from video_builder.apis.google_search_api import download_images
from pathlib import Path
from celery.utils.log import get_task_logger

# Create logger using Celery's task logger
logger = get_task_logger(__name__)


def generate_video_from_frontend(script_data: dict, voiceover_data: dict, 
                                social_media_data: dict, media_data: dict,
                                video_effects_config: dict = None,
                                user_id: str = None, video_id: str = None, 
                                progress_callback=None):
    """
    Generate video using frontend-provided data instead of generating from scratch.
    
    Args:
        script_data: Selected script information (title, content, etc.)
        voiceover_data: Generated voiceover audio file and transcript
        social_media_data: Social media content and hashtags
        media_data: Selected media files (images/videos)
        video_effects_config: User-selected video effects configuration (NEW)
            - videoConfig: aspect ratio, duration settings
            - visualEffects: transitions, Ken Burns, color grading
            - textStyles: text overlays, colors, fonts
            - audioSettings: volume, background music
        user_id: User ID for file organization
        video_id: Video process ID
        progress_callback: Function to call for progress updates
        
    Returns:
        str: Path to generated video file
    """
    clips_to_close = []
    audio_clip = None
    final = None
    
    try:
        if progress_callback:
            progress_callback(1, "Starting video generation with frontend data...")

        # ========== Extract Video Effects Configuration ========== 
        # Get user-selected effects with safe defaults
        video_config = video_effects_config.get('videoConfig', {}) if video_effects_config else {}
        visual_effects = video_effects_config.get('visualEffects', {}) if video_effects_config else {}
        text_styles = video_effects_config.get('textStyles', {}) if video_effects_config else {}
        audio_settings = video_effects_config.get('audioSettings', {}) if video_effects_config else {}

        # Video Configuration
        aspect_ratio = video_config.get('aspectRatio', 'youtube_short')
        image_duration = video_config.get('imageDuration', 5)
        transition_duration = video_config.get('transitionDuration', 1)

        # Visual Effects - Transitions
        transition_type = visual_effects.get('transitions', {}).get('type', 'crossfade')
        transition_intensity = visual_effects.get('transitions', {}).get('intensity', 0.5)
        transition_duration_effect = visual_effects.get('transitions', {}).get('duration', 1.0)
        slide_direction = visual_effects.get('transitions', {}).get('slideDirection', 'left')

        # Visual Effects - Ken Burns
        ken_burns_enabled = visual_effects.get('kenBurns', {}).get('enabled', True)
        ken_burns_zoom = visual_effects.get('kenBurns', {}).get('zoomRatio', 0.8)
        ken_burns_direction = visual_effects.get('kenBurns', {}).get('direction', 'zoom_in')

        # Visual Effects - Color Grading
        color_grading_enabled = visual_effects.get('colorGrading', {}).get('enabled', False)
        brightness = visual_effects.get('colorGrading', {}).get('brightness', 0)
        contrast = visual_effects.get('colorGrading', {}).get('contrast', 0)
        saturation = visual_effects.get('colorGrading', {}).get('saturation', 0)
        warmth = visual_effects.get('colorGrading', {}).get('warmth', 0)
        
        # Visual Effects - Overlays
        face_overlay_enabled = visual_effects.get('overlays', {}).get('faceOverlay', True)
        particles_enabled = visual_effects.get('overlays', {}).get('particles', False)
        vignette_enabled = visual_effects.get('overlays', {}).get('vignette', False)
        
        # Text Styling
        text_enabled = text_styles.get('enabled', True)
        text_position = text_styles.get('position', 'top')
        text_font_size = text_styles.get('fontSize', 100)
        text_font_family = text_styles.get('fontFamily', 'Arial')
        text_base_color = text_styles.get('baseColor', '#ffffff')
        text_highlight_color = text_styles.get('highlightColor', '#ffe066')
        text_highlight_text_color = text_styles.get('highlightTextColor', '#000000')
        text_border_color = text_styles.get('borderColor', '#ffae00')
        text_border_width = text_styles.get('borderWidth', 4)
        
        # Audio Settings
        background_music_enabled = audio_settings.get('backgroundMusic', False)
        music_volume = audio_settings.get('musicVolume', 0.3)
        voice_volume = audio_settings.get('voiceVolume', 1.0)
        
        # Calculate video dimensions based on aspect ratio
        aspect_ratio_dimensions = {
            'youtube_short': (1080, 1920),      # 9:16
            'instagram_feed': (1080, 1080),     # 1:1
            'instagram_story': (1080, 1920),    # 9:16
            'facebook': (1200, 630)             # 16:9
        }
        video_width, video_height = aspect_ratio_dimensions.get(aspect_ratio, (1080, 1920))
        
        # Log configuration for debugging
        logger.info(f"🎨 Video Effects Config Applied:")
        logger.info(f"  - Aspect Ratio: {aspect_ratio} ({video_width}x{video_height})")
        logger.info(f"  - Image Duration: {image_duration}s")
        logger.info(f"  - Transition: {transition_type} ({transition_duration}s)")
        logger.info(f"  - Ken Burns: {'Enabled' if ken_burns_enabled else 'Disabled'} ({ken_burns_direction}, {ken_burns_zoom})")
        logger.info(f"  - Color Grading: {'Enabled' if color_grading_enabled else 'Disabled'}")
        logger.info(f"  - Text Overlay: {'Enabled' if text_enabled else 'Disabled'} at {text_position}")
        
        # ========== End of Configuration Extraction ==========
        
        # Use frontend data instead of generating
        ai_data = {
            "title": script_data.get('title', 'Generated Video'),
            "description": script_data.get('content', ''),
            "voiceover_script": script_data.get('voiceover_script', script_data.get('content', '')),
            "tags": social_media_data.get('tags', [])
        }
        
        if progress_callback:
            progress_callback(2, "Processing frontend voiceover data...")
        
        # Use frontend voiceover data
        voiceover_file_path = voiceover_data.get('audio_file_path')
        voice_segments = voiceover_data.get('transcript', {})
        
        if not voiceover_file_path:
            raise ValueError("No voiceover file provided in frontend data")
        
        if progress_callback:
            progress_callback(3, "Processing frontend media files...")
        
        # Use frontend media files - Download URLs if needed
        logger.info("📦 Processing media data...")
        logger.info(f"   Media data keys: {list(media_data.keys()) if media_data else 'None'}")
        
        image_paths = []
        image_urls = []
        
        # Collect image paths and URLs
        selected_media = media_data.get('selected_media', [])
        logger.info(f"   Found {len(selected_media)} media items")
        
        for idx, media_item in enumerate(selected_media, 1):
            if media_item.get('type') == 'image' and media_item.get('file_path'):
                file_path = media_item['file_path']
                logger.info(f"   Item {idx}: {file_path[:100]}...")
                
                # Check if it's a URL or local path
                if file_path.startswith(('http://', 'https://')):
                    logger.info(f"      -> URL detected, will download")
                    image_urls.append(file_path)
                else:
                    logger.info(f"      -> Local path, using directly")
                    image_paths.append(file_path)
        
        # Download images from URLs if any
        if image_urls:
            logger.info(f"📥 Downloading {len(image_urls)} images from URLs...")
            try:
                # Use the script title or video_id for subfolder name
                query_name = script_data.get('title', f'video_{video_id}') if script_data else f'video_{video_id}'
                
                # Download images - this returns list of Path objects
                downloaded_paths = download_images(
                    image_urls=image_urls,
                    query=query_name,
                    subdir=f"media/{user_id or 'temp'}/{video_id}",
                    social_media=None,  # Don't filter by social media type
                    ratio_tolerance=0.15
                )
                
                # Convert Path objects to strings and add to image_paths
                for path in downloaded_paths:
                    image_paths.append(str(path))
                
                logger.info(f"✅ Successfully downloaded {len(downloaded_paths)} images")
                logger.info(f"   Total images available: {len(image_paths)}")
                
            except Exception as download_error:
                logger.error(f"❌ Error downloading images: {download_error}")
                logger.error(f"   Will attempt to use any local paths if available")
        
        if not image_paths:
            raise ValueError("No image files provided in frontend data")
        
        logger.info(f"📸 Creating video clips from {len(image_paths)} images...")
        
        if progress_callback:
            progress_callback(4, "Creating video clips from images...")
        
        # Create ImageClip objects with base composite using user-selected settings
        raw_clips = []
        failed_images = []
        
        for i, p in enumerate(image_paths):
            try:
                logger.info(f"   Processing image {i+1}/{len(image_paths)}: {p}")
                
                # Verify file exists
                if not Path(p).exists():
                    error_msg = f"File not found: {p}"
                    logger.error(f"      ❌ {error_msg}")
                    failed_images.append((p, error_msg))
                    continue
                
                # Create MoviePy ImageClip
                img_clip = ImageClip(p)
                logger.info(f"      ✓ ImageClip created, size: {img_clip.size}")
                
                img_clip = fit_to_screen(img_clip)
                logger.info(f"      ✓ Fitted to screen")
                
                # Use user-selected image duration and video size
                base_clip = create_base_composite_clip(
                    img_clip,
                    duration=image_duration,  # User-selected duration
                    background_color=(0, 0, 0),
                    overlays=None,
                    size=(video_width, video_height), # User-selected aspect ratio 
                    logger=logger
                )
                logger.info(f"      ✓ Base clip created (duration: {image_duration}s)")
                
                raw_clips.append(base_clip)
                clips_to_close.extend([img_clip, base_clip])
                logger.info(f"      ✅ Successfully processed image {i+1}")
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                logger.error(f"      ❌ Error processing image {i+1}: {str(e)}")
                logger.error(f"      Traceback:\n{error_trace}")
                failed_images.append((p, str(e)))
        
        # Provide detailed error if no clips created
        if not raw_clips:
            error_summary = f"No valid image clips could be created.\n"
            error_summary += f"  Total images attempted: {len(image_paths)}\n"
            error_summary += f"  Failed: {len(failed_images)}\n"
            if failed_images:
                error_summary += "\nFailed images:\n"
                for img_path, error in failed_images[:5]:  # Show first 5
                    error_summary += f"  - {img_path}\n    Error: {error}\n"
                if len(failed_images) > 5:
                    error_summary += f"  ... and {len(failed_images) - 5} more\n"
            logger.error(error_summary)
            raise ValueError(error_summary)
        
        logger.info(f"✅ Successfully created {len(raw_clips)}/{len(image_paths)} image clips")
        if failed_images:
            logger.warning(f"⚠️  {len(failed_images)} images failed to process")
        
        if progress_callback:
            progress_callback(5, "Applying transitions and effects...")
        
        # Apply transitions and effects with user settings
        audio_duration = AudioManager.get_audio_duration(voiceover_file_path)
        
        # Use user-selected transition settings instead of global constants
        final_clips = add_transitions_with_config(
            raw_clips, 
            image_duration=image_duration,
            transition_duration=transition_duration,
            transition_type=transition_type,
            transition_intensity=transition_intensity,  # Add intensity
            ken_burns_enabled=ken_burns_enabled,
            ken_burns_zoom=ken_burns_zoom,
            ken_burns_direction=ken_burns_direction,
            slide_direction=slide_direction,
            video_size=(video_width, video_height)
        )
        clips_to_close.extend(final_clips)
        
        if progress_callback:
            progress_callback(6, "Creating video composition...")
        
        # Create main video with user-selected aspect ratio
        main_video = CompositeVideoClip(final_clips, size=(video_width, video_height))
        clips_to_close.append(main_video)
        
        # Apply vignette effect if enabled by user (MoviePy 2.x compatible)
        if vignette_enabled:
            try:
                logger.info("✨ Applying vignette effect (dark edges)")
                main_video = add_vignette_effect(main_video, intensity=0.5)  # 0.5 = medium intensity
            except Exception as e:
                logger.error(f"⚠️  Could not apply vignette effect: {e}")
        
        # Add overlays (only if enabled by user)
        overlays = []
        
        # Add face overlay (only if enabled)
        if face_overlay_enabled:
            face_clip = add_face_overlay(audio_duration)
            if face_clip:
                clips_to_close.append(face_clip)
                overlays.append(face_clip.with_layer(1))
        
        if progress_callback:
            progress_callback(7, "Adding text overlays and synchronization...")
        
        # Add text overlays if transcript available (only if enabled by user)
        logger.info(f"📝 Text Overlay Debug - Checking conditions:")
        logger.info(f"   - text_enabled: {text_enabled}")
        logger.info(f"   - voice_segments exists: {voice_segments is not None}")
        logger.info(f"   - voice_segments type: {type(voice_segments)}")
        if voice_segments:
            logger.info(f"   - voice_segments keys: {voice_segments.keys()}")
            logger.info(f"   - 'segments' in voice_segments: {'segments' in voice_segments}")
            if 'segments' in voice_segments:
                logger.info(f"   - Number of segments: {len(voice_segments['segments'])}")
                logger.info(f"   - First segment sample: {voice_segments['segments'][0] if voice_segments['segments'] else 'None'}")
        
        if text_enabled and voice_segments and "segments" in voice_segments:
            font_style = base_dir() / 'fonts/opensans/opensans.ttf'
            logger.info(f"🎨 Applying custom text colors: base={text_base_color}, highlight={text_highlight_color}, border={text_border_color}")
            logger.info(f"🎨 Text config: fontSize={text_font_size}, position={text_position}, borderWidth={text_border_width}")
            # Function is already imported at top of file
            word_clips = create_first5_words_highlighted_clips(
                voice_segments["segments"], 
                size=(video_width, video_height), 
                font=str(font_style),
                font_size=text_font_size,  # Use user's font size
                base_color=text_base_color,  # Use user's base color
                highlight_color=text_highlight_color,  # Use user's highlight bg color
                highlight_text_color=text_highlight_text_color,  # Use user's highlight text color
                border_color=text_border_color,  # Use user's border color
                border_width=text_border_width,  # Use user's border width
                position=('center', text_position)  # Use user's position
            )
            logger.info(f"✅ Text overlay function returned {len(word_clips)} clips")
            if word_clips:
                logger.info(f"   - First clip type: {type(word_clips[0])}")
                logger.info(f"   - First clip duration: {word_clips[0].duration if hasattr(word_clips[0], 'duration') else 'N/A'}")
                logger.info(f"   - First clip start: {word_clips[0].start if hasattr(word_clips[0], 'start') else 'N/A'}")
            for txt_clip in word_clips:
                overlays.append(txt_clip)
                clips_to_close.append(txt_clip)
        else:
            logger.warning(f"⚠️  Text overlays NOT applied - conditions not met")
            if not text_enabled:
                logger.warning(f"   - Reason: text_enabled is False")
            if not voice_segments:
                logger.warning(f"   - Reason: voice_segments is None/empty")
            elif "segments" not in voice_segments:
                logger.warning(f"   - Reason: 'segments' key not found in voice_segments")
        
        # Compose final video with overlays using user-selected size
        logger.info(f"🎬 Composing final video:")
        logger.info(f"   - Number of final_clips: {len(final_clips)}")
        logger.info(f"   - Number of overlays: {len(overlays)}")
        logger.info(f"   - Video size: {video_width}x{video_height}")
        if overlays:
            logger.info(f"   - Creating CompositeVideoClip with {len(final_clips)} base clips + {len(overlays)} overlays")
            main_video = CompositeVideoClip([*final_clips, *overlays], size=(video_width, video_height))
            clips_to_close.append(main_video)
        else:
            logger.info(f"   - No overlays to add, using base final_clips only")
        
        if progress_callback:
            progress_callback(8, "Adding audio track...")
        
        # Add audio
        try:
            audio_clip = AudioFileClip(voiceover_file_path)
            audio_clip = audio_clip.with_duration(audio_duration)
            clips_to_close.append(audio_clip)
            final = main_video.with_audio(audio_clip)
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            final = main_video
        
        if progress_callback:
            progress_callback(9, "Exporting final video...")
        
        # Export video
        output_name = f"frontend_video_{video_id}_{user_id}.mp4"
        output_path = str(base_dir() / output_name)
        
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
        
        if progress_callback:
            progress_callback(10, "Video generation completed successfully!")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error in frontend video generation: {e}")
        if progress_callback:
            progress_callback(-1, f"Error: {str(e)}")
        raise
    finally:
        # Cleanup resources
        for clip in clips_to_close:
            close_clip_safe(clip)
        if final and hasattr(final, 'close'):
            close_clip_safe(final)
        if audio_clip and hasattr(audio_clip, 'close'):
            close_clip_safe(audio_clip)
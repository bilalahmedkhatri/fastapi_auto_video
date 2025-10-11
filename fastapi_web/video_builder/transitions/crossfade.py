from moviepy.video.fx import CrossFadeIn, CrossFadeOut
from video_builder.effects.ken_burns import ken_burns_effect
from celery.utils.log import get_task_logger

# Create logger using Celery's task logger
logger = get_task_logger(__name__)


def add_transitions(clips):
    if len(clips) <= 1:
        return clips

    final_clips = []

    for i, clip in enumerate(clips):
        # print(f"Processing clip {i+1}/{len(clips)}")
        try:
            # Set start time for each clip
            start_time = i * (5 - 1)
            processed_clip = clip.with_start(
                start_time).with_duration(5)

            # Apply Ken Burns effect if enabled
            if 0.80 >= 0.01:
                try:
                    processed_clip = ken_burns_effect(
                        processed_clip, 0.80)
                    # print(f"Applied Ken Burns effect to clip {i+1}")
                except Exception as e:
                    logger.error(
                        f"Warning: Could not apply Ken Burns effect to clip {i+1}: {e}")

            # Apply crossfade transitions (skip first clip for fade in, skip last for fade out)
            effects = []
            if i > 0:  # Not the first clip
                effects.append(CrossFadeIn(1))
            if i < len(clips) - 1:  # Not the last clip
                effects.append(CrossFadeOut(1))

            if effects:
                try:
                    processed_clip = processed_clip.with_effects(effects)
                    # print(f"Applied crossfade effects to clip {i+1}")
                except Exception as e:
                    logger.error(
                        f"Warning: Could not apply crossfade to clip {i+1}: {e}")

            final_clips.append(processed_clip)
        except Exception as e:
            logger.error(f"Error processing clip {i+1}: {e}")

    return final_clips


def add_transitions_with_config(clips, image_duration=5, transition_duration=1, 
                                transition_type='crossfade', transition_intensity=1.0,
                                ken_burns_enabled=True, ken_burns_zoom=0.8, 
                                ken_burns_direction='zoom_in', slide_direction='left', video_size=(1080,1920)):
    """
    Add transitions between clips using user-selected configuration.
    
    Args:
        clips: List of video clips
        image_duration: Duration each image is displayed (seconds)
        transition_duration: Duration of transition effect (seconds)
        transition_type: Type of transition ('crossfade', 'slide', 'zoom', 'dissolve')
        transition_intensity: Intensity of transition effect (0.0-1.0, default 1.0)
        ken_burns_enabled: Whether to apply Ken Burns pan/zoom effect
        ken_burns_zoom: Zoom ratio for Ken Burns (0.7-1.0, where <1.0 zooms in)
        ken_burns_direction: Direction of Ken Burns ('zoom_in', 'zoom_out', 'pan_left', 'pan_right')
    
    Returns:
        List of processed clips with transitions
    """
    if len(clips) <= 1:
        return clips

    final_clips = []
    
    # Calculate actual fade duration based on intensity
    actual_fade_duration = transition_duration * transition_intensity
    
    logger.info(f"🎬 Applying transitions with user config:")
    logger.info(f"   - Transition Type: {transition_type}")
    logger.info(f"   - Image Duration: {image_duration}s")
    logger.info(f"   - Transition Duration: {transition_duration}s (intensity: {transition_intensity})")
    logger.info(f"   - Actual Fade Duration: {actual_fade_duration}s")
    logger.info(f"   - Ken Burns: {'Enabled' if ken_burns_enabled else 'Disabled'}")

    for i, clip in enumerate(clips):
        try:
            # Set start time for each clip based on user-selected duration
            start_time = i * (image_duration - transition_duration)
            processed_clip = clip.with_start(start_time).with_duration(image_duration)

            # Apply Ken Burns effect if enabled by user
            if ken_burns_enabled and ken_burns_zoom >= 0.01:
                try:
                    processed_clip = ken_burns_effect(processed_clip, ken_burns_zoom)
                    logger.debug(f"Applied Ken Burns effect to clip {i+1}")
                except Exception as e:
                    logger.error(f"Warning: Could not apply Ken Burns effect to clip {i+1}: {e}")



            # Apply user-selected transition type
            if transition_type == 'slide' and i > 0:
                # Use SliderTransition for slide effect
                try:
                    from video_builder.transitions.slider import SliderTransition
                    prev_clip = final_clips[-1]
                    transition = SliderTransition(direction=slide_direction).apply(
                        prev_clip,
                        processed_clip,
                        actual_fade_duration,
                        video_size
                    )
                    # Replace previous clip with transition composite
                    final_clips[-1] = transition
                    logger.debug(f"Applied slide transition to clip {i+1} (direction: {slide_direction})")
                except Exception as e:
                    logger.error(f"Warning: Could not apply slide transition to clip {i+1}: {e}")
                final_clips.append(processed_clip)
            else:
                # All other transitions (crossfade, zoom, dissolve, fallback)
                effects = []
                if transition_type == 'crossfade':
                    if i > 0:
                        effects.append(CrossFadeIn(actual_fade_duration))
                    if i < len(clips) - 1:
                        effects.append(CrossFadeOut(actual_fade_duration))
                elif transition_type == 'zoom':
                    if i > 0:
                        effects.append(CrossFadeIn(actual_fade_duration))
                    if i < len(clips) - 1:
                        effects.append(CrossFadeOut(actual_fade_duration))
                elif transition_type == 'dissolve':
                    if i > 0:
                        effects.append(CrossFadeIn(actual_fade_duration))
                    if i < len(clips) - 1:
                        effects.append(CrossFadeOut(actual_fade_duration))
                else:
                    logger.warning(f"Unknown transition type '{transition_type}', using crossfade")
                    if i > 0:
                        effects.append(CrossFadeIn(actual_fade_duration))
                    if i < len(clips) - 1:
                        effects.append(CrossFadeOut(actual_fade_duration))
                if effects:
                    try:
                        processed_clip = processed_clip.with_effects(effects)
                        logger.debug(f"Applied {transition_type} effects to clip {i+1}")
                    except Exception as e:
                        logger.error(f"Warning: Could not apply {transition_type} to clip {i+1}: {e}")
                final_clips.append(processed_clip)
        except Exception as e:
            logger.error(f"Error processing clip {i+1}: {e}")

    logger.info(f"✅ Processed {len(final_clips)} clips with {transition_type} transitions")
    return final_clips

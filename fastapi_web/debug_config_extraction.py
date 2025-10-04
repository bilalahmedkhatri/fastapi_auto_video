#!/usr/bin/env python3
"""
Debug script to trace exactly what config values are being extracted and used
"""

# Sample frontend data from your screenshot
frontend_config = {
    "videoConfig": {
        "aspectRatio": "instagram_feed",
        "imageDuration": 5,
        "totalDuration": 25,
        "transitionDuration": 1
    },
    "visualEffects": {
        "colorGrading": {
            "enabled": False,
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "warmth": 0
        },
        "kenBurns": {
            "enabled": True,
            "zoomRatio": 0.8,
            "direction": "zoom_in"
        },
        "overlays": {
            "faceOverlay": True,
            "particles": True,
            "vignette": True
        },
        "transitions": {
            "type": "slide",
            "duration": 1,
            "intensity": 0.5
        }
    },
    "textStyles": {
        "animation": "fade_in",
        "baseColor": "#ffffff",
        "borderColor": "#ffa800",
        "borderWidth": 4,
        "enabled": True,
        "fontFamily": "Arial",
        "fontSize": 150,
        "highlightColor": "#ffa800",
        "highlightTextColor": "#ad0000",
        "maxWords": 5,
        "padding": 16,
        "position": "bottom"
    },
    "audioSettings": {
        "audioEffects": "none",
        "backgroundMusic": False,
        "musicVolume": 0.3,
        "synchronization": "word_level",
        "voiceVolume": 1
    }
}

print("="*70)
print("🔍 DEBUGGING VIDEO EFFECTS CONFIG EXTRACTION")
print("="*70)

# Simulate the extraction logic from video_builder.py
video_config = frontend_config.get('videoConfig', {})
visual_effects = frontend_config.get('visualEffects', {})
text_styles = frontend_config.get('textStyles', {})
audio_settings = frontend_config.get('audioSettings', {})

print("\n📦 EXTRACTED VALUES:")
print("-"*70)

# Video Configuration
aspect_ratio = video_config.get('aspectRatio', 'youtube_short')
image_duration = video_config.get('imageDuration', 5)
transition_duration = video_config.get('transitionDuration', 1)

print(f"✅ aspect_ratio: {aspect_ratio}")
print(f"✅ image_duration: {image_duration}")
print(f"✅ transition_duration (from videoConfig): {transition_duration}")

# Visual Effects - Transitions
transition_type = visual_effects.get('transitions', {}).get('type', 'crossfade')
transition_intensity = visual_effects.get('transitions', {}).get('intensity', 0.5)
transition_duration_effect = visual_effects.get('transitions', {}).get('duration', 1.0)

print(f"✅ transition_type: {transition_type}")
print(f"✅ transition_intensity: {transition_intensity}")
print(f"⚠️  transition_duration_effect (from visualEffects): {transition_duration_effect}")

# Visual Effects - Ken Burns
ken_burns_enabled = visual_effects.get('kenBurns', {}).get('enabled', True)
ken_burns_zoom = visual_effects.get('kenBurns', {}).get('zoomRatio', 0.8)
ken_burns_direction = visual_effects.get('kenBurns', {}).get('direction', 'zoom_in')

print(f"✅ ken_burns_enabled: {ken_burns_enabled}")
print(f"✅ ken_burns_zoom: {ken_burns_zoom}")
print(f"✅ ken_burns_direction: {ken_burns_direction}")

# Visual Effects - Overlays
face_overlay_enabled = visual_effects.get('overlays', {}).get('faceOverlay', True)
particles_enabled = visual_effects.get('overlays', {}).get('particles', False)
vignette_enabled = visual_effects.get('overlays', {}).get('vignette', False)

print(f"✅ face_overlay_enabled: {face_overlay_enabled}")
print(f"✅ particles_enabled: {particles_enabled}")
print(f"✅ vignette_enabled: {vignette_enabled}")

# Visual Effects - Color Grading
color_grading_enabled = visual_effects.get('colorGrading', {}).get('enabled', False)
brightness = visual_effects.get('colorGrading', {}).get('brightness', 0)
contrast = visual_effects.get('colorGrading', {}).get('contrast', 0)
saturation = visual_effects.get('colorGrading', {}).get('saturation', 0)
warmth = visual_effects.get('colorGrading', {}).get('warmth', 0)

print(f"✅ color_grading_enabled: {color_grading_enabled}")
print(f"   brightness: {brightness}")
print(f"   contrast: {contrast}")
print(f"   saturation: {saturation}")
print(f"   warmth: {warmth}")

# Text Styles
text_enabled = text_styles.get('enabled', True)
font_family = text_styles.get('fontFamily', 'Arial')
font_size = text_styles.get('fontSize', 150)
base_color = text_styles.get('baseColor', '#ffffff')
highlight_color = text_styles.get('highlightColor', '#ffa800')
border_color = text_styles.get('borderColor', '#ffa800')
border_width = text_styles.get('borderWidth', 4)
animation = text_styles.get('animation', 'fade_in')
position = text_styles.get('position', 'bottom')

print(f"✅ text_enabled: {text_enabled}")
print(f"   font_family: {font_family}")
print(f"   font_size: {font_size}")
print(f"   base_color: {base_color}")
print(f"   highlight_color: {highlight_color}")
print(f"   border_color: {border_color}")

# Aspect ratio dimensions
aspect_ratio_dimensions = {
    'youtube_short': (1080, 1920),
    'instagram_story': (1080, 1920),
    'instagram_feed': (1080, 1080),
    'facebook': (1200, 630),
}
video_width, video_height = aspect_ratio_dimensions.get(aspect_ratio, (1080, 1920))

print(f"✅ video_width: {video_width}")
print(f"✅ video_height: {video_height}")

print("\n" + "="*70)
print("⚠️  POTENTIAL ISSUES DETECTED:")
print("="*70)

issues = []

# Check which transition duration is being used
if transition_duration != transition_duration_effect:
    issues.append(f"❌ MISMATCH: videoConfig.transitionDuration ({transition_duration}) != visualEffects.transitions.duration ({transition_duration_effect})")
    issues.append(f"   Currently using: {transition_duration} (from videoConfig)")
    issues.append(f"   Should probably use: {transition_duration_effect} (from visualEffects slider)")
else:
    print("✅ Transition durations match")

# Check if advanced features are enabled but not applied
if color_grading_enabled:
    issues.append(f"⚠️  Color grading is ENABLED but not yet implemented in video generation")

if particles_enabled:
    issues.append(f"⚠️  Particles are ENABLED but not yet implemented in video generation")

if vignette_enabled:
    issues.append(f"⚠️  Vignette is ENABLED but not yet implemented in video generation")

if animation != 'fade_in':
    issues.append(f"⚠️  Text animation '{animation}' selected but only 'fade_in' is implemented")

if base_color != '#ffffff' or highlight_color != '#ffa800':
    issues.append(f"⚠️  Custom text colors selected but not yet applied in video generation")

if border_color != '#ffa800' or border_width != 4:
    issues.append(f"⚠️  Custom text borders selected but not yet applied in video generation")

if transition_type in ['slide', 'zoom', 'dissolve']:
    issues.append(f"⚠️  Transition type '{transition_type}' selected but falls back to 'crossfade' (MoviePy limitation)")

if not issues:
    print("✅ No issues detected! All selected features are implemented.")
else:
    for issue in issues:
        print(issue)

print("\n" + "="*70)
print("🎬 WHAT WILL BE PASSED TO add_transitions_with_config():")
print("="*70)
print(f"   clips: [<video clips>]")
print(f"   image_duration: {image_duration}")
print(f"   transition_duration: {transition_duration}  ⚠️ Should this be {transition_duration_effect}?")
print(f"   transition_type: {transition_type}")
print(f"   ken_burns_enabled: {ken_burns_enabled}")
print(f"   ken_burns_zoom: {ken_burns_zoom}")
print(f"   ken_burns_direction: {ken_burns_direction}")

print("\n" + "="*70)
print("📋 SUMMARY:")
print("="*70)
print(f"✅ Config extracted successfully")
print(f"✅ Video will be: {video_width}x{video_height} ({aspect_ratio})")
print(f"✅ Each image will show for: {image_duration} seconds")
print(f"✅ Transitions will take: {transition_duration} seconds")
print(f"✅ Transition type: {transition_type} (falls back to crossfade)")
print(f"✅ Ken Burns effect: {'Enabled' if ken_burns_enabled else 'Disabled'} (zoom: {ken_burns_zoom})")
print(f"✅ Face overlay: {'Enabled' if face_overlay_enabled else 'Disabled'}")
print(f"✅ Text overlay: {'Enabled' if text_enabled else 'Disabled'}")
print(f"⏳ Color grading: {'Enabled but NOT APPLIED' if color_grading_enabled else 'Disabled'}")
print(f"⏳ Particles: {'Enabled but NOT APPLIED' if particles_enabled else 'Disabled'}")
print(f"⏳ Vignette: {'Enabled but NOT APPLIED' if vignette_enabled else 'Disabled'}")

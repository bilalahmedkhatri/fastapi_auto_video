from PIL import Image
from moviepy import *
from moviepy.video.fx import CrossFadeIn, CrossFadeOut
from moviepy.audio.io.AudioFileClip import AudioFileClip
from tools.utils import FileDirectory
from pathlib import Path
import random
import math
from typing import Optional
import numpy
BASE_DIR = Path(__file__).resolve().parent
file_directory = FileDirectory()

# Video configuration
TARGET_SIZE = {
    "youtube": (1920, 1080),
    "instagram_feed": (1080, 1080),
    "instagram_story": (1080, 1920),
    "facebook": (1200, 630)
}
CURRENT_SIZE = TARGET_SIZE["instagram_story"]
IMAGE_VIEW_DURATION = 2  # seconds per image
TRANSITION_DURATION = 1  # seconds between images
ZOOM_INTENSITY = 0.08  # 8% zoom effect

def calculate_total_duration(image_count):
    """Calculate video duration based on number of images and transitions"""
    return (image_count * IMAGE_VIEW_DURATION) - ((image_count - 1) * TRANSITION_DURATION)

def zoom_in_effect(clip, zoom_ratio=0.09):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS) # type: ignore

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS) # type: ignore

        result = numpy.array(img)
        img.close()

        return result

    return clip.transform(effect)

def fit_to_screen(clip):
    """Resize image to fill screen with aspect ratio preservation"""
    target_w, target_h = CURRENT_SIZE
    scale = max(target_w / clip.w, target_h / clip.h)
    print('scale', scale)
    # return clip.with_effects([vfx.Resize(scale)]).with_position('center')
    return clip.resized(scale).with_position('center')

def create_transition_clips(images):
    """Generate clips with proper transitions using MoviePy 2.x syntax"""
    clips = []
    for i, clip in enumerate(images):
        print(i, 'clip', type(clip), clip)
        # Process base clip
        composite = CompositeVideoClip([
            ColorClip(
                size=CURRENT_SIZE,
                color=(0, 0, 0),
                duration=IMAGE_VIEW_DURATION),
            fit_to_screen(clip.with_duration(IMAGE_VIEW_DURATION)),
            zoom_in_effect(clip)
        ]).with_start(i * (IMAGE_VIEW_DURATION - TRANSITION_DURATION))
        if i > 0:
            composite = composite.with_effects([
                CrossFadeIn(TRANSITION_DURATION),
                CrossFadeOut(TRANSITION_DURATION)
            ])

        
        clips.append(composite)
    
    return clips


def create_face_overlay(total_duration: int) -> Optional[VideoClip]:
    """Create animated face overlay with proper clip creation."""
    face_image_paths = file_directory.get_image_files(
        BASE_DIR.joinpath('media', 'faces'))
    if not face_image_paths:
        return None

    try:
        print('face overlay ', type(face_image_paths))
        random_face_image_path = random.choice(face_image_paths)
        print('wih randome face overlay ', type(face_image_paths))
        
        return (
            random_face_image_path
            .resized(height=400)
            .with_position(('right', 'bottom'))
            # .with_effects([CrossFadeIn(1), CrossFadeOut(1)])
            .with_duration(total_duration)
        )
    except Exception as e:
        print(f"Face overlay error: {e}")
        return None

def main():
    """Main processing function with proper resource handling"""
    clips = []
    
    try:
        # Load and process images
        image_paths = file_directory.get_image_files(BASE_DIR.joinpath('media', 'image'))
        if not image_paths:
            raise ValueError("No images found in media/image directory")
        
        
        # Process clips with transitions
        final_clips = create_transition_clips(image_paths)
        clips.extend(final_clips)
        
        # Create main video
        main_video = CompositeVideoClip(final_clips, size=CURRENT_SIZE)

        # Add face overlay
        face_clip = create_face_overlay(main_video.duration)
        if face_clip:
            clips.append(face_clip)
            main_video = CompositeVideoClip([main_video, face_clip])

        # Add audio
        audio_paths = file_directory.get_audio_files(BASE_DIR.joinpath('media', 'audio'), load_clips=False)
        if audio_paths:
            audio_clip = AudioFileClip(random.choice(audio_paths)).with_duration(main_video.duration)
            clips.append(audio_clip)
            main_video = main_video.with_audio(audio_clip)

        # Export video
        output_name = f"output_{random.choices('abcdefghijklmnopqrstuvwxyz', k=3)[0]}.mp4"
        main_video.write_videofile(
            output_name,
            fps=15,
            codec="libx264",
            preset='fast'
        )
        print(f"Successfully created {output_name}")

    finally:
        for clip in clips:
            try:
                if hasattr(clip, 'close'):
                    clip.close()
            except Exception as e:
                print(f"Error closing clip: {e}")

if __name__ == "__main__":
    main()
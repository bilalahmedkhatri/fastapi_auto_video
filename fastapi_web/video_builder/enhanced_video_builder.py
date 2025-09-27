import random, math, json, asyncio, sys, logging, os
import numpy as np
from pathlib import Path
from PIL import Image
from moviepy import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip, TextClip
from moviepy.video.fx import CrossFadeIn, CrossFadeOut, Resize
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Import the new script generator
from script_generator import ScriptGenerator, ScriptOption, ScriptType

# Created functions (existing imports)
from utils import FileDirectory
from whiper_X_transcription import WhisperTranscriber
from ai_apis.voice_gen_api import download_voice_replicate
from ai_apis.youtube_api import async_upload_video_to_youtube
from ai_apis.text_gen_api import TextGenAPI
from ai_apis.pixabay_api import get_images_videos
from ai_apis.api_utils import ErrorLogger
from ai_audio import AudioManager
from apis.google_search_api import google_image_search, download_images

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
file_directory = FileDirectory()

# Video configuration (keeping existing settings)
TARGET_SIZE = {
    "youtube_short": (1920, 1080),
    "instagram_feed": (1080, 1080),
    "instagram_story": (1080, 1920),
    "facebook": (1200, 630)
}
CURRENT_SIZE = TARGET_SIZE["youtube_short"]
IMAGE_VIEW_DURATION = 5
TRANSITION_DURATION = 1
ZOOM_RATIO = 0.80

class EnhancedVideoBuilder:
    """Enhanced video builder with script generation capabilities"""
    
    def __init__(self):
        self.script_generator = ScriptGenerator()
        self.text_gen_api = TextGenAPI()
        self.clips_to_close = []
        
    def generate_script_options(
        self,
        user_prompt: str,
        script_types: list[ScriptType] = None,
        voiceover_language: str = "English",
        category: str = "General",
        user: str = "unknown"
    ) -> list[ScriptOption]:
        """Generate multiple script options for user selection"""
        
        if script_types is None:
            script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
        
        logging.info(f"Generating {len(script_types)} script options for: {user_prompt}")
        
        scripts = self.script_generator.generate_multiple_scripts(
            user_prompt=user_prompt,
            script_types=script_types,
            voiceover_language=voiceover_language,
            category=category,
            user=user
        )
        
        return scripts
    
    def display_script_options(self, scripts: list[ScriptOption]) -> None:
        """Display script options to user for selection"""
        
        print("\n" + "="*60)
        print("🎬 GENERATED SCRIPT OPTIONS")
        print("="*60)
        
        for i, script in enumerate(scripts, 1):
            print(f"\n--- Option {i}: {script.script_type.value.upper()} ---")
            print(f"📰 Title: {script.title}")
            print(f"⏱️  Duration: {script.duration_estimate}")
            print(f"📝 Word Count: {script.word_count} words")
            print(f"🏷️  Tags: {', '.join(script.tags[:5])}")
            print(f"📄 Script Preview:")
            
            # Show first 200 characters of script
            preview = script.voiceover_script[:200]
            if len(script.voiceover_script) > 200:
                preview += "..."
            print(f"   {preview}")
            print("-" * 50)
    
    def get_user_script_selection(self, scripts: list[ScriptOption]) -> tuple[ScriptOption, bool, bool]:
        """
        Get user's script selection with options to regenerate or edit
        
        Returns:
            tuple: (selected_script, should_regenerate, should_edit)
        """
        
        while True:
            print(f"\nSelect an option:")
            
            # Display script selection options
            for i, script in enumerate(scripts, 1):
                print(f"{i}. {script.script_type.value.upper()} - {script.title[:50]}...")
            
            print(f"{len(scripts) + 1}. 🔄 Regenerate all scripts")
            print(f"{len(scripts) + 2}. ✏️ Edit a script")
            print(f"{len(scripts) + 3}. 🔀 Merge multiple scripts")
            
            try:
                choice = input(f"\nEnter your choice (1-{len(scripts) + 3}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(scripts):
                    # User selected a script
                    selected_script = scripts[choice_num - 1]
                    print(f"\n✅ Selected: {selected_script.title}")
                    return selected_script, False, False
                    
                elif choice_num == len(scripts) + 1:
                    # User wants to regenerate
                    return None, True, False
                    
                elif choice_num == len(scripts) + 2:
                    # User wants to edit a script
                    return None, False, True
                    
                elif choice_num == len(scripts) + 3:
                    # User wants to merge scripts
                    return self.handle_script_merge(scripts), False, False
                    
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def handle_script_editing(self, scripts: list[ScriptOption]) -> ScriptOption:
        """Handle script editing workflow"""
        
        print("\nWhich script would you like to edit?")
        for i, script in enumerate(scripts, 1):
            print(f"{i}. {script.script_type.value.upper()} - {script.title[:50]}...")
        
        while True:
            try:
                choice = int(input(f"Enter script number (1-{len(scripts)}): "))
                if 1 <= choice <= len(scripts):
                    script_to_edit = scripts[choice - 1]
                    break
                else:
                    print("❌ Invalid choice.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Get edit instructions
        print(f"\n📝 Selected script: {script_to_edit.title}")
        print(f"Current script preview: {script_to_edit.voiceover_script[:200]}...")
        
        edit_instructions = input("\nEnter your editing instructions: ").strip()
        
        if not edit_instructions:
            print("❌ No edit instructions provided.")
            return script_to_edit
        
        print("\n🔄 Editing script...")
        edited_script = self.script_generator.edit_script(
            script_option=script_to_edit,
            edit_instructions=edit_instructions,
            user="interactive_user"
        )
        
        if edited_script:
            print("✅ Script edited successfully!")
            print(f"Updated preview: {edited_script.voiceover_script[:200]}...")
            return edited_script
        else:
            print("❌ Failed to edit script. Using original.")
            return script_to_edit
    
    def handle_script_merge(self, scripts: list[ScriptOption]) -> ScriptOption:
        """Handle script merging workflow"""
        
        print("\nSelect scripts to merge (enter numbers separated by commas):")
        for i, script in enumerate(scripts, 1):
            print(f"{i}. {script.script_type.value.upper()} - {script.title[:50]}...")
        
        while True:
            try:
                choices = input("Enter script numbers (e.g., 1,3): ").strip()
                indices = [int(x.strip()) - 1 for x in choices.split(",")]
                
                if len(indices) < 2:
                    print("❌ Please select at least 2 scripts to merge.")
                    continue
                
                if all(0 <= i < len(scripts) for i in indices):
                    scripts_to_merge = [scripts[i] for i in indices]
                    break
                else:
                    print("❌ Invalid script numbers.")
            except ValueError:
                print("❌ Please enter valid numbers separated by commas.")
        
        # Get merge instructions
        merge_instructions = input("\nEnter merge instructions (optional): ").strip()
        
        print(f"\n🔄 Merging {len(scripts_to_merge)} scripts...")
        merged_script = self.script_generator.merge_scripts(
            script_options=scripts_to_merge,
            merge_instructions=merge_instructions,
            user="interactive_user"
        )
        
        if merged_script:
            print("✅ Scripts merged successfully!")
            print(f"Merged script preview: {merged_script.voiceover_script[:200]}...")
            return merged_script
        else:
            print("❌ Failed to merge scripts. Please try again.")
            return scripts[0]  # Return first script as fallback
    
    def create_video_from_script(
        self,
        selected_script: ScriptOption,
        voice: str = "am_puck",
        num_images: int = 15
    ) -> Optional[str]:
        """Create video using the selected script"""
        
        try:
            # Convert ScriptOption to ai_data format expected by existing functions
            ai_data = {
                "title": selected_script.title,
                "description": selected_script.description, 
                "voiceover_script": selected_script.voiceover_script,
                "tags": selected_script.tags,
                "category": selected_script.category,
                "language": selected_script.language
            }
            
            logging.info(f"Creating video from selected script: {selected_script.title}")
            
            # Generate voiceover
            ai_gen_file_path = str(
                BASE_DIR / f"ai_voice_gen_{''.join(random.choices('123456789', k=3))}.mp3"
            )
            
            replicate_audio_dir = asyncio.run(download_voice_replicate(
                text=selected_script.voiceover_script,
                output_path=ai_gen_file_path,
                voice=voice
            ))
            
            if not replicate_audio_dir:
                logging.error("Failed to generate voiceover")
                return None
            
            # Transcribe audio for word-level timing
            transcriber = WhisperTranscriber(language="en")
            voice_segments = transcriber.transcribe_audio_to_json(
                replicate_audio_dir, max_words=5
            )
            
            # Download images
            google_image_paths = self.download_google_images(ai_data, num_images)
            image_paths = google_image_paths
            
            # Fallback to local images if needed
            if len(image_paths) < 5:
                local_image_paths = file_directory.get_image_files(
                    BASE_DIR.joinpath('media', 'bikes_test'), load_clips=False
                )
                if local_image_paths:
                    needed_images = 8 - len(image_paths)
                    image_paths.extend(local_image_paths[:needed_images])
            
            if not image_paths:
                logging.error("No images found")
                return None
            
            # Create video clips
            raw_clips = self.create_image_clips(image_paths)
            if not raw_clips:
                logging.error("Failed to create image clips")
                return None
            
            # Get audio duration and add transitions
            audio_duration = AudioManager.get_audio_duration(replicate_audio_dir)
            final_clips = self.add_transitions(raw_clips)
            
            # Create main video composite
            main_video = CompositeVideoClip(final_clips, size=CURRENT_SIZE)
            self.clips_to_close.append(main_video)
            
            # Add overlays (face, text)
            overlays = []
            
            # Add face overlay
            face_clip = self.add_face_overlay(audio_duration)
            if face_clip:
                overlays.append(face_clip.with_layer(1))
                self.clips_to_close.append(face_clip)
            
            # Add text overlays
            if voice_segments and "segments" in voice_segments:
                font_style = BASE_DIR / 'fonts/opensans/opensans.ttf'
                word_clips = self.create_first5_words_highlighted_clips(
                    voice_segments["segments"], size=CURRENT_SIZE, font=str(font_style)
                )
                overlays.extend(word_clips)
                self.clips_to_close.extend(word_clips)
            
            # Final composition
            main_video = CompositeVideoClip([*final_clips, *overlays], size=CURRENT_SIZE)
            
            # Add audio
            audio_clip = AudioFileClip(replicate_audio_dir)
            audio_clip = audio_clip.with_duration(audio_duration)
            self.clips_to_close.extend([main_video, audio_clip])
            
            final = main_video.with_audio(audio_clip)
            
            # Export video
            output_name = f"output_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))}.mp4"
            output_path = str(BASE_DIR / output_name)
            
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
            
            # Upload to YouTube
            asyncio.run(self.upload_to_youtube(output_path, ai_data))
            
            return output_path
            
        except Exception as e:
            logging.error(f"Error creating video: {e}")
            return None
        finally:
            self.cleanup_clips()
    
    def download_google_images(self, ai_data: Dict, num_images: int = 15) -> list[str]:
        """Download images from Google Search - copied from original"""
        try:
            api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
            cse_id = os.getenv("GOOGLE_SEARCH_ENGINE")
            
            if not api_key or not cse_id:
                logging.warning("Google API credentials not found.")
                return []
            
            # Generate search query
            search_prompt = f"""
            Generate a concise image search query for: {ai_data.get('title', '')} {ai_data.get('description', '')}
            """
            
            search_query = self.text_gen_api.generate_search_query(search_prompt)
            if not search_query:
                return []
            
            image_urls = google_image_search(
                api_key=api_key,
                cse_id=cse_id,
                search_ai_query=search_query,
                num_results=num_images
            )
            
            if not image_urls:
                return []
            
            query_short = " ".join(search_query.split()[:3])
            downloaded_paths = download_images(
                image_urls=image_urls,
                query=query_short,
                subdir="google_search_temp"
            )
            
            return downloaded_paths
            
        except Exception as e:
            logging.error(f"Error downloading Google images: {e}")
            return []
    
    def create_image_clips(self, image_paths: list[str]) -> list:
        """Create image clips from paths - copied from original"""
        raw_clips = []
        for p in image_paths:
            try:
                img_clip = ImageClip(p)
                img_clip = self.fit_to_screen(img_clip)
                base_clip = self.create_base_composite_clip(
                    img_clip,
                    duration=IMAGE_VIEW_DURATION,
                    background_color=(0, 0, 0),
                    overlays=None,
                    size=CURRENT_SIZE
                )
                raw_clips.append(base_clip)
                self.clips_to_close.extend([img_clip, base_clip])
            except Exception as e:
                logging.error(f"Error processing image {p}: {e}")
        return raw_clips
    
    def cleanup_clips(self):
        """Clean up all clips"""
        for clip in self.clips_to_close:
            try:
                if hasattr(clip, 'close'):
                    clip.close()
            except Exception as e:
                logging.error(f"Error closing clip: {e}")
        self.clips_to_close.clear()
    
    # Copy necessary methods from original video_builder.py
    def fit_to_screen(self, clip, min_zoom=1.0):
        """Resize image to fill screen with aspect ratio preservation"""
        target_w, target_h = CURRENT_SIZE
        scale = max(target_w / clip.w, target_h / clip.h) * min_zoom
        return clip.resized(scale).with_position('center')
    
    def create_base_composite_clip(self, image_clip, duration, background_color=(0, 0, 0), overlays=None, size=CURRENT_SIZE):
        """Create a base composite video clip"""
        try:
            main_image = image_clip.with_position('center').with_duration(duration)
            background = ColorClip(size=size, color=background_color, duration=duration)
            layers = [background, main_image]
            if overlays:
                layers.extend(overlays)
            return CompositeVideoClip(layers, size=size).with_duration(duration)
        except Exception as e:
            logging.error(f"Error creating base composite clip: {e}")
            return image_clip.with_duration(duration)
    
    def add_transitions(self, clips):
        """Add crossfade transitions between clips"""
        # Implementation from original video_builder.py
        if len(clips) <= 1:
            return clips

        final_clips = []

        for i, clip in enumerate(clips):
            try:
                start_time = i * (IMAGE_VIEW_DURATION - TRANSITION_DURATION)
                processed_clip = clip.with_start(start_time).with_duration(IMAGE_VIEW_DURATION)

                if ZOOM_RATIO >= 0.01:
                    try:
                        processed_clip = self.add_ken_burns_effect(processed_clip, ZOOM_RATIO)
                    except Exception as e:
                        logging.error(f"Warning: Could not apply Ken Burns effect to clip {i+1}: {e}")

                effects = []
                if i > 0:
                    effects.append(CrossFadeIn(TRANSITION_DURATION))
                if i < len(clips) - 1:
                    effects.append(CrossFadeOut(TRANSITION_DURATION))

                if effects:
                    try:
                        processed_clip = processed_clip.with_effects(effects)
                    except Exception as e:
                        logging.error(f"Warning: Could not apply crossfade to clip {i+1}: {e}")

                final_clips.append(processed_clip)
            except Exception as e:
                logging.error(f"Error processing clip {i+1}: {e}")

        return final_clips
    
    def add_ken_burns_effect(self, clip, zoom_ratio):
        """Apply Ken Burns (zoom) effect to a clip"""
        # Implementation from original video_builder.py
        def effect_func(get_frame, t):
            frame = get_frame(t)
            img = Image.fromarray(frame)
            base_size = img.size

            zoom_factor = 1 + (zoom_ratio * t / clip.duration)
            new_size = [
                math.ceil(img.size[0] * zoom_factor),
                math.ceil(img.size[1] * zoom_factor)
            ]

            new_size[0] = new_size[0] + (new_size[0] % 2)
            new_size[1] = new_size[1] + (new_size[1] % 2)

            img = img.resize(new_size, Image.Resampling.LANCZOS)
            x = math.ceil((new_size[0] - base_size[0]) / 2)
            y = math.ceil((new_size[1] - base_size[1]) / 2)
            img = img.crop((x, y, x + base_size[0], y + base_size[1])).resize(base_size, Image.Resampling.LANCZOS)

            result = np.array(img)
            img.close()
            return result

        try:
            return clip.transform(effect_func)
        except Exception as e:
            logging.error(f"Error applying Ken Burns effect: {e}")
            return clip
    
    def add_face_overlay(self, audio_duration):
        """Add animated face overlay"""
        # Implementation from original video_builder.py
        face_paths = file_directory.get_image_files(
            BASE_DIR.joinpath('media', 'faces'), load_clips=False)
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
    
    def create_first5_words_highlighted_clips(self, transcript, size=CURRENT_SIZE, font_size=100, **kwargs):
        """Create highlighted text clips - simplified version of original"""
        # This is a simplified version - you can copy the full implementation from original
        clips = []
        try:
            for seg in transcript:
                words = seg.get('words', [])[:5]
                if not words:
                    continue
                    
                phrase = ' '.join([w['text'] for w in words])
                seg_start = words[0]['start']
                seg_end = words[-1]['end']
                
                text_clip = TextClip(
                    text=phrase,
                    font_size=font_size,
                    color='white',
                    method='caption',
                    size=(size[0]-40, None)
                ).with_start(seg_start).with_duration(seg_end-seg_start).with_position(('center', 'top'))
                
                clips.append(text_clip)
        except Exception as e:
            logging.error(f"Error creating text clips: {e}")
            
        return clips
    
    async def upload_to_youtube(self, video_path: str, ai_data: Dict):
        """Upload video to YouTube"""
        try:
            response = await async_upload_video_to_youtube(
                video_path,
                title=ai_data["title"],
                description=ai_data["description"],
                tags=ai_data["tags"],
            )
            if response and 'id' in response:
                logging.info(f"Watch it at: https://youtu.be/{response['id']}")
                return response['id']
            else:
                logging.error("Upload failed or no video ID returned.")
                return None
        except Exception as e:
            logging.error(f"Error uploading video to YouTube: {e}")
            return None


def interactive_video_creation():
    """Interactive video creation with script selection"""
    
    builder = EnhancedVideoBuilder()
    
    print("🎬 Enhanced Video Creator with Script Options")
    print("=" * 50)
    
    # Get user input
    user_prompt = input("Enter your video topic/prompt: ").strip()
    if not user_prompt:
        print("❌ Please provide a valid topic.")
        return
    
    # Optional: Let user select script types
    print("\nAvailable script types:")
    for i, script_type in enumerate(ScriptType, 1):
        print(f"{i}. {script_type.value.replace('_', ' ').title()}")
    
    type_choice = input("Enter script type numbers (comma-separated) or press Enter for default: ").strip()
    
    if type_choice:
        try:
            indices = [int(x.strip()) - 1 for x in type_choice.split(",")]
            script_types = [list(ScriptType)[i] for i in indices if 0 <= i < len(ScriptType)]
        except (ValueError, IndexError):
            script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
    else:
        script_types = [ScriptType.SHORT, ScriptType.MEDIUM, ScriptType.LONG]
    
    # Get additional parameters
    category = input("Enter category (or press Enter for 'General'): ").strip() or "General"
    language = input("Enter language (or press Enter for 'English'): ").strip() or "English"
    
    # Generate scripts
    while True:
        print(f"\n🔄 Generating {len(script_types)} script options...")
        scripts = builder.generate_script_options(
            user_prompt=user_prompt,
            script_types=script_types,
            voiceover_language=language,
            category=category,
            user="interactive_user"
        )
        
        if not scripts:
            print("❌ Failed to generate scripts. Please try again with a different prompt.")
            return
        
        # Display options
        builder.display_script_options(scripts)
        
        # Get user selection
        selected_script, should_regenerate, should_edit = builder.get_user_script_selection(scripts)
        
        if should_regenerate:
            print("\n🔄 Regenerating scripts...")
            scripts = builder.script_generator.regenerate_scripts(
                user_prompt=user_prompt,
                script_types=script_types,
                voiceover_language=language,
                category=category,
                user="interactive_user"
            )
            continue
            
        elif should_edit:
            selected_script = builder.handle_script_editing(scripts)
            
        if selected_script:
            break
    
    # Create video
    print(f"\n🎬 Creating video from selected script: {selected_script.title}")
    
    voice = input("Enter voice name (or press Enter for 'am_puck'): ").strip() or "am_puck"
    
    output_path = builder.create_video_from_script(
        selected_script=selected_script,
        voice=voice
    )
    
    if output_path:
        print(f"\n✅ Video created successfully: {output_path}")
    else:
        print("\n❌ Failed to create video.")


def main():
    """Enhanced main function with script selection"""
    interactive_video_creation()


if __name__ == "__main__":
    main()

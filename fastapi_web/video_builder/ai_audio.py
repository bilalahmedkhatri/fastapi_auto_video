from moviepy import AudioFileClip

class AudioManager:
    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """Return the duration of an audio file in seconds."""
        try:
            with AudioFileClip(audio_path) as audio_clip:
                return audio_clip.duration
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0

    @staticmethod
    def load_audio_clip(audio_path: str, duration: float = None):
        """Load an audio file and optionally trim to duration."""
        try:
            audio_clip = AudioFileClip(audio_path)
            if duration:
                audio_clip = audio_clip.with_duration(duration)
            return audio_clip
        except Exception as e:
            print(f"Error loading audio: {e}")
            return None
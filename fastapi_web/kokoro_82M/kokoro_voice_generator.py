"""
Kokoro-82M Voice Generation Module - Backward Compatibility Wrapper

This module provides backward compatibility by wrapping the new modular architecture.
For new code, import directly from: from kokoro_82M.generators import KokoroVoiceGenerator

Author: Auto Video Generator Team
Date: 2025-11-12 (Refactored from 557 lines to 85 lines)
"""

try:
    from .generators import KokoroVoiceGenerator
    from .config import KOKORO_CONFIG, AUDIO_CONFIG, FILE_CONFIG
except ImportError:
    # Standalone execution
    from generators import KokoroVoiceGenerator
    from config import KOKORO_CONFIG, AUDIO_CONFIG, FILE_CONFIG

# Voice metadata constants (for backward compatibility only)
# NOTE: In production, voice catalog should be managed in SelectAIVoices database table
# These constants are kept here only for existing code that references them

SUPPORTED_VOICES = [
    "af_sarah", "af_nicole", "af_bella", "af_jessica", "af_april", "af_diana",
    "am_michael", "am_david", "am_john", "am_eric", "am_aaron", "am_andrew",
    "bf_emma", "bf_grace",
    "bm_lewis", "bm_oliver",
]

VOICE_METADATA = {
    "af_sarah": {"name": "Sarah", "gender": "Female", "accent": "American", "age": "Young Adult"},
    "af_nicole": {"name": "Nicole", "gender": "Female", "accent": "American", "age": "Adult"},
    "af_bella": {"name": "Bella", "gender": "Female", "accent": "American", "age": "Young Adult"},
    "af_jessica": {"name": "Jessica", "gender": "Female", "accent": "American", "age": "Adult"},
    "af_april": {"name": "April", "gender": "Female", "accent": "American", "age": "Young Adult"},
    "af_diana": {"name": "Diana", "gender": "Female", "accent": "American", "age": "Adult"},
    "am_michael": {"name": "Michael", "gender": "Male", "accent": "American", "age": "Adult"},
    "am_david": {"name": "David", "gender": "Male", "accent": "American", "age": "Middle-Aged"},
    "am_john": {"name": "John", "gender": "Male", "accent": "American", "age": "Adult"},
    "am_eric": {"name": "Eric", "gender": "Male", "accent": "American", "age": "Young Adult"},
    "am_aaron": {"name": "Aaron", "gender": "Male", "accent": "American", "age": "Young Adult"},
    "am_andrew": {"name": "Andrew", "gender": "Male", "accent": "American", "age": "Adult"},
    "bf_emma": {"name": "Emma", "gender": "Female", "accent": "British", "age": "Young Adult"},
    "bf_grace": {"name": "Grace", "gender": "Female", "accent": "British", "age": "Adult"},
    "bm_lewis": {"name": "Lewis", "gender": "Male", "accent": "British", "age": "Middle-Aged"},
    "bm_oliver": {"name": "Oliver", "gender": "Male", "accent": "British", "age": "Young Adult"},
}


# Helper functions for backward compatibility
def get_supported_voices():
    """Get list of supported voice types (legacy function)."""
    return SUPPORTED_VOICES.copy()


def get_voice_metadata(voice_type: str):
    """Get metadata for a specific voice (legacy function)."""
    return VOICE_METADATA.get(voice_type.lower(), {})


def validate_voice_type(voice_type: str) -> bool:
    """Validate if voice type is supported (legacy function)."""
    return voice_type.lower() in SUPPORTED_VOICES


# Main entry point for backward compatibility
if __name__ == "__main__":
    # Example usage (same as before)
    generator = KokoroVoiceGenerator()
    
    try:
        audio_path, metadata = generator.generate_voice(
            text="Welcome to Kokoro voice generation system",
            voice_type="af_sarah"
        )
        print(f"✅ Generated: {audio_path}")
        print(f"Duration: {metadata['duration_seconds']:.2f}s")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # List all generated voices
    voices = generator.list_generated_voices()
    print(f"\nTotal generated voices: {len(voices)}")


# Export all public APIs
__all__ = [
    'KokoroVoiceGenerator',
    'SUPPORTED_VOICES',
    'VOICE_METADATA',
    'KOKORO_CONFIG',
    'AUDIO_CONFIG',
    'FILE_CONFIG',
    'get_supported_voices',
    'get_voice_metadata',
    'validate_voice_type',
]

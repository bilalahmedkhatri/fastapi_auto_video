"""
Kokoro-82M Technical Configuration

Technical constants and settings for Kokoro voice generation.
Does NOT contain voice catalog data (managed in database).

Author: Auto Video Generator Team
Date: 2025-11-12
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Technical Configuration
KOKORO_CONFIG = {
    "model_name": "kokoro-82m",
    "provider": "kokoro",
    "sample_rate": 24000,
    "lang_code": "a",  # "a" = English
    "repo_id": "hexgrad/Kokoro-82M",
}

# Audio Processing Settings
AUDIO_CONFIG = {
    "speed_min": 0.5,
    "speed_max": 2.0,
    "speed_default": 1.0,
    "target_db": -20.0,  # Normalization target
    "bit_depth": 16,  # For WAV files
}

# File Management
FILE_CONFIG = {
    "output_dir": BASE_DIR / "media/voice_generated",
    "filename_format": "%Y-%m-%d-%H-%M",  # Timestamp format
    "audio_extension": ".wav",
    "metadata_suffix": "_metadata.json",
}


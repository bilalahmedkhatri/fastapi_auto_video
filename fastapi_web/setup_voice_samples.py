#!/usr/bin/env python3
"""
Script to copy and rename voice files to match our API naming convention
"""

import os
import shutil
from pathlib import Path

def setup_voice_samples():
    """Copy and rename voice samples to match API naming convention"""
    
    source_dir = Path("video_builder/ai_apis/voices_samples/american")
    target_dir = Path("media/voice_samples_real")
    
    # Create target directory
    target_dir.mkdir(exist_ok=True)
    
    # Mapping of voice IDs to actual filenames
    voice_mappings = {
        "af_alloy": "voices_0_af_alloy.wav",
        "af_aoede": "voices_1_af_aoede.wav", 
        "af_bella": "voices_1_af_bella.wav",
        "af_jessica": "voices_1_af_jessica.wav",
        "af_kore": "voices_1_af_kore.wav",
        "af_nicole": "voices_1_af_nicole.wav",
        "af_nova": "voices_1_af_nova.wav",
        "af_river": "voices_1_af_river.wav",
        "af_sarah": "voices_1_af_sarah.wav",
        "af_sky": "voices_1_af_sky.wav",
        "am_adam": "voices_1_am_adam.wav",
        "am_echo": "voices_1_am_echo.wav",
        "am_eric": "voices_1_am_eric.wav",
        "am_fenrir": "voices_1_am_fenrir.wav",
        "am_liam": "voices_1_am_liam.wav",
        "am_michael": "voices_1_am_michael.wav",
        "am_onyx": "voices_1_am_onyx.wav",
        "am_puck": "voices_1_am_puck.wav"
    }
    
    copied_files = 0
    for voice_id, filename in voice_mappings.items():
        source_file = source_dir / filename
        target_file = target_dir / f"{voice_id}.wav"
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                print(f"✓ Copied {filename} -> {voice_id}.wav")
                copied_files += 1
            except Exception as e:
                print(f"✗ Error copying {filename}: {e}")
        else:
            print(f"✗ Source file not found: {filename}")
    
    print(f"\nTotal files copied: {copied_files}")
    print(f"Files available in: {target_dir.absolute()}")
    
    return copied_files

if __name__ == "__main__":
    print("Setting up voice samples for API access...")
    print("=" * 50)
    setup_voice_samples()

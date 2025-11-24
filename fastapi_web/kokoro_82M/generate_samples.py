"""
Generate Voice Samples Script

This script generates voice samples for all available voices using the 
free voiceover API endpoint. The samples are saved in the kokoro_82M/samples directory.

Usage:
    python kokoro_82M/generate_samples.py

Author: Auto Video Generator Team
Date: 2025-11-19
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLE_TEXT = "Hello! This is a sample of my voice. I can help you create amazing voiceovers for your videos and projects."


def create_samples_directory():
    """Create the samples directory if it doesn't exist"""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Samples directory created/verified: {SAMPLES_DIR}")


def get_available_voices() -> List[Dict]:
    """Fetch available voices from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/voiceover/voiceover_samples")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Found {data['total']} voices in the catalog")
        return data['voices']
    except Exception as e:
        print(f"❌ Error fetching voices: {e}")
        return []


def generate_voice_sample(voice_id: str, voice_name: str) -> bool:
    """
    Generate a voice sample using the free voiceover API
    
    Args:
        voice_id: The voice ID (e.g., 'af_sarah')
        voice_name: The display name of the voice (e.g., 'Sarah')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare request payload
        payload = {
            "text": SAMPLE_TEXT,
            "voice_id": voice_id,
            "speed": 1.0
        }
        
        print(f"📝 Generating sample for {voice_name} ({voice_id})...", end=" ")
        
        # Call the free voiceover API
        response = requests.post(
            f"{API_BASE_URL}/api/voiceover/free_tool",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_url = result['audio_url']
            
            # Download the audio file
            audio_response = requests.get(audio_url, timeout=30)
            audio_response.raise_for_status()
            
            # Save to samples directory
            output_file = SAMPLES_DIR / f"{voice_id}_sample.wav"
            output_file.write_bytes(audio_response.content)
            
            # Save metadata
            metadata_file = SAMPLES_DIR / f"{voice_id}_metadata.json"
            metadata = {
                "voice_id": voice_id,
                "voice_name": voice_name,
                "sample_text": SAMPLE_TEXT,
                "duration_seconds": result.get('duration_seconds'),
                "file_size": result.get('file_size'),
                "generated_at": result.get('created_at'),
            }
            metadata_file.write_text(json.dumps(metadata, indent=2))
            
            print(f"✅ Success! ({result.get('file_size', 0)} bytes)")
            return True
            
        elif response.status_code == 429:
            # Rate limit exceeded
            result = response.json()
            print(f"⚠️  Rate limit exceeded. Reset at: {result.get('reset_at')}")
            return False
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def wait_for_rate_limit_reset():
    """Wait for rate limit to reset (12 hours)"""
    print("\n⏳ Rate limit exceeded. You can:")
    print("   1. Wait 12 hours for the rate limit to reset")
    print("   2. Clear your IP's usage from the database")
    print("   3. Continue generating remaining samples later")
    
    response = input("\nDo you want to wait 60 seconds and try again? (y/n): ")
    if response.lower() == 'y':
        print("⏳ Waiting 60 seconds...")
        time.sleep(60)
        return True
    return False


def generate_all_samples():
    """Generate samples for all available voices"""
    print("=" * 70)
    print("🎙️  VOICE SAMPLE GENERATOR")
    print("=" * 70)
    
    # Create samples directory
    create_samples_directory()
    
    # Get available voices from API
    voices = get_available_voices()
    if not voices:
        print("❌ No voices found. Make sure the API server is running!")
        return
    
    # Generate samples
    total = len(voices)
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    print(f"\n📊 Starting generation for {total} voices...")
    print("-" * 70)
    
    for index, voice in enumerate(voices, 1):
        voice_id = voice['voice_id']
        voice_name = voice['voice_name']
        
        # Check if sample already exists
        sample_file = SAMPLES_DIR / f"{voice_id}_sample.wav"
        if sample_file.exists():
            print(f"[{index}/{total}] ⏭️  {voice_name} ({voice_id}) - Already exists, skipping")
            skipped_count += 1
            continue
        
        print(f"[{index}/{total}] ", end="")
        
        success = generate_voice_sample(voice_id, voice_name)
        
        if success:
            success_count += 1
            # Small delay to avoid overwhelming the server
            time.sleep(1)
        else:
            failed_count += 1
            # If rate limited, ask user if they want to wait
            if index < total:
                if not wait_for_rate_limit_reset():
                    print(f"\n⏹️  Stopping. Generated {success_count}/{total} samples.")
                    break
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 GENERATION SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"⏭️  Skipped:    {skipped_count} (already exist)")
    print(f"❌ Failed:     {failed_count}")
    print(f"📁 Saved to:   {SAMPLES_DIR.absolute()}")
    print("=" * 70)
    
    # List generated files
    if success_count > 0:
        print("\n📂 Generated files:")
        for file in sorted(SAMPLES_DIR.glob("*.wav")):
            size_kb = file.stat().st_size / 1024
            print(f"   - {file.name} ({size_kb:.1f} KB)")


def list_samples():
    """List all existing samples in the samples directory"""
    if not SAMPLES_DIR.exists():
        print("❌ Samples directory doesn't exist yet.")
        return
    
    samples = list(SAMPLES_DIR.glob("*.wav"))
    if not samples:
        print("❌ No samples found in directory.")
        return
    
    print(f"\n📂 Found {len(samples)} voice samples:")
    print("-" * 70)
    
    for sample in sorted(samples):
        size_kb = sample.stat().st_size / 1024
        voice_id = sample.stem.replace("_sample", "")
        
        # Try to load metadata
        metadata_file = sample.parent / f"{voice_id}_metadata.json"
        voice_name = voice_id
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
                voice_name = metadata.get('voice_name', voice_id)
            except:
                pass
        
        print(f"   🎤 {voice_name:20} ({voice_id:15}) - {size_kb:6.1f} KB")
    
    print("-" * 70)


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_samples()
    else:
        generate_all_samples()


if __name__ == "__main__":
    main()

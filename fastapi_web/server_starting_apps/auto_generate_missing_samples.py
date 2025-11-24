"""
Auto-generate missing voice samples

This script:
1. Checks all voices in the database
2. Identifies voices without samples (NULL or Replicate URLs)
3. Generates samples for voices that don't have local files
4. Updates the database with correct path URLs

Usage:
    python server_starting_apps/auto_generate_missing_samples.py
    python server_starting_apps/auto_generate_missing_samples.py --check-only
"""
import sys
from pathlib import Path
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from sqlmodel import Session, select
from models.db_models import SelectAIVoices, engine

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SAMPLES_DIR = parent_dir / "media/voice-samples"
KOKORO_SAMPLES_DIR = parent_dir / "kokoro_82M/samples"
SAMPLE_TEXT = "Hello! This is a sample of my voice. I can help you create amazing voiceovers for your videos and projects."


def is_sample_file_exists(voice_id: str) -> tuple[bool, Path]:
    """
    Check if sample file exists in either location
    Returns: (exists, file_path)
    """
    # Check in media/voice-samples
    sample_path = SAMPLES_DIR / f"{voice_id}_sample.wav"
    if sample_path.exists():
        return True, sample_path
    
    # Check in kokoro_82M/samples
    sample_path = KOKORO_SAMPLES_DIR / f"{voice_id}_sample.wav"
    if sample_path.exists():
        return True, sample_path
    
    return False, None


def needs_sample_generation(voice: SelectAIVoices) -> tuple[bool, str]:
    """
    Check if voice needs sample generation
    Returns: (needs_generation, reason)
    """
    # Check if voice_sample_url is NULL or empty
    if not voice.voice_sample_url or voice.voice_sample_url.strip() == "":
        return True, "No URL in database"
    
    # Check if URL points to Replicate (external)
    if "replicate.com" in voice.voice_sample_url:
        # Check if we actually have a local file
        exists, _ = is_sample_file_exists(voice.voice_id)
        if exists:
            return False, "Local file exists, needs URL update"
        return True, "External URL, no local file"
    
    # Check if URL points to non-existent file
    if voice.voice_sample_url.startswith("/api/voice-samples/"):
        filename = voice.voice_sample_url.split("/")[-1]
        file_path = SAMPLES_DIR / filename
        if not file_path.exists():
            return True, "URL points to missing file"
    
    # Check if local file exists
    exists, _ = is_sample_file_exists(voice.voice_id)
    if not exists:
        return True, "No local file found"
    
    return False, "Sample exists"


def generate_voice_sample(voice_id: str, voice_name: str) -> tuple[bool, str, dict]:
    """
    Generate voice sample using the free voiceover API
    Returns: (success, message, data)
    """
    try:
        payload = {
            "text": SAMPLE_TEXT,
            "voice_id": voice_id,
            "speed": 1.0
        }
        
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
            
            # Save to media/voice-samples
            SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
            output_file = SAMPLES_DIR / f"{voice_id}_sample.wav"
            output_file.write_bytes(audio_response.content)
            
            return True, f"Generated successfully ({len(audio_response.content)} bytes)", result
            
        elif response.status_code == 429:
            result = response.json()
            return False, f"Rate limit exceeded. Reset at: {result.get('reset_at')}", {}
            
        else:
            return False, f"API error {response.status_code}: {response.text}", {}
            
    except Exception as e:
        return False, f"Error: {str(e)}", {}


def update_voice_url(session: Session, voice: SelectAIVoices, voice_id: str) -> bool:
    """
    Update voice_sample_url in database
    Returns: success status
    """
    try:
        # Check if file exists
        exists, file_path = is_sample_file_exists(voice_id)
        if not exists:
            return False
        
        # If file is in kokoro_82M/samples, copy to media/voice-samples
        if "kokoro_82M" in str(file_path):
            SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
            target_path = SAMPLES_DIR / f"{voice_id}_sample.wav"
            if not target_path.exists():
                import shutil
                shutil.copy(file_path, target_path)
        
        # Update URL to path only
        new_url = f"/api/voice-samples/{voice_id}_sample.wav"
        voice.voice_sample_url = new_url
        session.add(voice)
        session.commit()
        
        return True
    except Exception as e:
        print(f"   ❌ Error updating URL: {e}")
        return False


def check_missing_samples(check_only=False):
    """
    Check and optionally generate missing voice samples
    """
    session = Session(engine)
    
    # Get all active voices
    voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.is_active == True)
        .order_by(SelectAIVoices.voice_id)
    ).all()
    
    print(f"\n{'='*100}")
    print(f"🔍 VOICE SAMPLE CHECK - Total Active Voices: {len(voices)}")
    print(f"{'='*100}\n")
    
    # Categorize voices
    needs_generation = []
    needs_url_update = []
    has_samples = []
    
    for voice in voices:
        needs_gen, reason = needs_sample_generation(voice)
        
        if needs_gen:
            needs_generation.append((voice, reason))
        else:
            # Check if URL needs update
            exists, file_path = is_sample_file_exists(voice.voice_id)
            if exists and (not voice.voice_sample_url or "replicate.com" in voice.voice_sample_url):
                needs_url_update.append((voice, reason))
            else:
                has_samples.append((voice, reason))
    
    # Display summary
    print(f"📊 Summary:")
    print(f"   ✅ Has samples:        {len(has_samples)}")
    print(f"   🔄 Needs URL update:   {len(needs_url_update)}")
    print(f"   ❌ Needs generation:   {len(needs_generation)}")
    print(f"\n{'='*100}\n")
    
    # Show needs generation
    if needs_generation:
        print(f"❌ Voices needing sample generation ({len(needs_generation)}):")
        print(f"{'─'*100}")
        for voice, reason in needs_generation:
            provider = f"({voice.provider})" if voice.provider else ""
            print(f"   {voice.voice_id:<20} {voice.voice_name:<25} {provider:<15} - {reason}")
        print(f"{'─'*100}\n")
    
    # Show needs URL update
    if needs_url_update:
        print(f"🔄 Voices needing URL update ({len(needs_url_update)}):")
        print(f"{'─'*100}")
        for voice, reason in needs_url_update:
            print(f"   {voice.voice_id:<20} {voice.voice_name:<25} - {reason}")
        print(f"{'─'*100}\n")
    
    if check_only:
        session.close()
        return
    
    # Update URLs first
    if needs_url_update:
        print(f"\n{'='*100}")
        print(f"🔄 UPDATING URLs ({len(needs_url_update)} voices)")
        print(f"{'='*100}\n")
        
        updated_count = 0
        for voice, _ in needs_url_update:
            print(f"📝 {voice.voice_id:<20} {voice.voice_name:<25}...", end=" ")
            if update_voice_url(session, voice, voice.voice_id):
                print("✅ Updated")
                updated_count += 1
            else:
                print("❌ Failed")
        
        print(f"\n✅ Updated {updated_count}/{len(needs_url_update)} URLs\n")
    
    # Generate missing samples
    if needs_generation:
        print(f"\n{'='*100}")
        print(f"🎙️  GENERATING SAMPLES ({len(needs_generation)} voices)")
        print(f"{'='*100}\n")
        
        success_count = 0
        failed_count = 0
        rate_limited = False
        
        for index, (voice, reason) in enumerate(needs_generation, 1):
            print(f"[{index}/{len(needs_generation)}] {voice.voice_id:<20} {voice.voice_name:<25}...", end=" ")
            
            success, message, data = generate_voice_sample(voice.voice_id, voice.voice_name)
            
            if success:
                print(f"✅ {message}")
                # Update URL in database
                if update_voice_url(session, voice, voice.voice_id):
                    success_count += 1
                    # Small delay to avoid rate limiting
                    time.sleep(1)
                else:
                    print(f"   ⚠️  Generated but failed to update URL")
                    failed_count += 1
            else:
                print(f"❌ {message}")
                failed_count += 1
                
                if "Rate limit" in message:
                    rate_limited = True
                    print(f"\n⏸️  Stopping due to rate limit")
                    break
        
        print(f"\n{'='*100}")
        print(f"📊 Generation Summary:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed:  {failed_count}")
        if rate_limited:
            print(f"   ⚠️  Rate limited - run again later to continue")
        print(f"{'='*100}\n")
    
    session.close()


def main():
    import sys
    
    check_only = "--check-only" in sys.argv or "-c" in sys.argv
    
    if check_only:
        print("\n🔍 CHECK-ONLY MODE: No samples will be generated\n")
    
    check_missing_samples(check_only=check_only)


if __name__ == "__main__":
    main()

"""
Update voice sample URLs in database

This script updates the voice_sample_url field for all voices that have 
generated samples in the kokoro_82M/samples directory.
"""
from pathlib import Path
from sqlmodel import Session, select
from models.db_models import SelectAIVoices, engine

# Configuration
SAMPLES_DIR = Path("kokoro_82M/samples")
API_PATH = "/api/voice-samples"  # Store only the path, not the full URL

def update_sample_urls():
    """Update voice sample URLs for all generated samples"""
    session = Session(engine)
    
    # Get all sample files from both locations
    media_samples = list(Path("media/voice-samples").glob("*_sample.wav"))
    kokoro_samples = list(SAMPLES_DIR.glob("*_sample.wav"))
    
    # Combine and deduplicate (prefer media/voice-samples)
    sample_files = media_samples.copy()
    media_names = {f.name for f in media_samples}
    for f in kokoro_samples:
        if f.name not in media_names:
            sample_files.append(f)
    
    if not sample_files:
        print("❌ No sample files found")
        return
    
    print(f"\n📂 Found {len(sample_files)} sample files")
    print("=" * 80)
    
    updated_count = 0
    not_found_count = 0
    
    for sample_file in sorted(sample_files):
        # Extract voice_id from filename (e.g., "af_sarah_sample.wav" -> "af_sarah")
        voice_id = sample_file.stem.replace("_sample", "")
        
        # Find voice in database
        voice = session.exec(
            select(SelectAIVoices)
            .where(SelectAIVoices.voice_id == voice_id)
        ).first()
        
        if voice:
            # Update the sample URL (store only path, not full URL)
            new_url = f"{API_PATH}/{sample_file.name}"
            old_url = voice.voice_sample_url
            
            voice.voice_sample_url = new_url
            session.add(voice)
            
            status = "✅ Updated" if old_url != new_url else "✓ Same"
            print(f"{status} | {voice_id:15} | {voice.voice_name:20} | {new_url}")
            updated_count += 1
        else:
            print(f"⚠️  Not found | {voice_id:15} | Voice not in database")
            not_found_count += 1
    
    # Commit all changes
    session.commit()
    session.close()
    
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   ✅ Updated: {updated_count} voices")
    print(f"   ⚠️  Not found: {not_found_count} voices")
    print(f"\n✅ All voice sample URLs have been updated!")


def verify_urls():
    """Verify the updated URLs"""
    session = Session(engine)
    
    # Get all voices with sample URLs
    voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.voice_sample_url.isnot(None))
        .where(SelectAIVoices.voice_sample_url != "")
        .order_by(SelectAIVoices.voice_id)
    ).all()
    
    print(f"\n📊 Voices with Sample URLs: {len(voices)}")
    print("=" * 100)
    
    for voice in voices:
        # Check if sample file exists
        if "/api/voice-samples/" in voice.voice_sample_url:
            filename = voice.voice_sample_url.split("/")[-1]
            sample_path = SAMPLES_DIR / filename
            exists = "✅" if sample_path.exists() else "❌"
        else:
            exists = "⚠️"
        
        print(f"{exists} | {voice.voice_id:15} | {voice.voice_name:20} | {voice.voice_sample_url}")
    
    print("=" * 100)
    session.close()


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_urls()
    else:
        update_sample_urls()
        print("\nVerifying updated URLs...")
        verify_urls()


if __name__ == "__main__":
    main()

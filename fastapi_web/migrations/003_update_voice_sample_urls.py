"""
Migration: Update voice_sample_url to store only path (without domain)

This migration updates the voice_sample_url field in selectaivoices table
to store only the path portion of the URL, removing the domain.

Before: http://localhost:8000/api/voice-samples/af_sarah_sample.wav
After: /api/voice-samples/af_sarah_sample.wav

Date: 2025-11-21
"""
import sys
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from models.db_models import SelectAIVoices, engine
import re

def remove_domain_from_url(url: str) -> str:
    """
    Extract only the path from a full URL
    
    Examples:
        http://localhost:8000/api/voice-samples/af_sarah_sample.wav 
        -> /api/voice-samples/af_sarah_sample.wav
        
        https://replicate.com/jaaari/kokoro-82m?voice=af_alloy
        -> (keep as is - external URL)
    """
    if not url:
        return url
    
    # Pattern to match localhost URLs
    localhost_pattern = r'^https?://localhost:\d+(.*)$'
    match = re.match(localhost_pattern, url)
    
    if match:
        # Extract the path portion
        return match.group(1)
    
    # Keep external URLs as is
    return url


def update_voice_sample_urls():
    """Update all voice_sample_url fields to store only paths"""
    session = Session(engine)
    
    # Get all voices with sample URLs
    voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.voice_sample_url.isnot(None))
        .where(SelectAIVoices.voice_sample_url != "")
    ).all()
    
    print(f"\n📊 Found {len(voices)} voices with sample URLs")
    print("=" * 100)
    print(f"{'Voice ID':<20} {'Old URL':<50} {'New URL':<50}")
    print("=" * 100)
    
    updated_count = 0
    unchanged_count = 0
    
    for voice in voices:
        old_url = voice.voice_sample_url
        new_url = remove_domain_from_url(old_url)
        
        if old_url != new_url:
            voice.voice_sample_url = new_url
            session.add(voice)
            status = "✅ Updated"
            updated_count += 1
        else:
            status = "⏭️  Skipped"
            unchanged_count += 1
        
        # Truncate URLs for display
        old_display = (old_url[:47] + '...') if len(old_url) > 50 else old_url
        new_display = (new_url[:47] + '...') if len(new_url) > 50 else new_url
        
        print(f"{voice.voice_id:<20} {old_display:<50} {new_display:<50} {status}")
    
    # Commit changes
    session.commit()
    session.close()
    
    print("=" * 100)
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Updated:   {updated_count} URLs (localhost URLs converted to paths)")
    print(f"   ⏭️  Unchanged: {unchanged_count} URLs (external URLs kept as is)")
    print(f"\n✅ Migration completed successfully!")


def verify_migration():
    """Verify the migration results"""
    session = Session(engine)
    
    voices = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.voice_sample_url.isnot(None))
        .where(SelectAIVoices.voice_sample_url != "")
        .order_by(SelectAIVoices.voice_id)
    ).all()
    
    print(f"\n📋 Verification Report:")
    print("=" * 100)
    
    localhost_count = 0
    path_count = 0
    external_count = 0
    
    for voice in voices:
        url = voice.voice_sample_url
        if url.startswith('http://localhost') or url.startswith('https://localhost'):
            localhost_count += 1
            print(f"⚠️  Still has localhost: {voice.voice_id} -> {url}")
        elif url.startswith('/'):
            path_count += 1
        elif url.startswith('http'):
            external_count += 1
    
    print("=" * 100)
    print(f"\n📊 URL Types:")
    print(f"   ✅ Path only:     {path_count}")
    print(f"   🌐 External URLs: {external_count}")
    print(f"   ⚠️  Localhost:     {localhost_count}")
    
    if localhost_count > 0:
        print(f"\n⚠️  WARNING: {localhost_count} URLs still contain localhost!")
    else:
        print(f"\n✅ All localhost URLs have been converted to paths!")
    
    session.close()


def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_migration()
    else:
        print("\n" + "=" * 100)
        print("🔄 MIGRATION: Update voice_sample_url to store only paths")
        print("=" * 100)
        
        update_voice_sample_urls()
        
        print("\n" + "=" * 100)
        print("🔍 Running verification...")
        print("=" * 100)
        
        verify_migration()


if __name__ == "__main__":
    main()

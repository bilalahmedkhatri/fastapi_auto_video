#!/usr/bin/env python3
"""
Integrate Kokoro voices into the database
This script adds the 46 Kokoro voices to the existing voice system
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from kokoro_voice_scraper import KokoroVoiceScraper
from models.db_models import SelectAIVoices, get_session

async def integrate_kokoro_voices():
    """Integrate Kokoro voices into the database"""
    print("🚀 Integrating Kokoro Voices into Database")
    print("=" * 60)
    
    # Create scraper (not dry-run mode)
    scraper = KokoroVoiceScraper(dry_run=False, update_existing=True)
    
    try:
        # Run the scraper
        success = scraper.run()
        
        if success:
            print("\n✅ Integration completed successfully!")
            
            # Verify integration
            print("\n🔍 Verifying integration...")
            with next(get_session()) as session:
                kokoro_voices = session.query(SelectAIVoices).filter(
                    SelectAIVoices.provider == 'kokoro'
                ).all()
                
                print(f"📊 Found {len(kokoro_voices)} Kokoro voices in database:")
                
                # Group by language
                lang_groups = {}
                for voice in kokoro_voices:
                    lang = voice.language
                    if lang not in lang_groups:
                        lang_groups[lang] = []
                    lang_groups[lang].append(voice)
                
                for lang, voices in lang_groups.items():
                    female_count = sum(1 for v in voices if v.gender == 'female')
                    male_count = sum(1 for v in voices if v.gender == 'male')
                    print(f"  {lang}: {len(voices)} voices ({female_count} female, {male_count} male)")
                
                print(f"\n🎉 Successfully integrated {len(kokoro_voices)} Kokoro voices!")
        else:
            print("❌ Integration failed. Check logs for details.")
            return False
            
    except Exception as e:
        print(f"💥 Integration failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main entry point"""
    # Check if database is available
    try:
        from models.db_models import SelectAIVoices
        print("✅ Database models available")
    except ImportError as e:
        print(f"❌ Database models not available: {e}")
        print("Make sure you're in the FastAPI environment and database is configured")
        return 1
    
    # Run integration
    success = asyncio.run(integrate_kokoro_voices())
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

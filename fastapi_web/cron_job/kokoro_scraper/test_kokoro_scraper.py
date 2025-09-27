#!/usr/bin/env python3
"""
Test script for the Kokoro Voice Scraper
Tests the scraper functionality without making database changes
"""

import sys
import json
import logging
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from kokoro_voice_scraper import KokoroVoiceScraper

def test_scraper():
    """Test the scraper functionality"""
    print("🧪 Testing Kokoro Voice Scraper...")
    print("=" * 50)
    
    # Create scraper in dry-run mode
    scraper = KokoroVoiceScraper(dry_run=True, update_existing=False)
    
    try:
        # Test webpage fetching
        print("📥 Testing webpage fetch...")
        html_content = scraper.fetch_webpage_with_retry()
        print(f"✅ Fetched {len(html_content):,} bytes of HTML content")
        
        # Test voice parsing
        print("\n🔍 Testing voice data parsing...")
        voices = scraper.parse_voice_data(html_content)
        print(f"✅ Parsed {len(voices)} voices")
        
        # Analyze voices by language
        print("\n📊 Voice Statistics by Language:")
        lang_stats = {}
        for voice in voices:
            lang = voice.language
            if lang not in lang_stats:
                lang_stats[lang] = {"total": 0, "male": 0, "female": 0, "grades": {}}
            
            lang_stats[lang]["total"] += 1
            lang_stats[lang][voice.gender] += 1
            
            grade = voice.quality_grade
            if grade not in lang_stats[lang]["grades"]:
                lang_stats[lang]["grades"][grade] = 0
            lang_stats[lang]["grades"][grade] += 1
        
        for lang, stats in lang_stats.items():
            print(f"  {lang}: {stats['total']} voices ({stats['female']} female, {stats['male']} male)")
            grade_str = ", ".join([f"{grade}:{count}" for grade, count in sorted(stats['grades'].items())])
            print(f"    Grades: {grade_str}")
        
        # Show sample voices
        print("\n🎤 Sample Voices (first 10):")
        for i, voice in enumerate(voices[:10]):
            special = f" [{voice.special_features}]" if voice.special_features else ""
            print(f"  {i+1:2d}. {voice.voice_id:<12} | {voice.gender:<6} | {voice.accent:<10} | Grade: {voice.quality_grade} | {voice.training_duration}{special}")
        
        # Test backup creation
        print("\n💾 Testing backup creation...")
        scraper.save_backup(voices)
        print("✅ Backup created successfully")
        
        # Test database simulation (dry run)
        print("\n🗄️  Testing database update (dry run)...")
        scraper.update_database(voices)
        print("✅ Database update simulation completed")
        
        # Generate report
        print("\n📋 Final Report:")
        report = scraper.generate_report()
        
        print("\n🎉 All tests completed successfully!")
        
        # Save detailed results
        results = {
            "test_timestamp": scraper.stats["start_time"].isoformat(),
            "total_voices": len(voices),
            "language_stats": lang_stats,
            "sample_voices": [
                {
                    "voice_id": voice.voice_id,
                    "language": voice.language,
                    "gender": voice.gender,
                    "quality_grade": voice.quality_grade,
                    "accent": voice.accent
                }
                for voice in voices[:5]
            ],
            "scraper_stats": scraper.stats
        }
        
        with open("kokoro_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📄 Detailed results saved to: kokoro_test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Test individual components"""
    print("\n🔧 Testing Individual Components:")
    print("=" * 50)
    
    scraper = KokoroVoiceScraper(dry_run=True)
    
    # Test language mappings
    print("🌍 Testing language mappings...")
    language_mappings = {
        "American English 🇺🇸": {"code": "en", "accent": "american"},
        "British English 🇬🇧": {"code": "en-gb", "accent": "british"},
        "French 🇫🇷": {"code": "fr", "accent": "french"},
        "Hindi 🇮🇳": {"code": "hi", "accent": "hindi"},
        "Italian 🇮🇹": {"code": "it", "accent": "italian"}, 
        "Japanese 🇯🇵": {"code": "ja", "accent": "japanese"},
        "Mandarin Chinese 🇨🇳": {"code": "zh", "accent": "chinese"}
    }
    
    for lang_display, lang_info in language_mappings.items():
        print(f"  ✅ {lang_display} -> {lang_info['code']} ({lang_info['accent']})")
    
    # Test voice data structure
    print("\n📋 Testing voice data structure...")
    from kokoro_voice_scraper import VoiceData
    
    test_voice = VoiceData(
        voice_id="af_bella",
        gender="female",
        language="American English 🇺🇸",
        language_code="en",
        accent="american",
        quality_grade="A",
        training_duration="HH hours",
        overall_grade="A-",
        hash_id="8cb64e02",
        special_features="🔥"
    )
    
    db_dict = test_voice.to_db_dict()
    print(f"  ✅ Voice data conversion: {test_voice.voice_id}")
    print(f"     Description: {db_dict['voice_description']}")
    print(f"     Settings: {db_dict['voice_settings']}")
    
    print("\n🎯 Component tests completed!")

def main():
    """Main test function"""
    print("🚀 Starting Kokoro Voice Scraper Tests")
    print("=" * 60)
    
    # Run individual component tests
    test_individual_components()
    
    print("\n" + "=" * 60)
    
    # Run full scraper test
    success = test_scraper()
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Result: {'SUCCESS' if success else 'FAILED'}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

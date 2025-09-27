#!/usr/bin/env python3
"""
Simple Kokoro Voice Data Extractor
Since the webpage is JavaScript-rendered, this approach extracts voices from the API schema
"""

import re
import json
import requests
from typing import Dict, List
from kokoro_voice_scraper import VoiceData

def extract_voices_from_api_schema():
    """Extract voices from the API schema in the HTML"""
    
    # Get the webpage
    response = requests.get("https://replicate.com/jaaari/kokoro-82m")
    html_content = response.text
    
    # Find the voice enum in the API schema
    # Look for the voice enum definition
    voice_enum_pattern = r'"enum":\s*\[(.*?)\]'
    matches = re.findall(voice_enum_pattern, html_content, re.DOTALL)
    
    # Find the longest enum (likely the voice list)
    voice_list = None
    max_length = 0
    
    for match in matches:
        # Parse as JSON array
        try:
            voices = json.loads('[' + match + ']')
            if len(voices) > max_length and all(isinstance(v, str) and '_' in v for v in voices):
                voice_list = voices
                max_length = len(voices)
        except json.JSONDecodeError:
            continue
    
    if not voice_list:
        print("❌ Could not find voice list in API schema")
        return []
    
    print(f"✅ Found {len(voice_list)} voices in API schema")
    
    # Create voice data objects with metadata mapping
    voices = []
    
    # Language and gender mapping based on voice ID prefixes
    voice_mappings = {
        'af_': {'language': 'American English 🇺🇸', 'code': 'en', 'accent': 'american', 'gender': 'female'},
        'am_': {'language': 'American English 🇺🇸', 'code': 'en', 'accent': 'american', 'gender': 'male'},
        'bf_': {'language': 'British English 🇬🇧', 'code': 'en-gb', 'accent': 'british', 'gender': 'female'},
        'bm_': {'language': 'British English 🇬🇧', 'code': 'en-gb', 'accent': 'british', 'gender': 'male'},
        'ff_': {'language': 'French 🇫🇷', 'code': 'fr', 'accent': 'french', 'gender': 'female'},
        'fm_': {'language': 'French 🇫🇷', 'code': 'fr', 'accent': 'french', 'gender': 'male'},
        'hf_': {'language': 'Hindi 🇮🇳', 'code': 'hi', 'accent': 'hindi', 'gender': 'female'},
        'hm_': {'language': 'Hindi 🇮🇳', 'code': 'hi', 'accent': 'hindi', 'gender': 'male'},
        'if_': {'language': 'Italian 🇮🇹', 'code': 'it', 'accent': 'italian', 'gender': 'female'},
        'im_': {'language': 'Italian 🇮🇹', 'code': 'it', 'accent': 'italian', 'gender': 'male'},
        'jf_': {'language': 'Japanese 🇯🇵', 'code': 'ja', 'accent': 'japanese', 'gender': 'female'},
        'jm_': {'language': 'Japanese 🇯🇵', 'code': 'ja', 'accent': 'japanese', 'gender': 'male'},
        'zf_': {'language': 'Mandarin Chinese 🇨🇳', 'code': 'zh', 'accent': 'chinese', 'gender': 'female'},
        'zm_': {'language': 'Mandarin Chinese 🇨🇳', 'code': 'zh', 'accent': 'chinese', 'gender': 'male'},
    }
    
    for voice_id in voice_list:
        # Extract prefix
        prefix = voice_id[:3]
        
        if prefix in voice_mappings:
            mapping = voice_mappings[prefix]
            
            # Create VoiceData object
            voice = VoiceData(
                voice_id=voice_id,
                gender=mapping['gender'],
                language=mapping['language'],
                language_code=mapping['code'],
                accent=mapping['accent'],
                quality_grade="B",  # Default - would need to scrape individual pages for exact grades
                training_duration="Variable",  # Default - would need to scrape for exact duration
                overall_grade="C+",  # Default - would need to scrape for exact grade
                hash_id="00000000",  # Placeholder - would need to scrape for actual hash
                special_features=None
            )
            
            voices.append(voice)
        else:
            print(f"⚠️ Unknown voice prefix for {voice_id}")
    
    return voices

def main():
    """Test the simple extraction"""
    print("🚀 Testing Simple Voice Extraction")
    print("=" * 50)
    
    voices = extract_voices_from_api_schema()
    
    if not voices:
        print("❌ No voices extracted")
        return
    
    # Group by language
    lang_groups = {}
    for voice in voices:
        lang = voice.language
        if lang not in lang_groups:
            lang_groups[lang] = []
        lang_groups[lang].append(voice)
    
    print(f"📊 Extracted {len(voices)} voices across {len(lang_groups)} languages:")
    
    for lang, lang_voices in lang_groups.items():
        print(f"\n{lang}: {len(lang_voices)} voices")
        for voice in lang_voices[:5]:  # Show first 5
            print(f"  - {voice.voice_id} ({voice.gender})")
        if len(lang_voices) > 5:
            print(f"  ... and {len(lang_voices) - 5} more")
    
    # Save results
    results = {
        'total_voices': len(voices),
        'voices': [
            {
                'voice_id': voice.voice_id,
                'language': voice.language,
                'gender': voice.gender,
                'accent': voice.accent,
                'db_data': voice.to_db_dict()
            }
            for voice in voices
        ]
    }
    
    with open('extracted_voices.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to extracted_voices.json")
    print("✅ Extraction completed successfully!")

if __name__ == "__main__":
    main()

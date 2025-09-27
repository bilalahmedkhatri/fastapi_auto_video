#!/usr/bin/env python3
"""
Debug script to examine the HTML structure and test parsing
"""

import re
import requests
from pathlib import Path

def debug_html_structure():
    """Debug the HTML structure"""
    print("🔍 Debugging HTML Structure...")
    
    # Fetch the webpage
    response = requests.get("https://replicate.com/jaaari/kokoro-82m")
    html_content = response.text
    
    print(f"HTML Content Length: {len(html_content):,} bytes")
    
    # Look for section headers
    print("\n📄 Looking for section headers...")
    section_matches = re.findall(r'###\s*([^#\n]+)', html_content)
    print(f"Found {len(section_matches)} section headers:")
    for i, section in enumerate(section_matches[:10]):  # Show first 10
        print(f"  {i+1:2d}. '{section.strip()}'")
    
    # Look for American English section specifically
    print("\n🇺🇸 Looking for American English section...")
    patterns_to_try = [
        "American English",
        "🇺🇸",
        "af_",
        "am_",
        "### American"
    ]
    
    for pattern in patterns_to_try:
        matches = []
        for match in re.finditer(pattern, html_content):
            start = max(0, match.start() - 50)
            end = min(len(html_content), match.end() + 50)
            context = html_content[start:end].replace('\n', '\\n')
            matches.append(f"Position {match.start()}: ...{context}...")
        
        print(f"\nPattern '{pattern}': {len(matches)} matches")
        for match in matches[:3]:  # Show first 3 matches
            print(f"  {match}")
    
    # Look for table patterns
    print("\n📊 Looking for table patterns...")
    table_patterns = [
        r'\|.*af_.*\|',
        r'\|.*🚺.*\|',
        r'\|.*\|.*\|.*\|.*\|.*\|.*\|',  # 6+ column table
    ]
    
    for pattern in table_patterns:
        matches = re.findall(pattern, html_content)
        print(f"Pattern '{pattern}': {len(matches)} matches")
        for match in matches[:3]:  # Show first 3
            print(f"  {match[:100]}...")
    
    # Save a sample of the HTML for manual inspection
    print("\n💾 Saving HTML sample...")
    # Find the voices section
    voices_start = html_content.find("# Voices")
    if voices_start != -1:
        # Get about 10KB around the voices section
        start = max(0, voices_start - 2000)
        end = min(len(html_content), voices_start + 8000)
        sample = html_content[start:end]
        
        with open("html_voices_sample.txt", "w", encoding="utf-8") as f:
            f.write(sample)
        print("Sample saved to html_voices_sample.txt")
    else:
        print("Could not find '# Voices' section")
    
    # Look for voice IDs directly
    print("\n🎤 Looking for voice IDs directly...")
    voice_id_pattern = r'\b[a-z]{2}_[a-z]+\b'
    voice_ids = re.findall(voice_id_pattern, html_content)
    unique_voice_ids = list(set(voice_ids))
    print(f"Found {len(unique_voice_ids)} unique voice IDs:")
    for voice_id in sorted(unique_voice_ids)[:20]:  # Show first 20
        print(f"  {voice_id}")

if __name__ == "__main__":
    debug_html_structure()

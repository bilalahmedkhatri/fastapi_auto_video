#!/usr/bin/env python3
"""
Extract the HTML structure around voice tables
"""

import requests
import re

def extract_voice_sections():
    """Extract voice sections from HTML"""
    response = requests.get("https://replicate.com/jaaari/kokoro-82m")
    html_content = response.text
    
    # Find American English section
    start = html_content.find('<h3 id="american-english">')
    if start != -1:
        # Get content after this header
        end = html_content.find('<h3 id=', start + 1)
        if end == -1:
            end = start + 5000
        
        section = html_content[start:end]
        print("=== American English Section ===")
        print(section[:3000])
        
        # Save full section to file
        with open("american_english_section.html", "w", encoding="utf-8") as f:
            f.write(section[:5000])
    
    # Look for table structures
    print("\n=== Table Structures ===")
    table_patterns = [
        r'<table[^>]*>.*?</table>',
        r'<tbody[^>]*>.*?</tbody>',
        r'<tr[^>]*>.*?</tr>',
    ]
    
    for pattern in table_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        print(f"Pattern '{pattern}': {len(matches)} matches")
        if matches:
            print(f"First match preview: {matches[0][:200]}...")
    
    # Look for specific voice entries in different formats
    print("\n=== Voice Entry Patterns ===")
    voice_patterns = [
        r'af_alloy.*?[a-f0-9]{8}',  # voice_id to hash
        r'<.*?>af_alloy<.*?>',      # HTML tagged voice
        r'af_alloy[^a-z]*🚺',       # voice with gender
    ]
    
    for pattern in voice_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        print(f"Pattern '{pattern}': {len(matches)} matches")
        for match in matches[:2]:
            print(f"  {match}")

if __name__ == "__main__":
    extract_voice_sections()

#!/usr/bin/env python3
"""
Test script for the updated SelectAIVoices model
"""

import sys
import os
sys.path.append('models')

from models.db_models import (
    create_db_and_tables, 
    get_session, 
    SelectAIVoices, 
    VideoVoiceSelection,
    seed_demo_voices,
    get_local_voice_sample_url
)
from sqlmodel import select

def test_voice_models():
    """Test the voice models and demonstrate functionality"""
    
    print("=" * 60)
    print("Testing AI Voices Database Models")
    print("=" * 60)
    
    # Create tables
    print("1. Creating database tables...")
    create_db_and_tables()
    print("✓ Tables created successfully")
    
    # Seed demo voices
    print("\n2. Seeding demo voices...")
    seed_demo_voices()
    print("✓ Demo voices seeded successfully")
    
    # Test querying voices
    print("\n3. Querying available voices...")
    with next(get_session()) as session:
        voices = session.exec(select(SelectAIVoices)).all()
        
        print(f"Found {len(voices)} voices:")
        for voice in voices:
            print(f"  - {voice.voice_name} ({voice.voice_id})")
            print(f"    Gender: {voice.gender}, Accent: {voice.accent}")
            print(f"    Provider: {voice.provider}")
            print(f"    Sample URL: {voice.voice_sample_url}")
            print(f"    Is Demo: {voice.is_demo}")
            print()
    
    # Test URL generation
    print("4. Testing URL generation...")
    test_voice_id = "am_puck"
    sample_url = get_local_voice_sample_url(test_voice_id)
    print(f"Sample URL for {test_voice_id}: {sample_url}")
    
    # Test filtering voices
    print("\n5. Testing voice filtering...")
    with next(get_session()) as session:
        # Get only demo voices
        demo_voices = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.is_demo == True)
        ).all()
        print(f"Demo voices: {len(demo_voices)}")
        
        # Get only female voices
        female_voices = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.gender == "female")
        ).all()
        print(f"Female voices: {len(female_voices)}")
        
        # Get only male voices
        male_voices = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.gender == "male")
        ).all()
        print(f"Male voices: {len(male_voices)}")
        
        # Get voices by provider
        openai_voices = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.provider == "openai")
        ).all()
        print(f"OpenAI voices: {len(openai_voices)}")
        
        # Get voices by age group
        young_adult_voices = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.age_group == "young_adult")
        ).all()
        print(f"Young adult voices: {len(young_adult_voices)}")
    
    # Test voice file existence
    print("\n6. Testing voice file availability...")
    voices_dir = "video_builder/ai_apis/voices_samples/american"
    import os
    available_files = []
    if os.path.exists(voices_dir):
        files = os.listdir(voices_dir)
        wav_files = [f for f in files if f.endswith('.wav')]
        print(f"Available WAV files: {len(wav_files)}")
        for f in wav_files[:5]:  # Show first 5 files
            print(f"  - {f}")
        if len(wav_files) > 5:
            print(f"  ... and {len(wav_files) - 5} more files")
    else:
        print(f"Voice samples directory not found: {voices_dir}")
    
    print("\n✓ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_voice_models()

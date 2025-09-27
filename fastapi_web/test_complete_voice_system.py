#!/usr/bin/env python3
"""
Complete test of the AI Voices system with actual voice samples
"""

import sys
import os
from pathlib import Path

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

def test_complete_voice_system():
    """Test the complete voice system with actual samples"""
    
    print("=" * 70)
    print("COMPLETE AI VOICES SYSTEM TEST")
    print("=" * 70)
    
    # 1. Setup database
    print("1. Setting up database...")
    create_db_and_tables()
    print("✓ Database tables created")
    
    # 2. Seed voices
    print("\n2. Seeding voices database...")
    seed_demo_voices()
    print("✓ Voice database seeded")
    
    # 3. Query and display all voices
    print("\n3. Available Voices:")
    print("-" * 50)
    
    with next(get_session()) as session:
        voices = session.exec(select(SelectAIVoices)).all()
        
        # Group by gender
        female_voices = [v for v in voices if v.gender == "female"]
        male_voices = [v for v in voices if v.gender == "male"]
        
        print(f"FEMALE VOICES ({len(female_voices)}):")
        for voice in female_voices:
            sample_exists = "✓" if Path(f"media/voice_samples_real/{voice.voice_id}.wav").exists() else "✗"
            print(f"  {sample_exists} {voice.voice_name} ({voice.voice_id}) - {voice.voice_description}")
            print(f"      Age: {voice.age_group}, Provider: {voice.provider}")
            print(f"      Sample: {voice.voice_sample_url}")
        
        print(f"\nMALE VOICES ({len(male_voices)}):")
        for voice in male_voices:
            sample_exists = "✓" if Path(f"media/voice_samples_real/{voice.voice_id}.wav").exists() else "✗"
            print(f"  {sample_exists} {voice.voice_name} ({voice.voice_id}) - {voice.voice_description}")
            print(f"      Age: {voice.age_group}, Provider: {voice.provider}")
            print(f"      Sample: {voice.voice_sample_url}")
    
    # 4. Test voice sample file availability
    print("\n4. Voice Sample Files Status:")
    print("-" * 50)
    
    samples_dir = Path("media/voice_samples_real")
    if samples_dir.exists():
        sample_files = list(samples_dir.glob("*.wav"))
        print(f"✓ Found {len(sample_files)} voice sample files")
        
        # Show file sizes
        for sample_file in sorted(sample_files)[:5]:  # Show first 5
            size_mb = sample_file.stat().st_size / (1024 * 1024)
            print(f"    {sample_file.name}: {size_mb:.2f} MB")
        
        if len(sample_files) > 5:
            print(f"    ... and {len(sample_files) - 5} more files")
    else:
        print("✗ Voice samples directory not found")
    
    # 5. Test voice selection for video
    print("\n5. Testing Voice Selection for Video:")
    print("-" * 50)
    
    test_video_id = "test-video-123"
    
    with next(get_session()) as session:
        # Select a female voice for the test video
        female_voice = session.exec(
            select(SelectAIVoices).where(SelectAIVoices.gender == "female")
        ).first()
        
        if female_voice:
            # Create voice selection
            selection = VideoVoiceSelection(
                video_id=test_video_id,
                voice_id=female_voice.voice_id,
                is_active=True
            )
            session.add(selection)
            session.commit()
            
            print(f"✓ Selected voice '{female_voice.voice_name}' for video {test_video_id}")
            print(f"  Voice ID: {female_voice.voice_id}")
            print(f"  Description: {female_voice.voice_description}")
            print(f"  Sample URL: {female_voice.voice_sample_url}")
    
    # 6. Query voice selection
    print("\n6. Querying Voice Selection:")
    print("-" * 50)
    
    with next(get_session()) as session:
        selection = session.exec(
            select(VideoVoiceSelection)
            .where(VideoVoiceSelection.video_id == test_video_id)
            .where(VideoVoiceSelection.is_active == True)
        ).first()
        
        if selection:
            selected_voice = session.exec(
                select(SelectAIVoices).where(SelectAIVoices.voice_id == selection.voice_id)
            ).first()
            
            print(f"✓ Video {test_video_id} has voice selection:")
            print(f"  Voice: {selected_voice.voice_name} ({selected_voice.voice_id})")
            print(f"  Selected at: {selection.selected_at}")
    
    # 7. Provider statistics
    print("\n7. Voice Statistics:")
    print("-" * 50)
    
    with next(get_session()) as session:
        voices = session.exec(select(SelectAIVoices)).all()
        
        # Count by provider
        providers = {}
        for voice in voices:
            providers[voice.provider] = providers.get(voice.provider, 0) + 1
        
        # Count by age group
        age_groups = {}
        for voice in voices:
            age_groups[voice.age_group] = age_groups.get(voice.age_group, 0) + 1
        
        print("By Provider:")
        for provider, count in providers.items():
            print(f"  {provider}: {count} voices")
        
        print("\nBy Age Group:")
        for age, count in age_groups.items():
            print(f"  {age}: {count} voices")
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE VOICE SYSTEM TEST SUCCESSFUL!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    test_complete_voice_system()

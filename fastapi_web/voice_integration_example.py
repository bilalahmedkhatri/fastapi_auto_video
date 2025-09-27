"""
Example integration of AI Voices with Video Builder
This shows how to use the voice selection system in your video generation workflow
"""

from models.db_models import SelectAIVoices, VideoVoiceSelection, get_session
from sqlmodel import select
import random

class VoiceSelector:
    """Helper class for voice selection in video generation"""
    
    def __init__(self):
        pass
    
    def get_available_voices(self, gender=None, age_group=None, provider=None):
        """Get available voices with optional filtering"""
        with next(get_session()) as session:
            query = select(SelectAIVoices).where(SelectAIVoices.is_active == True)
            
            if gender:
                query = query.where(SelectAIVoices.gender == gender)
            if age_group:
                query = query.where(SelectAIVoices.age_group == age_group)  
            if provider:
                query = query.where(SelectAIVoices.provider == provider)
            
            return session.exec(query).all()
    
    def get_voice_by_id(self, voice_id):
        """Get a specific voice by ID"""
        with next(get_session()) as session:
            return session.exec(
                select(SelectAIVoices).where(SelectAIVoices.voice_id == voice_id)
            ).first()
    
    def select_voice_for_video(self, video_id, voice_id):
        """Select a voice for a specific video"""
        with next(get_session()) as session:
            # Deactivate existing selections
            existing = session.exec(
                select(VideoVoiceSelection).where(VideoVoiceSelection.video_id == video_id)
            ).all()
            
            for sel in existing:
                sel.is_active = False
            
            # Create new selection
            selection = VideoVoiceSelection(
                video_id=video_id,
                voice_id=voice_id,
                is_active=True
            )
            session.add(selection)
            session.commit()
            
            return selection
    
    def get_selected_voice(self, video_id):
        """Get the currently selected voice for a video"""
        with next(get_session()) as session:
            selection = session.exec(
                select(VideoVoiceSelection)
                .where(VideoVoiceSelection.video_id == video_id)
                .where(VideoVoiceSelection.is_active == True)
            ).first()
            
            if selection:
                return session.exec(
                    select(SelectAIVoices).where(SelectAIVoices.voice_id == selection.voice_id)
                ).first()
            
            return None
    
    def recommend_voice(self, content_type="general", target_audience="adult"):
        """Recommend a voice based on content type and audience"""
        
        # Voice recommendation logic
        recommendations = {
            "news": {"gender": "male", "age_group": "adult"},
            "tutorial": {"gender": "female", "age_group": "adult"},
            "entertainment": {"gender": None, "age_group": "young_adult"},
            "professional": {"gender": "male", "age_group": "adult"},
            "casual": {"gender": None, "age_group": "young_adult"}
        }
        
        criteria = recommendations.get(content_type, {})
        voices = self.get_available_voices(**criteria)
        
        if voices:
            return random.choice(voices)
        
        # Fallback to any available voice
        all_voices = self.get_available_voices()
        return random.choice(all_voices) if all_voices else None

# Example usage in video generation
def example_video_generation_with_voice():
    """Example showing how to integrate voice selection in video generation"""
    
    voice_selector = VoiceSelector()
    
    # Example video data
    video_id = "video-12345"
    content_type = "news"
    
    print("=== Video Generation with Voice Selection ===")
    
    # 1. Get or recommend a voice
    print("\n1. Voice Selection:")
    recommended_voice = voice_selector.recommend_voice(content_type)
    
    if recommended_voice:
        print(f"✓ Recommended voice: {recommended_voice.voice_name}")
        print(f"  ID: {recommended_voice.voice_id}")
        print(f"  Description: {recommended_voice.voice_description}")
        print(f"  Sample URL: {recommended_voice.voice_sample_url}")
        
        # 2. Select voice for video
        print("\n2. Selecting voice for video...")
        voice_selector.select_voice_for_video(video_id, recommended_voice.voice_id)
        print(f"✓ Voice '{recommended_voice.voice_name}' selected for video {video_id}")
        
        # 3. Retrieve selected voice for video generation
        print("\n3. Retrieving selected voice...")
        selected_voice = voice_selector.get_selected_voice(video_id)
        
        if selected_voice:
            print(f"✓ Using voice: {selected_voice.voice_name} ({selected_voice.voice_id})")
            
            # 4. Integration with existing video generation
            voice_config = {
                "voice_id": selected_voice.voice_id,
                "voice_name": selected_voice.voice_name,
                "provider": selected_voice.provider,
                "model_name": selected_voice.model_name,
                "sample_url": selected_voice.voice_sample_url
            }
            
            print(f"\n4. Voice configuration for video generation:")
            for key, value in voice_config.items():
                print(f"   {key}: {value}")
            
            # This would integrate with your existing video_builder.py
            # For example, in the main() function:
            # voice_id = voice_config["voice_id"]
            # download_voice_replicate(text=ai_generated_script, voice=voice_id)
            
            return voice_config
    else:
        print("✗ No voices available")
        return None

# Alternative: Manual voice selection
def example_manual_voice_selection():
    """Example of manual voice selection"""
    
    voice_selector = VoiceSelector()
    
    print("=== Available Female Voices ===")
    female_voices = voice_selector.get_available_voices(gender="female")
    
    for voice in female_voices[:5]:  # Show first 5
        print(f"• {voice.voice_name} ({voice.voice_id})")
        print(f"  {voice.voice_description}")
        print(f"  Age: {voice.age_group}, Provider: {voice.provider}")
        print(f"  Sample: {voice.voice_sample_url}")
        print()
    
    print(f"Total female voices: {len(female_voices)}")

if __name__ == "__main__":
    print("Testing Voice Selection Integration...")
    
    # Test recommendation system
    example_video_generation_with_voice()
    
    print("\n" + "="*50)
    
    # Test manual selection
    example_manual_voice_selection()

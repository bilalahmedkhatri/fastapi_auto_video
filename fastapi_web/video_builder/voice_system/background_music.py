"""
Background Music Manager for Voice System
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .voice_models import BackgroundMusicConfig

logger = logging.getLogger(__name__)


class BackgroundMusicManager:
    """Manages background music for voiceovers"""
    
    def __init__(self, music_dir: str = "media/background_music"):
        self.music_dir = Path(music_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self._music_catalog = self._build_music_catalog()
    
    def _build_music_catalog(self) -> Dict[str, List[str]]:
        """Build catalog of available background music by type"""
        
        # Default music categories and sample tracks
        catalog = {
            "upbeat": [
                "energetic_beat.mp3",
                "positive_vibes.mp3",
                "uplifting_melody.mp3"
            ],
            "calm": [
                "peaceful_ambient.mp3",
                "soft_piano.mp3",
                "meditation_track.mp3"
            ],
            "dramatic": [
                "epic_orchestral.mp3",
                "tension_builder.mp3",
                "cinematic_theme.mp3"
            ],
            "corporate": [
                "professional_theme.mp3",
                "business_background.mp3",
                "corporate_success.mp3"
            ],
            "tech": [
                "electronic_ambient.mp3",
                "digital_pulse.mp3",
                "futuristic_sound.mp3"
            ],
            "nature": [
                "forest_sounds.mp3",
                "ocean_waves.mp3",
                "rain_ambient.mp3"
            ]
        }
        
        return catalog
    
    def get_available_music_types(self) -> List[str]:
        """Get list of available music types"""
        return list(self._music_catalog.keys())
    
    def get_music_tracks(self, music_type: str) -> List[str]:
        """Get list of tracks for a specific music type"""
        return self._music_catalog.get(music_type, [])
    
    def get_recommended_music(self, script_content: str) -> str:
        """Recommend background music type based on script content"""
        
        script_lower = script_content.lower()
        
        # Keywords to music type mapping
        keyword_mapping = {
            "upbeat": ["exciting", "amazing", "awesome", "energy", "fast", "quick", "breakthrough", "revolutionary"],
            "calm": ["peaceful", "relax", "meditation", "sleep", "calm", "gentle", "soft", "quiet"],
            "dramatic": ["breaking", "urgent", "crisis", "dramatic", "intense", "powerful", "epic", "shocking"],
            "corporate": ["business", "professional", "corporate", "company", "success", "growth", "strategy"],
            "tech": ["technology", "ai", "digital", "innovation", "tech", "future", "modern", "advanced"],
            "nature": ["nature", "environment", "eco", "green", "sustainability", "natural", "organic"]
        }
        
        # Score each music type based on keyword matches
        scores = {}
        for music_type, keywords in keyword_mapping.items():
            score = sum(1 for keyword in keywords if keyword in script_lower)
            if score > 0:
                scores[music_type] = score
        
        # Return the highest scoring type, or default to 'upbeat'
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "upbeat"  # Default
    
    async def apply_background_music(
        self, 
        voiceover_path: str, 
        config: BackgroundMusicConfig
    ) -> Optional[str]:
        """Apply background music to voiceover audio"""
        
        if not config.enabled:
            return voiceover_path
        
        try:
            # TODO: Implement audio mixing using pydub or moviepy
            # This would:
            # 1. Load the background music track
            # 2. Adjust volume according to config.volume
            # 3. Apply fade in/out effects
            # 4. Mix with voiceover audio
            # 5. Return path to mixed audio file
            
            logger.info(f"Background music would be applied: {config.music_type} at {config.volume} volume")
            return voiceover_path
            
        except Exception as e:
            logger.error(f"Error applying background music: {str(e)}")
            return voiceover_path

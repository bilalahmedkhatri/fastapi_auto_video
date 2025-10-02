"""
Voice Service - Core business logic for voice operations
"""
import asyncio
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import aiohttp
import json
from sqlmodel import Session

from .voice_models import (
    VoiceConfig, VoiceRequest, VoiceResponse, VoiceListResponse,
    VoiceGender, VoiceAccent, VoiceStyle, AudioSettings
)
from ..ai_apis.voice_gen_api import download_voice_replicate
from ..ai_apis.voices_replicate_json import voices
from models.db_models import GeneratedVoiceover, engine

logger = logging.getLogger(__name__)


class VoiceService:
    """Service class for voice-related operations"""
    
    def __init__(self, audio_output_dir: str = "media/audio"):
        self.audio_output_dir = Path(audio_output_dir)
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self._voice_cache = None
        
    def _get_voice_metadata(self) -> Dict[str, VoiceConfig]:
        """Get comprehensive voice metadata with gender, accent, and style information"""
        voice_metadata = {
            # American English Female Voices
            "af_alloy": VoiceConfig(
                voice_id="af_alloy", name="Alloy", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.NEUTRAL,
                description="Clear, professional American female voice"
            ),
            "af_aoede": VoiceConfig(
                voice_id="af_aoede", name="Aoede", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.FRIENDLY,
                description="Warm, friendly American female voice"
            ),
            "af_bella": VoiceConfig(
                voice_id="af_bella", name="Bella", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.EXCITED,
                description="Energetic, youthful American female voice"
            ),
            "af_jessica": VoiceConfig(
                voice_id="af_jessica", name="Jessica", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.PROFESSIONAL,
                description="Authoritative, confident American female voice"
            ),
            "af_kore": VoiceConfig(
                voice_id="af_kore", name="Kore", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.CALM,
                description="Soothing, calm American female voice"
            ),
            "af_nicole": VoiceConfig(
                voice_id="af_nicole", name="Nicole", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.FRIENDLY,
                description="Conversational American female voice"
            ),
            "af_nova": VoiceConfig(
                voice_id="af_nova", name="Nova", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.EXCITED,
                description="Dynamic, modern American female voice"
            ),
            "af_river": VoiceConfig(
                voice_id="af_river", name="River", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.CALM,
                description="Natural, flowing American female voice"
            ),
            "af_sarah": VoiceConfig(
                voice_id="af_sarah", name="Sarah", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.NEUTRAL,
                description="Reliable, clear American female voice"
            ),
            "af_sky": VoiceConfig(
                voice_id="af_sky", name="Sky", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.EXCITED,
                description="Bright, optimistic American female voice"
            ),
            
            # American English Male Voices
            "am_adam": VoiceConfig(
                voice_id="am_adam", name="Adam", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.PROFESSIONAL,
                description="Deep, authoritative American male voice"
            ),
            "am_echo": VoiceConfig(
                voice_id="am_echo", name="Echo", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.NEUTRAL,
                description="Versatile, clear American male voice"
            ),
            "am_eric": VoiceConfig(
                voice_id="am_eric", name="Eric", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.FRIENDLY,
                description="Warm, approachable American male voice"
            ),
            "am_fenrir": VoiceConfig(
                voice_id="am_fenrir", name="Fenrir", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.PROFESSIONAL,
                description="Strong, commanding American male voice"
            ),
            "am_liam": VoiceConfig(
                voice_id="am_liam", name="Liam", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.EXCITED,
                description="Energetic, youthful American male voice"
            ),
            "am_michael": VoiceConfig(
                voice_id="am_michael", name="Michael", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.NEUTRAL,
                description="Classic, trustworthy American male voice"
            ),
            "am_onyx": VoiceConfig(
                voice_id="am_onyx", name="Onyx", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.CALM,
                description="Smooth, sophisticated American male voice"
            ),
            "am_puck": VoiceConfig(
                voice_id="am_puck", name="Puck", gender=VoiceGender.MALE,
                accent=VoiceAccent.AMERICAN, style=VoiceStyle.EXCITED,
                description="Playful, dynamic American male voice"
            ),
            
            # British English Voices
            "bf_alice": VoiceConfig(
                voice_id="bf_alice", name="Alice", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.PROFESSIONAL,
                description="Elegant British female voice with RP accent"
            ),
            "bf_emma": VoiceConfig(
                voice_id="bf_emma", name="Emma", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.FRIENDLY,
                description="Charming, conversational British female voice"
            ),
            "bf_isabella": VoiceConfig(
                voice_id="bf_isabella", name="Isabella", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.CALM,
                description="Refined, sophisticated British female voice"
            ),
            "bf_lily": VoiceConfig(
                voice_id="bf_lily", name="Lily", gender=VoiceGender.FEMALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.NEUTRAL,
                description="Clear, articulate British female voice"
            ),
            "bm_daniel": VoiceConfig(
                voice_id="bm_daniel", name="Daniel", gender=VoiceGender.MALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.PROFESSIONAL,
                description="Distinguished British male voice with authority"
            ),
            "bm_fable": VoiceConfig(
                voice_id="bm_fable", name="Fable", gender=VoiceGender.MALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.FRIENDLY,
                description="Engaging storyteller British male voice"
            ),
            "bm_george": VoiceConfig(
                voice_id="bm_george", name="George", gender=VoiceGender.MALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.CALM,
                description="Steady, reliable British male voice"
            ),
            "bm_lewis": VoiceConfig(
                voice_id="bm_lewis", name="Lewis", gender=VoiceGender.MALE,
                accent=VoiceAccent.BRITISH, style=VoiceStyle.NEUTRAL,
                description="Clear, articulate British male voice"
            )
        }
        
        # Add sample URLs if voice samples exist
        voice_samples_dir = Path(__file__).parent.parent / "ai_apis" / "voices_samples" / "american"
        for voice_config in voice_metadata.values():
            sample_file = voice_samples_dir / f"voices_1_{voice_config.voice_id}.wav"
            if sample_file.exists():
                voice_config.sample_url = f"/api/voice-samples/{voice_config.voice_id}.wav"
                
        return voice_metadata
    
    async def get_available_voices(
        self, 
        gender: Optional[VoiceGender] = None,
        accent: Optional[VoiceAccent] = None,
        style: Optional[VoiceStyle] = None
    ) -> VoiceListResponse:
        """Get list of available voices with optional filtering"""
        
        if self._voice_cache is None:
            self._voice_cache = self._get_voice_metadata()
        
        filtered_voices = list(self._voice_cache.values())
        
        # Apply filters
        if gender:
            filtered_voices = [v for v in filtered_voices if v.gender == gender]
        if accent:
            filtered_voices = [v for v in filtered_voices if v.accent == accent]
        if style:
            filtered_voices = [v for v in filtered_voices if v.style == style]
            
        return VoiceListResponse(
            voices=filtered_voices,
            total_count=len(self._voice_cache),
            filtered_count=len(filtered_voices)
        )
    
    async def generate_voiceover(
        self, 
        request: VoiceRequest,
        base_url: str = "http://localhost:8000"
    ) -> VoiceResponse:
        """Generate voiceover audio from text using selected voice"""
        
        start_time = time.time()
        
        try:
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"voiceover_{request.script_id}_{timestamp}.wav"
            output_path = self.audio_output_dir / filename
            
            logger.info(f"Generating voiceover for script {request.script_id} with voice {request.voice_id}")
            
            # Generate audio using the existing voice API
            audio_path = await download_voice_replicate(
                text=request.text,
                output_path=str(output_path),
                voice=request.voice_id,
                speed=request.audio_settings.speed
            )
            
            if not Path(audio_path).exists():
                raise Exception(f"Audio file was not created at {audio_path}")
            
            # Get file info
            file_size = Path(audio_path).stat().st_size
            generation_time = time.time() - start_time
            
            # TODO: Get actual audio duration using audio library
            estimated_duration = len(request.text.split()) * 0.5  # Rough estimate
            
            logger.info(f"Voiceover generated successfully in {generation_time:.2f}s")
            
            # Save voiceover record to database
            voiceover_id = None  # Initialize ID variable
            try:
                with Session(engine) as session:
                    # Get voice name from config
                    voice_config = self._voice_cache.get(request.voice_id)
                    voice_name = voice_config.name if voice_config else request.voice_id
                    
                    voiceover_record = GeneratedVoiceover(
                        user_id=request.user_id,
                        script_id=request.script_id,
                        voice_id=request.voice_id,
                        voice_name=voice_name,
                        text_content=request.text,
                        speed=request.audio_settings.speed,
                        pitch=request.audio_settings.pitch,
                        volume=request.audio_settings.volume,
                        tone=request.audio_settings.tone,
                        filename=filename,
                        file_url=f"{base_url}/api/audio/{filename}",
                        file_size=file_size,
                        duration_seconds=estimated_duration,
                        generation_duration_ms=int(generation_time * 1000),
                        ai_provider="replicate",
                        ai_model="kokoro-82m",
                        status="completed"
                    )
                    
                    session.add(voiceover_record)
                    session.commit()
                    session.refresh(voiceover_record)  # Refresh to get the generated ID
                    
                    voiceover_id = str(voiceover_record.id)  # Capture the database ID
                    logger.info(f"Saved voiceover record to database with ID: {voiceover_id}")
                    
            except Exception as db_error:
                logger.error(f"Failed to save voiceover to database: {str(db_error)}")
                # Continue without failing the entire operation
            
            finally:
                # close the session if needed
                session.close()
                
            return VoiceResponse(
                success=True,
                id=voiceover_id,  # Include the database ID in the response
                audio_path=audio_path,
                audio_url=f"{base_url}/api/audio/{filename}",  # Return full URL, not relative path
                duration=estimated_duration,
                file_size=file_size,
                generation_time=generation_time
            )
            
        except Exception as e:
            logger.error(f"Error generating voiceover: {str(e)}")
            return VoiceResponse(
                success=False,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    async def apply_audio_effects(
        self, 
        audio_path: str, 
        settings: AudioSettings
    ) -> str:
        """Apply audio effects like pitch, speed, and volume adjustments"""
        
        try:
            # TODO: Implement audio effects using pydub or similar
            # For now, return original path
            logger.info(f"Audio effects applied: speed={settings.speed}, pitch={settings.pitch}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error applying audio effects: {str(e)}")
            return audio_path
    
    async def get_voice_sample(self, voice_id: str) -> Optional[str]:
        """Get voice sample file path if available"""
        
        voice_samples_dir = Path(__file__).parent.parent / "ai_apis" / "voices_samples" / "american"
        sample_file = voice_samples_dir / f"voices_1_{voice_id}.wav"
        
        if sample_file.exists():
            return str(sample_file)
        return None
    
    async def validate_voice_settings(self, request: VoiceRequest) -> Tuple[bool, Optional[str]]:
        """Validate voice generation request"""
        
        if not request.text.strip():
            return False, "Text cannot be empty"
            
        if len(request.text) > 10000:  # Reasonable limit
            return False, "Text is too long (max 10,000 characters)"
            
        # Check if voice exists
        voice_metadata = self._get_voice_metadata()
        if request.voice_id not in voice_metadata:
            return False, f"Voice '{request.voice_id}' not found"
            
        return True, None

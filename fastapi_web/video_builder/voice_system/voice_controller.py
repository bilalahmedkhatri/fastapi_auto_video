"""
Voice Controller - FastAPI endpoints for voice operations
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import FileResponse
from typing import Optional
import logging

from .voice_models import (
    VoiceRequest, VoiceResponse, VoiceListResponse, 
    VoiceVerificationRequest, VoiceGender, VoiceAccent, VoiceStyle
)
from .voice_service import VoiceService

logger = logging.getLogger(__name__)

# Create router
voice_router = APIRouter(prefix="/api/voice", tags=["voice"])

# Initialize service
voice_service = VoiceService()


class VoiceController:
    """Controller for voice-related endpoints"""
    
    def __init__(self, service: VoiceService):
        self.service = service
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @voice_router.get("/voices", response_model=VoiceListResponse)
        async def get_voices(
            gender: Optional[VoiceGender] = Query(None, description="Filter by gender"),
            accent: Optional[VoiceAccent] = Query(None, description="Filter by accent"),
            style: Optional[VoiceStyle] = Query(None, description="Filter by style")
        ):
            """Get list of available AI voices with filtering options"""
            try:
                return await self.service.get_available_voices(gender, accent, style)
            except Exception as e:
                logger.error(f"Error fetching voices: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @voice_router.post("/generate", response_model=VoiceResponse)
        async def generate_voiceover(request: VoiceRequest, req: Request):
            """Generate voiceover audio from text using selected voice"""
            try:
                # Validate request
                is_valid, error_msg = await self.service.validate_voice_settings(request)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error_msg)
                
                # Auto-detect base URL from request
                base_url = f"{req.url.scheme}://{req.url.netloc}"
                
                return await self.service.generate_voiceover(request, base_url=base_url)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error generating voiceover: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @voice_router.get("/sample/{voice_id}")
        async def get_voice_sample(voice_id: str):
            """Get voice sample audio file"""
            try:
                sample_path = await self.service.get_voice_sample(voice_id)
                if not sample_path:
                    raise HTTPException(status_code=404, detail="Voice sample not found")
                
                return FileResponse(
                    sample_path,
                    media_type="audio/wav",
                    filename=f"{voice_id}_sample.wav"
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting voice sample: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @voice_router.post("/verify", response_model=VoiceResponse)
        async def verify_voiceover(request: VoiceVerificationRequest):
            """Verify generated voiceover and optionally regenerate with new settings"""
            try:
                if request.approved:
                    return VoiceResponse(
                        success=True,
                        audio_path=request.audio_path,
                        audio_url=request.audio_path.replace("media/", "/api/")
                    )
                
                if request.regenerate and request.new_settings:
                    # TODO: Implement regeneration with new settings
                    logger.info("Regenerating voiceover with new settings")
                    return VoiceResponse(
                        success=True,
                        audio_path=request.audio_path
                    )
                
                return VoiceResponse(
                    success=False,
                    error_message="Voiceover not approved and no regeneration requested"
                )
                
            except Exception as e:
                logger.error(f"Error verifying voiceover: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @voice_router.get("/audio/{filename}")
        async def serve_audio_file(filename: str):
            """Serve generated audio files"""
            try:
                audio_path = self.service.audio_output_dir / filename
                if not audio_path.exists():
                    raise HTTPException(status_code=404, detail="Audio file not found")
                
                return FileResponse(
                    audio_path,
                    media_type="audio/wav",
                    filename=filename
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error serving audio file: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))


# Initialize controller
voice_controller = VoiceController(voice_service)

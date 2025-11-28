"""
Create voiceover endpoint
POST /api/voiceover/create
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel, Field
from typing import Optional
import time
from pathlib import Path

from models.db_models import GeneratedVoiceover, SelectAIVoices, get_session
from kokoro_82M.model_cache import get_cached_generator

router = APIRouter()


class CreateVoiceoverRequest(BaseModel):
    """Request model for creating voiceover"""
    user_id: str
    text: str
    voice_id: str
    script_id: Optional[str] = None
    video_id: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    volume: float = Field(default=0.8, ge=0.1, le=2.0)
    tone: Optional[str] = "neutral"


class CreateVoiceoverResponse(BaseModel):
    """Response model for voiceover creation"""
    id: str
    audio_url: str
    filename: str
    duration_seconds: float
    file_size: int
    generation_time_ms: int


@router.post("/create", response_model=CreateVoiceoverResponse)
async def create_voiceover(
    request: CreateVoiceoverRequest,
    session: Session = Depends(get_session)
):
    """
    Generate voiceover using local Kokoro-82M model
    
    - Validates voice exists in database
    - Generates audio using local Kokoro generator
    - Saves metadata to GeneratedVoiceover table
    """
    start_time = time.time()
    
    try:
        # Validate voice exists in database
        voice = session.query(SelectAIVoices).filter(
            SelectAIVoices.voice_id == request.voice_id,
            SelectAIVoices.is_active == True
        ).first()
        
        if not voice:
            raise HTTPException(
                status_code=404, 
                detail=f"Voice '{request.voice_id}' not found or inactive"
            )
        
        # Validate text
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text too long (max 10,000 characters)")
        
        # Generate voiceover using cached Kokoro model (faster after first request)
        generator = get_cached_generator()
        audio_path, metadata = generator.generate_voice(
            text=request.text,
            voice_type=request.voice_id,
            output_dir="media/audio",
            speed=request.speed,
            normalize=True,
            save_metadata=True
        )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to database
        voiceover = GeneratedVoiceover(
            user_id=request.user_id,
            script_id=request.script_id,
            video_id=request.video_id,
            voice_id=request.voice_id,
            voice_name=voice.voice_name,
            text_content=request.text,
            speed=request.speed,
            pitch=request.pitch,
            volume=request.volume,
            tone=request.tone,
            filename=Path(audio_path).name,
            file_url=f"/api/voiceover/audio/{Path(audio_path).name}",
            file_size=metadata["file_size_bytes"],
            duration_seconds=metadata["duration_seconds"],
            generation_duration_ms=generation_time_ms,
            ai_provider="kokoro-local",
            ai_model="kokoro-82m",
            status="completed"
        )
        
        session.add(voiceover)
        session.commit()
        session.refresh(voiceover)
        
        return CreateVoiceoverResponse(
            id=voiceover.id,
            audio_url=voiceover.file_url,
            filename=voiceover.filename,
            duration_seconds=voiceover.duration_seconds,
            file_size=voiceover.file_size,
            generation_time_ms=generation_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

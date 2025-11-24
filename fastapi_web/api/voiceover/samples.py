"""
Voiceover samples endpoint
GET /api/voiceover/voiceover_samples
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import os

from models.db_models import SelectAIVoices, get_session
from kokoro_82M.generators import KokoroVoiceGenerator
from kokoro_82M.config import KOKORO_CONFIG

router = APIRouter()

base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
# Initialize generator for sample creation
kokoro_generator = KokoroVoiceGenerator(
    output_base_dir="media/voice_samples"
)


class VoiceSample(BaseModel):
    """Voice sample information"""
    voice_id: str
    voice_name: str
    gender: Optional[str]
    accent: Optional[str]
    language: str
    description: Optional[str]
    sample_url: Optional[str]
    provider: str
    model_name: str
    is_active: bool


class VoiceSamplesResponse(BaseModel):
    """Response model for voice samples list"""
    voices: List[VoiceSample]
    total: int
    language: Optional[str]


@router.get("/voiceover_samples", response_model=VoiceSamplesResponse)
async def get_voiceover_samples(
    language: Optional[str] = Query("en", description="Language code (en, es, fr, etc.)"),
    gender: Optional[str] = Query(None, description="Filter by gender (male, female)"),
    accent: Optional[str] = Query(None, description="Filter by accent (American, British, etc.)"),
    session: Session = Depends(get_session)
):
    """
    Get available voice samples with filtering
    
    - Lists all active voices from SelectAIVoices table
    - Filters by language, gender, accent
    - Returns voice metadata and sample URLs
    """
    # Build query
    query = select(SelectAIVoices).where(SelectAIVoices.is_active == True)
    
    if language:
        query = query.where(SelectAIVoices.language == language)
    if gender:
        query = query.where(SelectAIVoices.gender == gender)
    if accent:
        query = query.where(SelectAIVoices.accent == accent)
    
    voices = session.exec(query).all()
    
    return VoiceSamplesResponse(
        voices=[
            VoiceSample(
                voice_id=v.voice_id,
                voice_name=v.voice_name,
                gender=v.gender,
                accent=v.accent,
                language=v.language,
                description=v.voice_description,
                sample_url=f"{base_url}{v.voice_sample_url}",
                provider=v.provider or "kokoro-local",
                model_name=v.model_name or KOKORO_CONFIG["model_name"],
                is_active=v.is_active
            )
            for v in voices
        ],
        total=len(voices),
        language=language
    )


@router.get("/voiceover_samples/audio/{voice_id}")
async def get_voice_sample_audio(
    voice_id: str,
    session: Session = Depends(get_session)
):
    """
    Get voice sample audio file
    
    - Returns WAV file for voice preview
    - Generates sample if not exists
    """
    # Check if voice exists
    voice = session.query(SelectAIVoices).filter(
        SelectAIVoices.voice_id == voice_id,
        SelectAIVoices.is_active == True
    ).first()
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    # Check for existing sample
    sample_path = Path("media/voice_samples") / f"{voice_id}_sample.wav"
    
    # Generate sample if doesn't exist
    if not sample_path.exists():
        sample_text = "Hello, this is a sample of my voice. I can help you create engaging voiceovers for your videos."
        
        try:
            audio_path, _ = kokoro_generator.generate_voice(
                text=sample_text,
                voice_type=voice_id,
                filename=f"{voice_id}_sample",
                speed=1.0,
                normalize=True,
                save_metadata=False
            )
            sample_path = Path(audio_path)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate voice sample: {str(e)}"
            )
    
    return FileResponse(
        sample_path,
        media_type="audio/wav",
        filename=f"{voice_id}_sample.wav"
    )


@router.post("/voiceover_samples/generate/{voice_id}")
async def generate_voice_sample(
    voice_id: str,
    text: str = Query("Hello, this is a sample of my voice.", description="Text for sample generation"),
    session: Session = Depends(get_session)
):
    """
    Generate custom voice sample with provided text
    
    - Creates new sample audio with custom text
    - Returns sample URL
    """
    # Check if voice exists
    voice = session.query(SelectAIVoices).filter(
        SelectAIVoices.voice_id == voice_id,
        SelectAIVoices.is_active == True
    ).first()
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        audio_path, metadata = kokoro_generator.generate_voice(
            text=text,
            voice_type=voice_id,
            filename=f"{voice_id}_sample",
            speed=1.0,
            normalize=True,
            save_metadata=False
        )
        
        return {
            "voice_id": voice_id,
            "sample_url": f"/api/voiceover/voiceover_samples/audio/{voice_id}",
            "duration_seconds": metadata["duration_seconds"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate sample: {str(e)}"
        )

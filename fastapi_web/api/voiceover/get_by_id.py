"""
Get voiceover by ID endpoint
GET /api/voiceover/get_by_id/{voiceover_id}
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.db_models import GeneratedVoiceover, get_session

router = APIRouter()


class GetVoiceoverResponse(BaseModel):
    """Response model for single voiceover"""
    id: str
    user_id: str
    script_id: Optional[str]
    video_id: Optional[str]
    voice_id: str
    voice_name: str
    text_content: str
    speed: float
    pitch: float
    volume: float
    tone: Optional[str]
    filename: str
    file_url: str
    file_size: Optional[int]
    duration_seconds: Optional[float]
    generation_duration_ms: Optional[int]
    ai_provider: Optional[str]
    ai_model: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


@router.get("/get_by_id/{voiceover_id}", response_model=GetVoiceoverResponse)
async def get_voiceover_by_id(
    voiceover_id: str,
    session: Session = Depends(get_session)
):
    """
    Get specific voiceover by ID
    
    - Returns complete voiceover metadata
    - Includes all generation details
    """
    voiceover = session.get(GeneratedVoiceover, voiceover_id)
    
    if not voiceover:
        raise HTTPException(status_code=404, detail="Voiceover not found")
    
    return GetVoiceoverResponse(
        id=voiceover.id,
        user_id=voiceover.user_id,
        script_id=voiceover.script_id,
        video_id=voiceover.video_id,
        voice_id=voiceover.voice_id,
        voice_name=voiceover.voice_name,
        text_content=voiceover.text_content,
        speed=voiceover.speed,
        pitch=voiceover.pitch,
        volume=voiceover.volume,
        tone=voiceover.tone,
        filename=voiceover.filename,
        file_url=voiceover.file_url,
        file_size=voiceover.file_size,
        duration_seconds=voiceover.duration_seconds,
        generation_duration_ms=voiceover.generation_duration_ms,
        ai_provider=voiceover.ai_provider,
        ai_model=voiceover.ai_model,
        status=voiceover.status,
        created_at=voiceover.created_at,
        updated_at=voiceover.updated_at
    )

"""
Get all voiceovers endpoint
GET /api/voiceover/get_all
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.db_models import GeneratedVoiceover, get_session

router = APIRouter()


class VoiceoverItem(BaseModel):
    """Single voiceover item"""
    id: str
    user_id: str
    voice_id: str
    voice_name: str
    text_content: str
    filename: str
    file_url: str
    duration_seconds: Optional[float]
    file_size: Optional[int]
    speed: float
    status: str
    created_at: datetime


class GetAllVoiceoversResponse(BaseModel):
    """Response model for get all voiceovers"""
    voiceovers: List[VoiceoverItem]
    total: int
    page: int
    per_page: int


@router.get("/get_all", response_model=GetAllVoiceoversResponse)
async def get_all_voiceovers(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    script_id: Optional[str] = Query(None, description="Filter by script ID"),
    video_id: Optional[str] = Query(None, description="Filter by video ID"),
    voice_id: Optional[str] = Query(None, description="Filter by voice ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """
    Get all voiceovers with optional filtering
    
    - Supports pagination
    - Filters by user_id, script_id, video_id, voice_id
    - Returns most recent first
    """
    # Build query
    query = select(GeneratedVoiceover)
    
    if user_id:
        query = query.where(GeneratedVoiceover.user_id == user_id)
    if script_id:
        query = query.where(GeneratedVoiceover.script_id == script_id)
    if video_id:
        query = query.where(GeneratedVoiceover.video_id == video_id)
    if voice_id:
        query = query.where(GeneratedVoiceover.voice_id == voice_id)
    
    # Get total count
    count_query = select(GeneratedVoiceover.id)
    if user_id:
        count_query = count_query.where(GeneratedVoiceover.user_id == user_id)
    if script_id:
        count_query = count_query.where(GeneratedVoiceover.script_id == script_id)
    if video_id:
        count_query = count_query.where(GeneratedVoiceover.video_id == video_id)
    if voice_id:
        count_query = count_query.where(GeneratedVoiceover.voice_id == voice_id)
    
    total = len(session.exec(count_query).all())
    
    # Add ordering and pagination
    query = query.order_by(GeneratedVoiceover.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    voiceovers = session.exec(query).all()
    
    return GetAllVoiceoversResponse(
        voiceovers=[
            VoiceoverItem(
                id=v.id,
                user_id=v.user_id,
                voice_id=v.voice_id,
                voice_name=v.voice_name,
                text_content=v.text_content,
                filename=v.filename,
                file_url=v.file_url,
                duration_seconds=v.duration_seconds,
                file_size=v.file_size,
                speed=v.speed,
                status=v.status,
                created_at=v.created_at
            )
            for v in voiceovers
        ],
        total=total,
        page=page,
        per_page=per_page
    )

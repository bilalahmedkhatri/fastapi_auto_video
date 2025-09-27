from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from models.db_models import GeneratedVoiceover, get_session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create the router
voiceover_router = APIRouter(prefix="/api/voiceovers", tags=["voiceovers"])

# Pydantic models for API requests/responses
class VoiceoverCreateRequest(BaseModel):
    user_id: str
    script_id: Optional[str] = None
    video_id: Optional[str] = None
    voice_id: str
    voice_name: str
    text_content: str
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 0.8
    tone: Optional[str] = None
    filename: str
    file_url: str
    file_size: Optional[int] = None
    duration_seconds: Optional[float] = None
    generation_duration_ms: Optional[int] = None
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

class VoiceoverResponse(BaseModel):
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
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class VoiceoverListResponse(BaseModel):
    voiceovers: List[VoiceoverResponse]
    total: int
    page: int
    per_page: int

@voiceover_router.post("/", response_model=VoiceoverResponse)
async def create_voiceover(
    voiceover_data: VoiceoverCreateRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new voiceover record in the database
    """
    try:
        # Create the voiceover record
        voiceover = GeneratedVoiceover(
            user_id=voiceover_data.user_id,
            script_id=voiceover_data.script_id,
            video_id=voiceover_data.video_id,
            voice_id=voiceover_data.voice_id,
            voice_name=voiceover_data.voice_name,
            text_content=voiceover_data.text_content,
            speed=voiceover_data.speed,
            pitch=voiceover_data.pitch,
            volume=voiceover_data.volume,
            tone=voiceover_data.tone,
            filename=voiceover_data.filename,
            file_url=voiceover_data.file_url,
            file_size=voiceover_data.file_size,
            duration_seconds=voiceover_data.duration_seconds,
            generation_duration_ms=voiceover_data.generation_duration_ms,
            ai_provider=voiceover_data.ai_provider,
            ai_model=voiceover_data.ai_model,
            status="completed"
        )
        
        session.add(voiceover)
        session.commit()
        session.refresh(voiceover)
        
        logger.info(f"Voiceover record created: {voiceover.id} for user {voiceover.user_id}")
        
        return VoiceoverResponse(
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
            error_message=voiceover.error_message,
            created_at=voiceover.created_at,
            updated_at=voiceover.updated_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create voiceover record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create voiceover record: {str(e)}")

@voiceover_router.get("/", response_model=VoiceoverListResponse)
async def get_voiceovers(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    script_id: Optional[str] = Query(None, description="Filter by script ID"),
    video_id: Optional[str] = Query(None, description="Filter by video ID"),
    voice_id: Optional[str] = Query(None, description="Filter by voice ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session)
):
    """
    Get voiceovers with optional filtering and pagination
    """
    try:
        # Build query with filters
        query = select(GeneratedVoiceover)
        
        if user_id:
            query = query.where(GeneratedVoiceover.user_id == user_id)
        if script_id:
            query = query.where(GeneratedVoiceover.script_id == script_id)
        if video_id:
            query = query.where(GeneratedVoiceover.video_id == video_id)
        if voice_id:
            query = query.where(GeneratedVoiceover.voice_id == voice_id)
        
        # Add ordering (most recent first)
        query = query.order_by(GeneratedVoiceover.created_at.desc())
        
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
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        voiceovers = session.exec(query).all()
        
        # Convert to response models
        voiceover_responses = [
            VoiceoverResponse(
                id=vo.id,
                user_id=vo.user_id,
                script_id=vo.script_id,
                video_id=vo.video_id,
                voice_id=vo.voice_id,
                voice_name=vo.voice_name,
                text_content=vo.text_content,
                speed=vo.speed,
                pitch=vo.pitch,
                volume=vo.volume,
                tone=vo.tone,
                filename=vo.filename,
                file_url=vo.file_url,
                file_size=vo.file_size,
                duration_seconds=vo.duration_seconds,
                generation_duration_ms=vo.generation_duration_ms,
                ai_provider=vo.ai_provider,
                ai_model=vo.ai_model,
                status=vo.status,
                error_message=vo.error_message,
                created_at=vo.created_at,
                updated_at=vo.updated_at
            )
            for vo in voiceovers
        ]
        
        return VoiceoverListResponse(
            voiceovers=voiceover_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch voiceovers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch voiceovers: {str(e)}")

@voiceover_router.get("/{voiceover_id}", response_model=VoiceoverResponse)
async def get_voiceover(
    voiceover_id: str,
    session: Session = Depends(get_session)
):
    """
    Get a specific voiceover by ID
    """
    try:
        voiceover = session.get(GeneratedVoiceover, voiceover_id)
        
        if not voiceover:
            raise HTTPException(status_code=404, detail="Voiceover not found")
        
        return VoiceoverResponse(
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
            error_message=voiceover.error_message,
            created_at=voiceover.created_at,
            updated_at=voiceover.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch voiceover {voiceover_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch voiceover: {str(e)}")

@voiceover_router.delete("/{voiceover_id}")
async def delete_voiceover(
    voiceover_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a voiceover record and optionally the audio file
    """
    try:
        voiceover = session.get(GeneratedVoiceover, voiceover_id)
        
        if not voiceover:
            raise HTTPException(status_code=404, detail="Voiceover not found")
        
        # Optionally delete the actual audio file
        file_path = f"media/audio/{voiceover.filename}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted audio file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete audio file {file_path}: {str(e)}")
        
        # Delete the database record
        session.delete(voiceover)
        session.commit()
        
        logger.info(f"Deleted voiceover record: {voiceover_id}")
        
        return {"message": "Voiceover deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete voiceover {voiceover_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete voiceover: {str(e)}")

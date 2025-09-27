"""
Example API endpoints for managing AI voices
Add these to your main FastAPI app
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select
from typing import List, Optional
import os
from pathlib import Path

from models.db_models import SelectAIVoices, VideoVoiceSelection, get_session

# Create router for voice-related endpoints
voice_router = APIRouter(prefix="/api/voices", tags=["voices"])

# Define the path where demo voice samples are stored
VOICE_SAMPLES_DIR = Path("media/voice_samples_real")  # Updated to use renamed files

@voice_router.get("/", response_model=List[SelectAIVoices])
async def get_all_voices(
    session: Session = Depends(get_session),
    language: Optional[str] = None,
    gender: Optional[str] = None,
    is_demo: Optional[bool] = None,
    provider: Optional[str] = None
):
    """Get all available AI voices with optional filtering"""
    
    query = select(SelectAIVoices).where(SelectAIVoices.is_active == True)
    
    if language:
        query = query.where(SelectAIVoices.language == language)
    if gender:
        query = query.where(SelectAIVoices.gender == gender)
    if is_demo is not None:
        query = query.where(SelectAIVoices.is_demo == is_demo)
    if provider:
        query = query.where(SelectAIVoices.provider == provider)
    
    voices = session.exec(query).all()
    return voices

@voice_router.get("/{voice_id}", response_model=SelectAIVoices)
async def get_voice_by_id(voice_id: str, session: Session = Depends(get_session)):
    """Get a specific voice by its ID"""
    
    voice = session.exec(
        select(SelectAIVoices).where(SelectAIVoices.voice_id == voice_id)
    ).first()
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return voice

@voice_router.get("/samples/{voice_id}.wav")
async def get_voice_sample(voice_id: str):
    """Serve voice sample file"""
    
    sample_path = VOICE_SAMPLES_DIR / f"{voice_id}.wav"
    
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Voice sample not found: {voice_id}.wav")
    
    # Read and return the audio file
    with open(sample_path, "rb") as audio_file:
        audio_content = audio_file.read()
    
    return Response(
        content=audio_content,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"inline; filename={voice_id}.wav"
        }
    )

@voice_router.post("/videos/{video_id}/select/{voice_id}")
async def select_voice_for_video(
    video_id: str, 
    voice_id: str, 
    session: Session = Depends(get_session)
):
    """Select a voice for a specific video"""
    
    # Verify voice exists
    voice = session.exec(
        select(SelectAIVoices).where(SelectAIVoices.voice_id == voice_id)
    ).first()
    
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    # Deactivate any existing voice selection for this video
    existing_selections = session.exec(
        select(VideoVoiceSelection).where(VideoVoiceSelection.video_id == video_id)
    ).all()
    
    for selection in existing_selections:
        selection.is_active = False
    
    # Create new voice selection
    new_selection = VideoVoiceSelection(
        video_id=video_id,
        voice_id=voice_id,
        is_active=True
    )
    
    session.add(new_selection)
    session.commit()
    session.refresh(new_selection)
    
    return {
        "message": f"Voice {voice_id} selected for video {video_id}",
        "selection_id": new_selection.id,
        "voice_name": voice.voice_name
    }

@voice_router.get("/videos/{video_id}/selected")
async def get_selected_voice_for_video(
    video_id: str, 
    session: Session = Depends(get_session)
):
    """Get the currently selected voice for a video"""
    
    selection = session.exec(
        select(VideoVoiceSelection)
        .where(VideoVoiceSelection.video_id == video_id)
        .where(VideoVoiceSelection.is_active == True)
    ).first()
    
    if not selection:
        raise HTTPException(status_code=404, detail="No voice selected for this video")
    
    voice = session.exec(
        select(SelectAIVoices).where(SelectAIVoices.voice_id == selection.voice_id)
    ).first()
    
    return {
        "selection_id": selection.id,
        "voice": voice,
        "selected_at": selection.selected_at
    }

# Example usage in your main.py:
# from voice_api import voice_router
# app.include_router(voice_router)

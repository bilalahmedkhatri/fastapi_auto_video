"""
Update voiceover by ID endpoint
PUT /api/voiceover/update_by_id/{voiceover_id}
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.db_models import GeneratedVoiceover, get_session

router = APIRouter()


class UpdateVoiceoverRequest(BaseModel):
    """Request model for updating voiceover metadata"""
    text_content: Optional[str] = None
    speed: Optional[float] = None
    pitch: Optional[float] = None
    volume: Optional[float] = None
    tone: Optional[str] = None
    status: Optional[str] = None


class UpdateVoiceoverResponse(BaseModel):
    """Response model for update operation"""
    id: str
    message: str
    updated_at: datetime


@router.put("/update_by_id/{voiceover_id}", response_model=UpdateVoiceoverResponse)
async def update_voiceover_by_id(
    voiceover_id: str,
    request: UpdateVoiceoverRequest,
    session: Session = Depends(get_session)
):
    """
    Update voiceover metadata
    
    - Updates only provided fields
    - Updates timestamp automatically
    - Does not regenerate audio
    """
    voiceover = session.get(GeneratedVoiceover, voiceover_id)
    
    if not voiceover:
        raise HTTPException(status_code=404, detail="Voiceover not found")
    
    # Update only provided fields
    if request.text_content is not None:
        voiceover.text_content = request.text_content
    if request.speed is not None:
        voiceover.speed = request.speed
    if request.pitch is not None:
        voiceover.pitch = request.pitch
    if request.volume is not None:
        voiceover.volume = request.volume
    if request.tone is not None:
        voiceover.tone = request.tone
    if request.status is not None:
        voiceover.status = request.status
    
    voiceover.updated_at = datetime.now()
    
    session.add(voiceover)
    session.commit()
    session.refresh(voiceover)
    
    return UpdateVoiceoverResponse(
        id=voiceover.id,
        message="Voiceover updated successfully",
        updated_at=voiceover.updated_at
    )

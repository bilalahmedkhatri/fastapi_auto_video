"""
Delete voiceover by ID endpoint
DELETE /api/voiceover/delete_by_id/{voiceover_id}
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel
from pathlib import Path
import logging

from models.db_models import GeneratedVoiceover, get_session

router = APIRouter()
logger = logging.getLogger(__name__)


class DeleteVoiceoverResponse(BaseModel):
    """Response model for delete operation"""
    id: str
    message: str
    file_deleted: bool


@router.delete("/delete_by_id/{voiceover_id}", response_model=DeleteVoiceoverResponse)
async def delete_voiceover_by_id(
    voiceover_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete voiceover record and audio file
    
    - Removes database record
    - Deletes audio file from disk
    - Deletes metadata file if exists
    """
    voiceover = session.get(GeneratedVoiceover, voiceover_id)
    
    if not voiceover:
        raise HTTPException(status_code=404, detail="Voiceover not found")
    
    # Delete audio file
    file_deleted = False
    audio_path = Path("media/audio") / voiceover.filename
    
    if audio_path.exists():
        try:
            audio_path.unlink()
            file_deleted = True
            logger.info(f"Deleted audio file: {audio_path}")
            
            # Also delete metadata JSON if exists
            metadata_path = audio_path.with_suffix('.json')
            if metadata_path.exists():
                metadata_path.unlink()
                logger.info(f"Deleted metadata file: {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to delete audio file: {str(e)}")
    
    # Delete database record
    session.delete(voiceover)
    session.commit()
    
    return DeleteVoiceoverResponse(
        id=voiceover_id,
        message="Voiceover deleted successfully",
        file_deleted=file_deleted
    )

"""
Free Voiceover Tool API - Public endpoint for generating voiceovers without authentication
Includes rate limiting (3 uses per 12 hours per IP) and automatic file cleanup
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field, validator
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from typing import Optional
import os

from models.db_models import SelectAIVoices, GeneratedVoiceover, FreeVoiceoverUsage, get_session
from kokoro_82M.model_cache import get_cached_generator

router = APIRouter()


class FreeVoiceoverRequest(BaseModel):
    """Request model for free voiceover generation"""
    text: str = Field(..., description="Text to convert to speech")
    voice_id: str = Field(..., description="Voice ID from the voice catalog")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    pitch: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Voice pitch (0.5-2.0)")
    volume: Optional[float] = Field(0.8, ge=0.1, le=2.0, description="Audio volume (0.1-2.0)")
    tone: Optional[str] = Field("neutral", description="Voice tone/emotion")

    @validator('text')
    def validate_text(cls, v):
        """Validate text is not empty and within length limits"""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 10000:
            raise ValueError("Text cannot exceed 10,000 characters")
        return v.strip()


class FreeVoiceoverResponse(BaseModel):
    """Response model for free voiceover generation"""
    id: str
    audio_url: str
    voice_name: str
    duration_seconds: float
    file_size: int
    expires_at: datetime
    remaining_uses: int
    reset_at: Optional[datetime] = None


class RateLimitExceeded(BaseModel):
    """Response when rate limit is exceeded"""
    error: str
    retry_after: datetime
    message: str


def get_client_identifier(request: Request) -> str:
    """
    Extract client identifier (IP address) from request
    Handles proxies and load balancers
    """
    # Try to get real IP from headers (for proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"


def check_rate_limit(identifier: str, session: Session) -> tuple[bool, int, Optional[datetime]]:
    """
    Check if user has exceeded rate limit
    
    Args:
        identifier: Client IP address
        session: Database session
    
    Returns:
        Tuple of (is_allowed, remaining_uses, reset_at)
        - is_allowed: True if user can generate, False if limit exceeded
        - remaining_uses: Number of generations remaining (0-3)
        - reset_at: Timestamp when limit resets (only if is_allowed=False)
    """
    # Define time window (12 hours from now)
    time_window = datetime.now() - timedelta(hours=12)
    
    # Count usages in the last 12 hours that haven't been deleted
    usage_count = session.exec(
        select(func.count(FreeVoiceoverUsage.id))
        .where(FreeVoiceoverUsage.identifier == identifier)
        .where(FreeVoiceoverUsage.generated_at >= time_window)
        .where(FreeVoiceoverUsage.is_deleted == False)
    ).one()
    
    # Calculate remaining uses (max 3)
    remaining_uses = max(0, 100 - usage_count)
    
    # If usage count is 3 or more, rate limit is exceeded
    if usage_count >= 100:
        # Find the oldest usage to calculate when the limit will reset
        oldest_usage = session.exec(
            select(FreeVoiceoverUsage)
            .where(FreeVoiceoverUsage.identifier == identifier)
            .where(FreeVoiceoverUsage.generated_at >= time_window)
            .where(FreeVoiceoverUsage.is_deleted == False)
            .order_by(FreeVoiceoverUsage.generated_at)
        ).first()
        
        if oldest_usage:
            # Reset time is 12 hours after the oldest usage
            reset_at = oldest_usage.generated_at + timedelta(hours=12)
            # Return False - rate limit exceeded
            return False, 0, reset_at
        else:
            # No usage found but count >= 3 (shouldn't happen, but handle it)
            return False, 0, datetime.now() + timedelta(hours=12)
    
    # Rate limit not exceeded - user is allowed to generate
    # Return True with remaining uses
    return True, remaining_uses, None


@router.post("/free_tool", response_model=FreeVoiceoverResponse, responses={
    429: {"model": RateLimitExceeded, "description": "Rate limit exceeded"}
})
async def generate_free_voiceover(
    request: Request,
    voiceover_request: FreeVoiceoverRequest,
    session: Session = Depends(get_session)
):
    """
    Generate a voiceover using the free tool (no authentication required)
    
    **Rate Limit**: 3 generations per 12 hours per IP address
    **File Retention**: Files are automatically deleted after 1 hour
    
    Parameters:
    - **text**: Text to convert to speech (1-10,000 characters)
    - **voice_id**: Voice ID from the voice catalog (get from /api/voiceover/voiceover_samples)
    - **speed**: Speech speed multiplier (0.5-2.0, default: 1.0)
    - **pitch**: Voice pitch adjustment (0.5-2.0, default: 1.0)
    - **volume**: Audio volume level (0.1-2.0, default: 0.8)
    - **tone**: Voice tone/emotion (default: "neutral")
    
    Returns:
    - Audio file URL, metadata, expiration time, and remaining uses
    
    Raises:
    - 400: Invalid input (empty text, text too long, invalid voice_id)
    - 429: Rate limit exceeded (wait 12 hours from first use)
    - 500: Voice generation failed
    """
    # Get client identifier (IP address)
    identifier = get_client_identifier(request)
    
    # Check rate limit - if False, user has exceeded limit
    is_allowed, remaining_uses, reset_at = check_rate_limit(identifier, session)
    
    # If rate limit exceeded, return error immediately
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "retry_after": reset_at.isoformat() if reset_at else None,
                "message": f"You have exceeded the free tier limit of 3 generations per 12 hours. Please try again after {reset_at.strftime('%Y-%m-%d %H:%M:%S UTC') if reset_at else 'some time'}."
            }
        )
    
    # Only proceed if is_allowed is True
    # Validate voice exists and is active
    voice = session.exec(
        select(SelectAIVoices)
        .where(SelectAIVoices.voice_id == voiceover_request.voice_id)
        .where(SelectAIVoices.is_active == True)
    ).first()
    
    if not voice:
        raise HTTPException(
            status_code=404,
            detail=f"Voice with ID '{voiceover_request.voice_id}' not found or inactive"
        )
    
    # Create temporary directory if it doesn't exist
    temp_dir = "media/temp/voiceovers"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate voiceover using cached Kokoro model (fast - no reload!)
    try:
        # Get cached generator instance (instant if already loaded)
        generator = get_cached_generator()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"free_{timestamp}_{voiceover_request.voice_id}.wav"
        
        # Generate voice
        audio_file_path, result = generator.generate_voice(
            text=voiceover_request.text,
            voice_type=voiceover_request.voice_id,
            speed=voiceover_request.speed,
            normalize=True
        )
        
        # Move generated file to temp directory
        source_path = audio_file_path
        dest_path = os.path.join(temp_dir, filename)
        
        # If file was generated in different location, move it
        if os.path.abspath(source_path) != os.path.abspath(dest_path):
            import shutil
            shutil.move(source_path, dest_path)
        
        # Get file size and duration
        file_size = os.path.getsize(dest_path)
        duration_seconds = result.get("duration_seconds", 0.0)
        
        # Build complete URL with domain
        base_url = str(request.base_url).rstrip('/')
        complete_audio_url = f"{base_url}/media/temp/voiceovers/{filename}"
        
        # Create GeneratedVoiceover record (without user_id)
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        voiceover = GeneratedVoiceover(
            user_id=None,  # No user for free tool
            voice_id=voiceover_request.voice_id,
            voice_name=voice.voice_name,
            text_content=voiceover_request.text,
            speed=voiceover_request.speed,
            pitch=voiceover_request.pitch,
            volume=voiceover_request.volume,
            tone=voiceover_request.tone,
            filename=filename,
            file_url=complete_audio_url,
            file_size=file_size,
            duration_seconds=duration_seconds,
            generation_duration_ms=0,  # Not tracked in new generator
            ai_provider="kokoro",
            ai_model="kokoro-82m",
            status="completed"
        )
        session.add(voiceover)
        session.commit()
        session.refresh(voiceover)
        
        # Record usage for rate limiting
        usage = FreeVoiceoverUsage(
            identifier=identifier,
            voiceover_id=voiceover.id,
            generated_at=now,
            expires_at=expires_at,
            is_deleted=False
        )
        session.add(usage)
        session.commit()
        
        # Calculate new remaining uses
        new_remaining = remaining_uses - 1
        
        # Calculate reset_at if this was the last use
        reset_at_response = None
        if new_remaining == 0:
            reset_at_response = now + timedelta(hours=12)
        
        return FreeVoiceoverResponse(
            id=voiceover.id,
            audio_url=complete_audio_url,
            voice_name=voice.voice_name,
            duration_seconds=duration_seconds,
            file_size=file_size,
            expires_at=expires_at,
            remaining_uses=new_remaining,
            reset_at=reset_at_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Voice generation error: {str(e)}"
        )

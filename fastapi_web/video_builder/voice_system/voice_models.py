"""
Data models for voice system
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class VoiceAccent(str, Enum):
    AMERICAN = "American_English"
    BRITISH = "British_English"
    JAPANESE = "Japanese"
    MANDARIN = "Mandarin_Chinese"
    SPANISH = "Spanish"
    FRENCH = "French"
    HINDI = "Hindi"
    ITALIAN = "Italian"
    PORTUGUESE = "Brazilian Portuguese"


class VoiceStyle(str, Enum):
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"


class VoiceConfig(BaseModel):
    """Voice configuration with detailed metadata"""
    voice_id: str
    name: str
    gender: VoiceGender
    accent: VoiceAccent
    style: VoiceStyle = VoiceStyle.NEUTRAL
    description: str
    sample_url: Optional[str] = None
    is_premium: bool = False
    
    class Config:
        use_enum_values = True


class AudioSettings(BaseModel):
    """Audio processing settings"""
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: int = Field(default=0, ge=-20, le=20, description="Pitch adjustment in semitones")
    tone: str = Field(default="neutral", description="Voice tone/emotion")
    volume: float = Field(default=1.0, ge=0.1, le=2.0, description="Volume multiplier")
    

class BackgroundMusicConfig(BaseModel):
    """Background music configuration"""
    enabled: bool = False
    music_type: str = "upbeat"  # upbeat, calm, dramatic, corporate, etc.
    volume: float = Field(default=0.3, ge=0.0, le=1.0)
    fade_in: float = Field(default=2.0, ge=0.0, le=10.0)
    fade_out: float = Field(default=2.0, ge=0.0, le=10.0)


class VoiceRequest(BaseModel):
    """Request model for voice generation"""
    script_id: str
    text: str
    voice_id: str
    audio_settings: AudioSettings = AudioSettings()
    background_music: BackgroundMusicConfig = BackgroundMusicConfig()
    user_id: str
    

class VoiceResponse(BaseModel):
    """Response model for voice generation"""
    success: bool
    audio_url: Optional[str] = None
    audio_path: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
    

class VoiceListResponse(BaseModel):
    """Response model for listing available voices"""
    voices: List[VoiceConfig]
    total_count: int
    filtered_count: int
    

class VoiceVerificationRequest(BaseModel):
    """Request model for voice verification"""
    audio_path: str
    approved: bool
    regenerate: bool = False
    new_settings: Optional[AudioSettings] = None

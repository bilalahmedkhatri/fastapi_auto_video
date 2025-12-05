from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator, HttpUrl
import json
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection setup with fallback logic
from .database_connection import db_manager, get_engine, get_connection_info, health_check

# Get engine from connection manager (with automatic fallback)
engine = db_manager.get_engine()

# Model for video requests coming from API
class VideoCreationRequest(BaseModel):
    # Basic fields
    title: Optional[str]  # Made optional so it can be auto-generated from prompt
    description: Optional[str]
    prompt: Optional[str]  # Main prompt for AI video generation
    
    # Video settings
    duration: Optional[int]  # in seconds
    resolution: Optional[str]
    format: Optional[str]
    content_type: Optional[str]  # e.g., tutorial, slideshow, social_media, etc.
    style: Optional[str]  # e.g., modern, professional, fun, etc.
    
    # Audio settings
    audio_type: Optional[str]  # voiceover, music, both, none
    
    # Technical settings
    aspect_ratio: Optional[str]
    fps: Optional[int] = 24  # Frames per second
    quality: Optional[str]
    
    # Feature flags
    use_ai: Optional[bool]
    include_audio: Optional[bool]  # camelCase version
    
    # Audio options
    music_type: Optional[str]
    custom_audio: Optional[str]
    
    # Visual options
    color_grading: Optional[str]
    visual_effects: Optional[List[str]] = []
    transition_effects: Optional[str]
    
    # Content options
    target_audience: Optional[str]
    script: Optional[str]
    media_urls: Optional[List[str]]  # camelCase version
    background_music: Optional[str]
    text_overlay_style: Optional[str]
    transitions: Optional[str]
    
    # Processing options
    generate_type: Optional[str]
    model: Optional[str]
    priority: Optional[str]
    content_data: Dict[str, Any] = {}  # Additional metadata
    
    # Required field
    user_id: str  # Required user ID from frontend
    
    class Config:
        # This allows the model to accept additional fields that aren't defined
        extra = "allow"

    # Use the Pydantic v2 syntax for validators
    @field_validator('content_data', mode='before')
    @classmethod
    def validate_json_content(cls, v):
        # Ensure content_data is valid
        return v
    
    # Using a model_validator instead of field_validator for whole-model validation
    @model_validator(mode='before')
    @classmethod
    def convert_camel_to_snake(cls, data):
        """
        Automatically detect camelCase keys and convert them to snake_case,
        removing the original camelCase keys from the data.
        """
        if isinstance(data, dict):
            def is_camel_case(key):
                """Check if a string is in camelCase format"""
                if len(key) < 2:
                    return False
                # Must start with lowercase letter
                if not key[0].islower():
                    return False
                # Must have at least one uppercase letter (not at the start)
                return any(c.isupper() for c in key[1:])
            
            def camel_to_snake(key):
                """Convert camelCase to snake_case"""
                result = []
                for i, char in enumerate(key):
                    if char.isupper() and i > 0:
                        result.append('_')
                        result.append(char.lower())
                    else:
                        result.append(char.lower())
                return ''.join(result)
            
            converted_data = {}
            
            # Process all keys in the original data
            for key, value in data.items():
                if is_camel_case(key):
                    # Convert camelCase to snake_case
                    snake_key = camel_to_snake(key)
                    # Only use the camelCase value if snake_case doesn't already exist
                    if snake_key not in data:
                        converted_data[snake_key] = value
                    # Skip adding the original camelCase key
                else:
                    # Keep all non-camelCase keys (including existing snake_case)
                    converted_data[key] = value
            
            return converted_data
        
        return data

# Database model for storing video data
class Video(SQLModel, table=True):
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    prompt: Optional[str] = None  # Main prompt for AI video generation
    duration: Optional[int] = None
    resolution: str
    format: str
    content_type: str
    style: str
    audio_type: str
    aspect_ratio: Optional[str]
    fps: Optional[int]
    quality: Optional[str]
    use_ai: Optional[bool]
    include_audio: Optional[bool]
    music_type: Optional[str]
    custom_audio: Optional[str] = None
    color_grading: Optional[str]
    visual_effects: Optional[str] = None  # JSON array of effects
    transition_effects: Optional[str]
    target_audience: Optional[str] = None
    script: Optional[str] = None
    media_urls: Optional[str] = None  # Stored as JSON string
    background_music: Optional[str] = None
    text_overlay_style: str
    transitions: str
    generate_type: Optional[str]
    model: Optional[str]
    priority: Optional[str]
    content_data: Optional[str] = None  # Stored as JSON string
    status: str = "pending"  # pending, processing, completed, failed
    output_url: Optional[str] = None
    thumbnail: Optional[str] = None  # URL to video thumbnail
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None
    user_id: str  # Foreign key to frontend's user table

class DownloadImages(SQLModel, table=True):
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: int
    video_id: str  # Foreign key to Video table
    image_url: str
    created_at: datetime = Field(default_factory=datetime.now)
    query: Optional[str] = None
    status: str = Field(default="success")
    updated_at: datetime = Field(default_factory=datetime.now)

class SelectAIVoices(SQLModel, table=True):
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    voice_id: str = Field(unique=True)  # Unique ID for the AI voice (e.g., "am_puck", "en_female_1")
    voice_name: str  # Human-readable name (e.g., "Puck", "Sarah", "Professional Male")
    voice_description: Optional[str] = None  # Description of voice characteristics
    gender: Optional[str] = None  # "male", "female", "neutral"
    age_group: Optional[str] = None  # "child", "young_adult", "adult", "senior"
    accent: Optional[str] = None  # "american", "british", "australian", etc.
    language: str = "en"  # Language code (en, es, fr, etc.)
    voice_sample_url: Optional[str] = None  # URL to voice sample (can be local or external)
    is_demo: bool = Field(default=True)  # True if it's a demo voice stored locally
    is_premium: bool = Field(default=False)  # True if it's a premium voice requiring payment
    provider: Optional[str] = None  # Voice provider (e.g., "replicate", "elevenlabs", "local")
    model_name: Optional[str] = None  # Model name used by the provider
    voice_settings: Optional[str] = None  # JSON string for voice-specific settings
    is_active: bool = Field(default=True)  # Whether the voice is currently available
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class VideoVoiceSelection(SQLModel, table=True):
    """Junction table to track which voice is selected for each video"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    video_id: str  # Foreign key to Video table
    voice_id: str  # Reference to SelectAIVoices.voice_id
    selected_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)  # Allow multiple voice selections, mark active one


# Database models for media processing system
class MediaItem(SQLModel, table=True):
    """Store uploaded media files and their analysis results"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    # Basic file information
    filename: str
    original_filename: str
    file_path: str
    file_size: int  # in bytes
    mime_type: str
    media_type: str  # 'image' or 'video'
    
    # Processing status
    status: str = "uploaded"  # uploaded, processing, analyzed, error
    task_id: Optional[str] = None  # Celery task ID
    
    # Analysis results (stored as JSON strings)
    technical_specs: Optional[str] = None
    content_analysis: Optional[str] = None
    quality_metrics: Optional[str] = None
    processing_recommendations: Optional[str] = None
    
    # Error handling
    errors: Optional[str] = None  # JSON array of error messages
    warnings: Optional[str] = None  # JSON array of warning messages
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # User and session info
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Thumbnail and preview data
    thumbnail_path: Optional[str] = None
    preview_data: Optional[str] = None  # Base64 encoded thumbnail or preview


class ProcessingTask(SQLModel, table=True):
    """Track Celery processing tasks and their states"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    # Task identification
    task_id: str = Field(unique=True, index=True)  # Celery task ID
    task_name: str  # Name of the Celery task
    task_type: str  # 'single_media', 'batch_media', 'thumbnails', etc.
    
    # Task status
    status: str = "pending"  # pending, started, processing, success, failure, revoked
    progress: Optional[int] = None  # Progress percentage (0-100)
    
    # Task data
    input_data: Optional[str] = None  # JSON string of input parameters
    result_data: Optional[str] = None  # JSON string of task results
    error_info: Optional[str] = None  # Error details if failed
    
    # Related entities
    media_items: Optional[str] = None  # JSON array of related media item IDs
    user_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Estimated completion
    estimated_duration: Optional[int] = None  # Estimated duration in seconds
    estimated_completion: Optional[datetime] = None


class MediaSequence(SQLModel, table=True):
    """Store sequences of media items for video creation"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    
    # Sequence information
    name: str
    description: Optional[str] = None
    
    # Media items in sequence (stored as JSON array of media IDs with order)
    media_items: str  # JSON: [{"media_id": "...", "sequence_order": 1, "duration": 5}, ...]
    
    # Video configuration
    video_effects: Optional[str] = None  # JSON string of video effects configuration
    audio_settings: Optional[str] = None  # JSON string of audio settings
    
    # Processing status
    status: str = "draft"  # draft, processing, completed, error
    video_id: Optional[str] = Field(foreign_key="video.id")  # Link to generated video
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User info
    user_id: Optional[str] = None   
    session_id: Optional[str] = None


# New models for Script Generation and Social Media Content
class ScriptGeneration(SQLModel, table=True):
    """Table to store generated scripts"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str  # User who generated the script
    step_process_id: int = Field(foreign_key="videoprocessstep.id")
    step: "VideoProcessStep" = Relationship(back_populates="scripts")
    user_prompt: str  # Original user prompt
    script_type: str  # short, medium, long, etc.
    category: str  # General, Technology, etc.
    language: str = "English"  # Voiceover language
    
    # Generated content
    title: str
    description: str
    voiceover_script: str  # The main script content
    tags: str  # JSON array of tags
    duration_estimate: str
    word_count: int
    
    # Metadata
    generation_duration_ms: Optional[int] = None  # Time taken to generate
    ai_model_used: Optional[str] = None  # AI model that generated the content
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Note: Relationships removed to avoid SQLModel relationship issues

class SocialMediaContent(SQLModel, table=True):
    """Table to store social media optimized content for scripts"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    script_id: str = Field(foreign_key="scriptgeneration.id")
    user_id: str  # User who generated the content
    
    # Platform-specific content (stored as JSON)
    platform_descriptions: str  # JSON array of platform descriptions
    thumbnail_suggestions: str  # JSON array of thumbnail suggestions
    general_seo_keywords: str  # JSON array of general SEO keywords
    trending_hashtags: str  # JSON array of trending hashtags
    
    # Generation metadata
    platforms_requested: str  # JSON array of platforms requested
    generation_duration_ms: Optional[int] = None
    ai_model_used: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class GeneratedVoiceover(SQLModel, table=True):
    """Table to store generated voiceover files and metadata"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[int] = None  # User who generated the voiceover (None for free tool)
    script_id: Optional[str] = None  # Reference to ScriptGeneration if available
    video_id: Optional[str] = None  # Reference to Video if part of video generation
    
    # Voiceover details
    voice_id: str  # Reference to the voice used (from SelectAIVoices)
    voice_name: str  # Human-readable voice name for easy reference
    text_content: str  # The text that was converted to speech
    
    # Audio settings used for generation
    speed: float = 1.0  # Playback speed
    pitch: float = 1.0  # Voice pitch
    volume: float = 0.8  # Audio volume
    tone: Optional[str] = None  # Voice tone setting
    
    # File information
    filename: str  # The actual filename (e.g., "voiceover_demo-script-123_1757707084.wav")
    file_url: str  # Full URL to access the file (e.g., "/api/audio/voiceover_demo-script-123_1757707084.wav")
    file_size: Optional[int] = None  # File size in bytes
    duration_seconds: Optional[float] = None  # Audio duration in seconds
    
    # Generation metadata
    generation_duration_ms: Optional[int] = None  # Time taken to generate
    ai_provider: Optional[str] = None  # Provider used (e.g., "replicate", "elevenlabs")
    ai_model: Optional[str] = None  # Specific model used
    status: str = "completed"  # completed, failed, processing
    error_message: Optional[str] = None  # Error message if generation failed
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FreeVoiceoverUsage(SQLModel, table=True):
    """Table to track free voiceover tool usage for rate limiting"""
    _id: Optional[int] = Field(default=None, sa_column_kwargs={"autoincrement": True}, index=True)
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    identifier: str = Field(index=True)  # IP address or session ID
    voiceover_id: str  # Reference to GeneratedVoiceover
    generated_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime  # When the file will be deleted
    is_deleted: bool = Field(default=False)


class PlatformDescription(BaseModel):
    """Model for individual platform description"""
    platform: str
    title: str
    description: str
    hashtags: List[str]
    seo_keywords: List[str]

class ThumbnailSuggestion(BaseModel):
    """Model for thumbnail suggestions"""
    title: str
    style: str
    elements: List[str]
    colors: List[str]



class AIModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: Optional[str] = None
    model_name: str = Field(index=True, unique=True)          # e.g. "mistralai/mistral-7b-instruct"
    display_name: Optional[str] = Field(default=None)         # Human readable name
    is_free: bool = Field(default=False, index=True)
    quality_score: Optional[float] = Field(default=None)      # Heuristic score
    context_length: Optional[int] = None
    pricing_prompt: Optional[float] = None
    pricing_completion: Optional[float] = None
    capabilities: Optional[str] = None                        # JSON string
    tags: Optional[str] = None                                # JSON array string
    is_recommended: bool = Field(default=False, index=True)
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    raw_metadata: Optional[str] = None                        # Full JSON as string
    active: bool = Field(default=True)

        

# Create all tables
def create_db_and_tables():
    """
    Create all tables and run auto-migration to add missing columns.
    This function will:
    1. Create new tables based on SQLModel definitions
    2. Automatically detect and add missing columns to existing tables
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Create new tables (this won't modify existing tables)
        SQLModel.metadata.create_all(engine)
        logger.info("[OK] Table creation completed")
        
        # Step 2: Run auto-migration for missing columns
        from .auto_migration import run_auto_migration
        migration_result = run_auto_migration(engine)
        
        # Log migration results
        if migration_result['total_columns_added'] > 0:
            logger.info(f"[OK] Auto-migration completed: {migration_result['total_columns_added']} columns added")
        else:
            logger.info("[INFO] No schema migrations needed")
            
        return migration_result
        
    except ImportError as e:
        logger.warning(f"⚠️  Auto-migration not available: {e}")
        logger.info("ℹ️  Only basic table creation performed")
        return None
    except Exception as e:
        logger.error(f"❌ Error during database setup: {e}")
        # Don't fail startup on migration errors
        return None

# Get database session
def get_session():
    with Session(engine) as session:
        yield session

# --- Helper functions for User Info (Prisma User Table) ---

def get_user_by_id(user_id: str):
    """
    Fetch user info from the Prisma-managed 'user' table by user_id.
    Returns a dict with user fields, or None if not found.
    """
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT * FROM "user" WHERE id = :id'), {"id": user_id})
        row = result.fetchone()
        if row:
            # Convert SQLAlchemy Row to dict
            return dict(row._mapping)
        return None

# Helper functions for AI Voices
def get_local_voice_sample_url(voice_id: str, base_url: str = "http://localhost:8000") -> str:
    """Generate URL for local demo voice sample"""
    return f"{base_url}/api/voices/samples/{voice_id}.wav"

def seed_demo_voices():
    """Seed the database with demo AI voices from actual voice samples"""
    demo_voices = [
        # Female American Voices
        {
            "voice_id": "af_alloy",
            "voice_name": "Alloy",
            "voice_description": "Clear and professional female voice with neutral American accent",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-alloy"
        },
        {
            "voice_id": "af_aoede",
            "voice_name": "Aoede",
            "voice_description": "Smooth and articulate female voice",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-aoede"
        },
        {
            "voice_id": "af_bella",
            "voice_name": "Bella",
            "voice_description": "Warm and friendly female voice",
            "gender": "female",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-bella"
        },
        {
            "voice_id": "af_jessica",
            "voice_name": "Jessica",
            "voice_description": "Professional and confident female voice",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-jessica"
        },
        {
            "voice_id": "af_kore",
            "voice_name": "Kore",
            "voice_description": "Energetic and youthful female voice",
            "gender": "female",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-kore"
        },
        {
            "voice_id": "af_nicole",
            "voice_name": "Nicole",
            "voice_description": "Sophisticated and elegant female voice",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-nicole"
        },
        {
            "voice_id": "af_nova",
            "voice_name": "Nova",
            "voice_description": "Dynamic and modern female voice",
            "gender": "female",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-nova"
        },
        {
            "voice_id": "af_river",
            "voice_name": "River",
            "voice_description": "Calm and soothing female voice",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-river"
        },
        {
            "voice_id": "af_sarah",
            "voice_name": "Sarah",
            "voice_description": "Reliable and trustworthy female voice",
            "gender": "female",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-sarah"
        },
        {
            "voice_id": "af_sky",
            "voice_name": "Sky",
            "voice_description": "Bright and optimistic female voice",
            "gender": "female",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-sky"
        },
        
        # Male American Voices
        {
            "voice_id": "am_adam",
            "voice_name": "Adam",
            "voice_description": "Strong and authoritative male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-adam"
        },
        {
            "voice_id": "am_echo",
            "voice_name": "Echo",
            "voice_description": "Deep and resonant male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-echo"
        },
        {
            "voice_id": "am_eric",
            "voice_name": "Eric",
            "voice_description": "Friendly and approachable male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-eric"
        },
        {
            "voice_id": "am_fenrir",
            "voice_name": "Fenrir",
            "voice_description": "Powerful and commanding male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-fenrir"
        },
        {
            "voice_id": "am_liam",
            "voice_name": "Liam",
            "voice_description": "Smooth and professional male voice",
            "gender": "male",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-liam"
        },
        {
            "voice_id": "am_michael",
            "voice_name": "Michael",
            "voice_description": "Classic and reliable male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-michael"
        },
        {
            "voice_id": "am_onyx",
            "voice_name": "Onyx",
            "voice_description": "Rich and sophisticated male voice",
            "gender": "male",
            "age_group": "adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "openai",
            "model_name": "tts-1-onyx"
        },
        {
            "voice_id": "am_puck",
            "voice_name": "Puck",
            "voice_description": "Energetic and youthful male voice",
            "gender": "male",
            "age_group": "young_adult",
            "accent": "american",
            "language": "en",
            "is_demo": True,
            "provider": "replicate",
            "model_name": "puck-voice-model"
        }
    ]
    
    with Session(engine) as session:
        for voice_data in demo_voices:
            # Generate local sample URL
            voice_data["voice_sample_url"] = get_local_voice_sample_url(voice_data["voice_id"])
            
            # Check if voice already exists
            existing_voice = session.exec(
                select(SelectAIVoices).where(SelectAIVoices.voice_id == voice_data["voice_id"])
            ).first()
            
            if not existing_voice:
                voice = SelectAIVoices(**voice_data)
                session.add(voice)
        
        session.commit()
        print(f"Seeded {len(demo_voices)} demo voices")


# === Video Generation Process Tracking ===

class VideoGenerationProcess(SQLModel, table=True):
    """
    Comprehensive tracking of video generation workflow from start to finish.
    This table stores the complete state and progress of each video creation process,
    allowing users to resume from any step and providing full audit trails.
    """
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    
    # Core identification
    user_id: str  # User who initiated the video generation
    session_id: Optional[str] = None  # Browser session for tracking
    video_id: Optional[str] = None  # Reference to final Video record when completed
    
    # Process state tracking
    current_step: str = "input"  # Current workflow step (input, scripts, voiceover, etc.)
    step_progress: str = "{}"  # JSON object tracking completion status of each step
    overall_progress: int = 0  # Overall completion percentage (0-100)
    
    # Workflow step data (stored as JSON strings for flexibility)
    input_data: Optional[str] = None  # User prompt, categories, script types, preferences
    script_data: Optional[str] = None  # Generated scripts, selected script, edit history
    voiceover_data: Optional[str] = None  # Voice selection, audio settings, generated files
    social_media_data: Optional[str] = None  # Platform-specific content, SEO keywords, hashtags
    media_data: Optional[str] = None  # Selected/uploaded media items, search results
    video_effects_data: Optional[str] = None  # Final video configuration, effects, transitions
    
    # Process metadata and timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    total_processing_time: Optional[int] = None  # Total time in seconds
    
    # Error handling and recovery
    failed_steps: Optional[str] = None  # JSON array of steps that failed
    error_messages: Optional[str] = None  # JSON array of detailed error information
    retry_count: int = 0  # Number of retry attempts
    last_error_at: Optional[datetime] = None
    
    # Process status and configuration
    status: str = "active"  # active, completed, failed, paused, cancelled
    priority: str = "normal"  # low, normal, high for processing queue
    configuration: Optional[str] = None  # JSON for process-specific settings
    
    # Analytics and performance tracking
    step_durations: Optional[str] = None  # JSON object with timing for each step
    ai_model_usage: Optional[str] = None  # JSON tracking which AI models were used
    resource_usage: Optional[str] = None  # JSON for memory, processing metrics
    
    # User interaction tracking
    user_actions: Optional[str] = None  # JSON log of user interactions during process
    feedback_data: Optional[str] = None  # User feedback on generated content
    
    # Quality and validation
    validation_results: Optional[str] = None  # JSON results of content validation checks
    quality_scores: Optional[str] = None  # JSON quality metrics for each step
    
    # Collaboration and sharing
    shared_with_users: Optional[str] = None  # JSON array of user IDs if shared
    collaboration_data: Optional[str] = None  # JSON for collaborative editing history


class VideoProcessStep(SQLModel, table=True):
    """
    Individual step tracking within a video generation process.
    Provides granular tracking of each workflow step with detailed metadata.
    """
    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    
    # Process relationship
    process_id: int = Field(foreign_key="videogenerationprocess.id")
    scripts: List["ScriptGeneration"] = Relationship(back_populates="step")
    
    # Step identification
    step_name: str  # input, loading, scripts, editing, voiceover, social-media, media, video-effects
    step_order: int  # Sequential order in the workflow
    
    # Step state
    status: str = "not-started"  # not-started, in-progress, completed, failed, skipped
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Step data and results
    input_data: Optional[str] = None  # JSON data provided to this step
    output_data: Optional[str] = None  # JSON results produced by this step
    processing_logs: Optional[str] = None  # JSON array of processing events
    
    # Error handling
    error_message: Optional[str] = None
    error_details: Optional[str] = None  # JSON with full error context
    retry_count: int = 0
    
    # Performance metrics
    ai_requests: int = 0  # Number of AI API calls made
    ai_tokens_used: int = 0  # Total tokens consumed
    processing_time: Optional[int] = None  # Actual processing time in milliseconds
    
    # Quality and validation
    validation_passed: bool = True
    validation_messages: Optional[str] = None  # JSON array of validation results
    quality_score: Optional[float] = None  # 0.0 to 1.0 quality rating
    
    # User interaction
    user_modifications: Optional[str] = None  # JSON log of user edits/changes
    user_approval: Optional[bool] = None  # Whether user approved the step results
    
    # Technical details
    system_resources: Optional[str] = None  # JSON with memory, CPU usage during step
    external_apis_used: Optional[str] = None  # JSON list of external services called


# The CurrentVideoGenerate class is now in video_process_manager.py
# Import it here for backward compatibility
try:
    from .video_process_manager import CurrentVideoGenerate, VideoGenerationProcessManager
    from .video_process_manager import get_active_processes_for_user, cleanup_old_processes
except ImportError:
    # Handle case where video_process_manager is not available
    print("Warning: video_process_manager module not available")


        # === AI Model Metadata Table & OpenRouter Seeder ===

        
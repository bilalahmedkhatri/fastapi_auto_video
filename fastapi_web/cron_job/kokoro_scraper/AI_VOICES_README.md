# AI Voices Database System

## Overview
The AI Voices system has been updated to provide better management of voice options with demo samples and comprehensive voice metadata.

## Database Models

### SelectAIVoices
Main table for storing AI voice information:
- `voice_id`: Unique identifier for each voice (e.g., "am_puck")
- `voice_name`: Human-readable name (e.g., "Puck", "Sarah")
- `voice_description`: Description of voice characteristics
- `gender`: "male", "female", "neutral"
- `age_group`: "child", "young_adult", "adult", "senior"
- `accent`: "american", "british", "australian", etc.
- `language`: Language code ("en", "es", "fr", etc.)
- `voice_sample_url`: URL to access voice sample
- `is_demo`: Whether it's a free demo voice
- `is_premium`: Whether it requires payment
- `provider`: Voice service provider
- `model_name`: Specific model name from provider
- `voice_settings`: JSON string for provider-specific settings
- `is_active`: Whether the voice is currently available

### VideoVoiceSelection
Junction table to track voice selections for videos:
- `video_id`: Reference to Video table
- `voice_id`: Reference to SelectAIVoices
- `selected_at`: When the selection was made
- `is_active`: Whether this is the current active selection

## Voice Sample Storage

### Actual Voice Samples
The system now includes **21 high-quality voice samples**:

**Female Voices (12):**
- **Alloy** - Clear and professional female voice with neutral American accent
- **Aoede** - Smooth and articulate female voice  
- **Bella** - Warm and friendly female voice
- **Jessica** - Professional and confident female voice
- **Kore** - Energetic and youthful female voice
- **Nicole** - Sophisticated and elegant female voice
- **Nova** - Dynamic and modern female voice
- **River** - Calm and soothing female voice
- **Sarah** (af_sarah) - Reliable and trustworthy female voice
- **Sky** - Bright and optimistic female voice
- **Sarah** (en_female_1) - Professional female voice with clear pronunciation
- **Emma** - Elegant British female voice

**Male Voices (9):**
- **Adam** - Strong and authoritative male voice
- **Echo** - Deep and resonant male voice
- **Eric** - Friendly and approachable male voice
- **Fenrir** - Powerful and commanding male voice
- **Liam** - Smooth and professional male voice
- **Michael** - Classic and reliable male voice
- **Onyx** - Rich and sophisticated male voice
- **Puck** - Energetic and youthful male voice
- **James** - Deep professional male voice for business content

### Storage Structure
Voice samples are stored in organized directories:
```
media/voice_samples_real/
├── af_alloy.wav       (2.06 MB)
├── af_aoede.wav       (2.15 MB)
├── af_bella.wav       (2.41 MB)
├── af_jessica.wav     (1.93 MB)
├── af_kore.wav        (2.02 MB)
├── af_nicole.wav      (3.54 MB)
├── af_nova.wav        (2.04 MB)
├── af_river.wav       (1.93 MB)
├── af_sarah.wav       (2.33 MB)
├── af_sky.wav         (2.20 MB)
├── am_adam.wav        (2.21 MB)
├── am_echo.wav        (2.10 MB)
├── am_eric.wav        (1.91 MB)
├── am_fenrir.wav      (2.00 MB)
├── am_liam.wav        (1.98 MB)
├── am_michael.wav     (2.57 MB)
├── am_onyx.wav        (2.06 MB)
└── am_puck.wav        (1.92 MB)
```

### URL Access
Voice samples are accessible via:
```
http://localhost:8000/api/voices/samples/{voice_id}.wav
```

Examples:
- `http://localhost:8000/api/voices/samples/af_bella.wav`
- `http://localhost:8000/api/voices/samples/am_adam.wav`

## API Endpoints

### Get All Voices
```
GET /api/voices/
```
Query parameters:
- `language`: Filter by language code
- `gender`: Filter by gender
- `is_demo`: Filter demo/premium voices
- `provider`: Filter by provider

### Get Voice by ID
```
GET /api/voices/{voice_id}
```

### Get Voice Sample
```
GET /api/voices/samples/{voice_id}.wav
```

### Select Voice for Video
```
POST /api/voices/videos/{video_id}/select/{voice_id}
```

### Get Selected Voice
```
GET /api/voices/videos/{video_id}/selected
```

## Current Voice Statistics

- **Total Voices**: 21
- **Female Voices**: 12 
- **Male Voices**: 9
- **Providers**: OpenAI (17), Replicate (3), ElevenLabs (1)
- **Age Groups**: Adults (15), Young Adults (6)
- **All voices include high-quality WAV samples** (1.9-3.6 MB each)

## Usage Examples

### Initialize Database
```python
from models.db_models import create_db_and_tables, seed_demo_voices

# Create tables
create_db_and_tables()

# Seed with demo voices
seed_demo_voices()
```

### Query Voices
```python
from models.db_models import SelectAIVoices, get_session
from sqlmodel import select

with next(get_session()) as session:
    # Get all female voices
    female_voices = session.exec(
        select(SelectAIVoices).where(SelectAIVoices.gender == "female")
    ).all()
    
    # Get demo voices
    demo_voices = session.exec(
        select(SelectAIVoices).where(SelectAIVoices.is_demo == True)
    ).all()
```

### Select Voice for Video
```python
from models.db_models import VideoVoiceSelection

# Create voice selection
selection = VideoVoiceSelection(
    video_id="video-123",
    voice_id="am_puck",
    is_active=True
)
```

## Adding New Voices

To add new voices to the system:

1. Add the voice data to the database:
```python
new_voice = SelectAIVoices(
    voice_id="new_voice_id",
    voice_name="New Voice Name",
    voice_description="Description",
    gender="female",
    language="en",
    voice_sample_url="http://localhost:8000/api/voices/samples/new_voice_id.mp3",
    is_demo=True,
    provider="your_provider"
)
```

2. Add the sample file to `media/voice_samples/new_voice_id.mp3`

## Integration with Video Builder

The voice system integrates with the existing video builder. When generating videos, you can:

1. Query available voices
2. Let users select a voice
3. Use the selected voice for speech generation
4. Store the selection in VideoVoiceSelection table

## Future Enhancements

- Voice cloning capabilities
- Multi-language support expansion
- Voice quality ratings
- Custom voice uploads
- Voice synthesis parameters tuning

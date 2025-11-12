# Voiceover API Documentation

## Overview

The Voiceover API provides endpoints for text-to-speech generation using the local Kokoro-82M voice synthesis model. This system enables high-quality voiceover generation without external API dependencies.

## Architecture

```
api/voiceover/
├── router.py           # Main router combining all endpoints
├── create.py           # POST /api/voiceover/create
├── get_all.py          # GET /api/voiceover/get_all
├── get_by_id.py        # GET /api/voiceover/get_by_id/{id}
├── update_by_id.py     # PUT /api/voiceover/update_by_id/{id}
├── delete_by_id.py     # DELETE /api/voiceover/delete_by_id/{id}
└── samples.py          # GET /api/voiceover/voiceover_samples
```

## Technology Stack

- **Voice Engine:** Kokoro-82M (local ONNX model)
- **Database:** PostgreSQL with SQLModel ORM
- **Framework:** FastAPI with async support
- **Audio Format:** WAV (24kHz, 16-bit PCM)
- **Storage:** Local filesystem (media/audio/)

## Database Tables

### SelectAIVoices
Stores available voice configurations:
- `voice_id`: Unique identifier (e.g., "af_sarah", "am_michael")
- `voice_name`: Human-readable name
- `gender`: male/female
- `accent`: American/British/etc.
- `language`: Language code (en, es, fr, etc.)
- `provider`: "kokoro-local"
- `model_name`: "kokoro-82m"
- `is_active`: Availability status

### GeneratedVoiceover
Stores generated voiceover metadata:
- `id`: UUID primary key
- `user_id`: User who generated
- `voice_id`: Reference to SelectAIVoices
- `text_content`: Original text
- `speed`, `pitch`, `volume`: Audio settings
- `filename`: Audio file name
- `file_url`: Access URL
- `duration_seconds`: Audio length
- `ai_provider`: "kokoro-local"
- `ai_model`: "kokoro-82m"

## API Endpoints

### 1. Create Voiceover

**Endpoint:** `POST /api/voiceover/create`

**Description:** Generate voiceover from text using local Kokoro-82M model.

**Request Body:**
```json
{
  "user_id": "user_123",
  "text": "Your text to convert to speech",
  "voice_id": "af_sarah",
  "script_id": "script_456",
  "video_id": "video_789",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 0.8,
  "tone": "neutral"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "audio_url": "/api/voiceover/audio/filename.wav",
  "filename": "2025-11-12-03-45.wav",
  "duration_seconds": 3.5,
  "file_size": 168000,
  "generation_time_ms": 2234
}
```

**Validation:**
- Text cannot be empty
- Text max 10,000 characters
- Voice must exist in SelectAIVoices table
- Speed range: 0.5-2.0
- Pitch range: 0.5-2.0
- Volume range: 0.1-2.0

---

### 2. Get All Voiceovers

**Endpoint:** `GET /api/voiceover/get_all`

**Description:** List voiceovers with filtering and pagination.

**Query Parameters:**
- `user_id` (optional): Filter by user
- `script_id` (optional): Filter by script
- `video_id` (optional): Filter by video
- `voice_id` (optional): Filter by voice
- `page` (default: 1): Page number
- `per_page` (default: 20, max: 100): Items per page

**Response:**
```json
{
  "voiceovers": [
    {
      "id": "uuid",
      "user_id": "user_123",
      "voice_id": "af_sarah",
      "voice_name": "Sarah",
      "text_content": "Sample text",
      "filename": "2025-11-12-03-45.wav",
      "file_url": "/api/voiceover/audio/2025-11-12-03-45.wav",
      "duration_seconds": 3.5,
      "file_size": 168000,
      "speed": 1.0,
      "status": "completed",
      "created_at": "2025-11-12T03:45:00"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

---

### 3. Get Voiceover by ID

**Endpoint:** `GET /api/voiceover/get_by_id/{voiceover_id}`

**Description:** Get complete metadata for a specific voiceover.

**Response:**
```json
{
  "id": "uuid",
  "user_id": "user_123",
  "script_id": "script_456",
  "video_id": "video_789",
  "voice_id": "af_sarah",
  "voice_name": "Sarah",
  "text_content": "Full text content",
  "speed": 1.0,
  "pitch": 1.0,
  "volume": 0.8,
  "tone": "neutral",
  "filename": "2025-11-12-03-45.wav",
  "file_url": "/api/voiceover/audio/2025-11-12-03-45.wav",
  "file_size": 168000,
  "duration_seconds": 3.5,
  "generation_duration_ms": 2234,
  "ai_provider": "kokoro-local",
  "ai_model": "kokoro-82m",
  "status": "completed",
  "created_at": "2025-11-12T03:45:00",
  "updated_at": "2025-11-12T03:45:00"
}
```

---

### 4. Update Voiceover

**Endpoint:** `PUT /api/voiceover/update_by_id/{voiceover_id}`

**Description:** Update voiceover metadata (does not regenerate audio).

**Request Body:**
```json
{
  "text_content": "Updated text",
  "speed": 1.2,
  "pitch": 1.1,
  "volume": 0.9,
  "tone": "excited",
  "status": "completed"
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "Voiceover updated successfully",
  "updated_at": "2025-11-12T04:00:00"
}
```

**Note:** All fields are optional. Only provided fields are updated.

---

### 5. Delete Voiceover

**Endpoint:** `DELETE /api/voiceover/delete_by_id/{voiceover_id}`

**Description:** Delete voiceover record and audio files.

**Response:**
```json
{
  "id": "uuid",
  "message": "Voiceover deleted successfully",
  "file_deleted": true
}
```

**Actions:**
- Deletes database record
- Deletes WAV audio file
- Deletes JSON metadata file (if exists)

---

### 6. Get Voice Samples

**Endpoint:** `GET /api/voiceover/voiceover_samples`

**Description:** List available voices with filtering.

**Query Parameters:**
- `language` (default: "en"): Language code
- `gender` (optional): male/female
- `accent` (optional): American/British/etc.

**Response:**
```json
{
  "voices": [
    {
      "voice_id": "af_sarah",
      "voice_name": "Sarah",
      "gender": "female",
      "accent": "American",
      "language": "en",
      "description": "Reliable, clear American female voice",
      "sample_url": "/api/voiceover/voiceover_samples/audio/af_sarah",
      "provider": "kokoro-local",
      "model_name": "kokoro-82m",
      "is_active": true
    }
  ],
  "total": 16,
  "language": "en"
}
```

---

### 7. Get Voice Sample Audio

**Endpoint:** `GET /api/voiceover/voiceover_samples/audio/{voice_id}`

**Description:** Download voice sample audio file.

**Response:** WAV audio file (audio/wav)

**Behavior:**
- Returns existing sample if available
- Generates sample on-demand if not exists
- Sample text: "Hello, this is a sample of my voice..."

---

### 8. Generate Custom Voice Sample

**Endpoint:** `POST /api/voiceover/voiceover_samples/generate/{voice_id}`

**Description:** Generate custom voice sample with provided text.

**Query Parameters:**
- `text` (required): Text for sample generation

**Response:**
```json
{
  "voice_id": "af_sarah",
  "sample_url": "/api/voiceover/voiceover_samples/audio/af_sarah",
  "duration_seconds": 4.2
}
```

## Available Voices

### American English (10 voices)

**Female Voices:**
- `af_sarah`: Reliable, clear
- `af_nicole`: Conversational
- `af_bella`: Energetic, youthful
- `af_jessica`: Authoritative, confident
- `af_april`: Professional

**Male Voices:**
- `am_michael`: Classic, trustworthy
- `am_david`: Deep, professional
- `am_john`: Warm, friendly
- `am_eric`: Approachable
- `am_aaron`: Strong, commanding

### British English (6 voices)

**Female Voices:**
- `bf_emma`: Charming, conversational
- `bf_grace`: Refined, sophisticated
- `bf_alice`: Elegant RP accent

**Male Voices:**
- `bm_lewis`: Clear, articulate
- `bm_oliver`: Distinguished
- `bm_george`: Steady, reliable

## Usage Examples

### Example 1: Generate Simple Voiceover

```python
import requests

response = requests.post(
    "http://localhost:8000/api/voiceover/create",
    json={
        "user_id": "user_123",
        "text": "Welcome to our video tutorial!",
        "voice_id": "af_sarah",
        "speed": 1.0
    }
)

data = response.json()
print(f"Generated: {data['audio_url']}")
print(f"Duration: {data['duration_seconds']}s")
```

### Example 2: List User's Voiceovers

```python
response = requests.get(
    "http://localhost:8000/api/voiceover/get_all",
    params={
        "user_id": "user_123",
        "page": 1,
        "per_page": 20
    }
)

data = response.json()
print(f"Total: {data['total']} voiceovers")
for vo in data['voiceovers']:
    print(f"- {vo['voice_name']}: {vo['duration_seconds']}s")
```

### Example 3: Get Voice Samples

```python
response = requests.get(
    "http://localhost:8000/api/voiceover/voiceover_samples",
    params={
        "gender": "female",
        "accent": "American"
    }
)

data = response.json()
for voice in data['voices']:
    print(f"{voice['voice_name']}: {voice['description']}")
    print(f"  Sample: {voice['sample_url']}")
```

### Example 4: Delete Old Voiceovers

```python
# Get old voiceovers
response = requests.get(
    "http://localhost:8000/api/voiceover/get_all",
    params={"user_id": "user_123"}
)

voiceovers = response.json()['voiceovers']

# Delete first one
if voiceovers:
    vo_id = voiceovers[0]['id']
    delete_response = requests.delete(
        f"http://localhost:8000/api/voiceover/delete_by_id/{vo_id}"
    )
    print(delete_response.json()['message'])
```

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid input (empty text, text too long, invalid speed/pitch/volume)
- **404 Not Found**: Voice not found, voiceover not found
- **500 Internal Server Error**: Generation failed, file system error

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

## Performance

### Generation Speed
- Average: 2-3 seconds per voiceover
- Depends on: text length, CPU/GPU, model initialization

### File Sizes
- ~48KB per second of audio (24kHz, 16-bit PCM)
- 3-second voiceover ≈ 144KB
- 10-second voiceover ≈ 480KB

### Concurrency
- Supports async operations
- Multiple simultaneous generations
- Thread-safe database operations

## Migration from Replicate API

The new system replaces the cloud-based Replicate API:

### Changes:
- ✅ No more API costs (free local generation)
- ✅ Faster generation (no network latency)
- ✅ Privacy (all processing local)
- ✅ Offline capability
- ✅ Simplified codebase

### Removed:
- `download_voice_replicate()` function
- Replicate API dependencies
- Network-based voice generation
- External voice catalog

### Added:
- Local Kokoro-82M generator integration
- Database-driven voice catalog
- On-demand sample generation
- Improved error handling

## Best Practices

1. **Voice Selection**: Query `/voiceover_samples` before generation
2. **Text Length**: Keep under 5,000 characters for optimal performance
3. **Speed Settings**: Use 0.8-1.2 range for natural speech
4. **Batch Operations**: Use pagination for large voiceover lists
5. **Cleanup**: Regularly delete old voiceovers to save disk space
6. **Caching**: Cache voice samples for faster preview loading

## Troubleshooting

### Issue: "Voice not found"
**Solution:** Ensure SelectAIVoices table is populated with Kokoro voices

### Issue: "Generation failed"
**Solution:** Check Kokoro-82M installation and model files

### Issue: "File not deleted"
**Solution:** Check file permissions in media/audio directory

### Issue: Slow generation
**Solution:** Use GPU if available, reduce text length

## Future Enhancements

- [ ] Background music integration
- [ ] Batch voiceover generation
- [ ] Audio effects (reverb, echo, etc.)
- [ ] Multiple language support beyond English
- [ ] Voice cloning capabilities
- [ ] Real-time streaming generation
- [ ] WebSocket progress updates

## Support

For issues or questions:
- Check database connection in `models/db_models.py`
- Verify Kokoro installation in `kokoro_82M/`
- Review logs for generation errors
- Test with sample endpoint first

---

**Last Updated:** November 12, 2025  
**API Version:** 1.0.0  
**Kokoro Model:** 82M parameters

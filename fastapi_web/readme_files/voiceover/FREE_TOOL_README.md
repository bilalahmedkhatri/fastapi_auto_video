# Free Voiceover Tool API

Public voiceover generation endpoint with rate limiting and automatic cleanup.

## Endpoint

```
POST /api/voiceover/free_tool
```

No authentication required!

## Rate Limiting

- **Limit**: 3 voiceover generations per 12 hours
- **Tracking**: By IP address
- **Reset**: 12 hours from first use
- **Response**: Returns `remaining_uses` and `reset_at` in response

## File Retention

- **Storage**: Files saved to `media/temp/voiceovers/`
- **Lifetime**: 1 hour
- **Cleanup**: Automated hourly deletion via cron job
- **Warning**: Download files immediately, URLs expire after 1 hour!

## Request Format

```json
{
  "text": "Your text here (required, 1-10,000 characters)",
  "voice_id": "af_sarah (required - get from voice catalog)",
  "speed": 1.0,    // Optional: 0.5-2.0 (default: 1.0)
  "pitch": 1.0,    // Optional: 0.5-2.0 (default: 1.0)
  "volume": 0.8,   // Optional: 0.1-2.0 (default: 0.8)
  "tone": "neutral" // Optional (default: "neutral")
}
```

## Response Format

### Success (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "audio_url": "/media/temp/voiceovers/free_20251117_143022_af_sarah.wav",
  "voice_name": "Sarah (American Female)",
  "duration_seconds": 12.5,
  "file_size": 480000,
  "expires_at": "2025-11-17T15:30:22.000Z",
  "remaining_uses": 2,
  "reset_at": null
}
```

### Rate Limit Exceeded (429 Too Many Requests)

```json
{
  "detail": {
    "error": "rate_limit_exceeded",
    "retry_after": "2025-11-17T23:30:22.000Z",
    "message": "You have exceeded the free tier limit of 3 generations per 12 hours. Please try again after 2025-11-17 23:30:22 UTC."
  }
}
```

### Invalid Voice (404 Not Found)

```json
{
  "detail": "Voice with ID 'invalid_voice' not found or inactive"
}
```

### Validation Error (422 Unprocessable Entity)

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "Text cannot exceed 10,000 characters",
      "type": "value_error"
    }
  ]
}
```

## Examples

### cURL

```bash
curl -X POST "http://localhost:8000/api/voiceover/free_tool" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! This is a test voiceover using the free tool.",
    "voice_id": "af_sarah",
    "speed": 1.0
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/voiceover/free_tool",
    json={
        "text": "Hello! This is a test voiceover.",
        "voice_id": "af_sarah",
        "speed": 1.1
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Audio URL: {data['audio_url']}")
    print(f"Expires at: {data['expires_at']}")
    print(f"Remaining uses: {data['remaining_uses']}")
elif response.status_code == 429:
    print(f"Rate limit exceeded. Retry after: {response.json()['detail']['retry_after']}")
```

### JavaScript (Fetch)

```javascript
fetch('http://localhost:8000/api/voiceover/free_tool', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Hello! This is a test voiceover.',
    voice_id: 'af_sarah',
    speed: 1.0
  })
})
.then(response => response.json())
.then(data => {
  if (data.audio_url) {
    console.log('Audio URL:', data.audio_url);
    console.log('Remaining uses:', data.remaining_uses);
  } else {
    console.error('Error:', data.detail);
  }
});
```

## Getting Available Voices

To get a list of available voices:

```bash
GET /api/voiceover/voiceover_samples
```

Response includes all available voices with their IDs, names, genders, accents, and languages.

## Validation Rules

| Field | Rule | Error |
|-------|------|-------|
| text | Required, not empty | 422 - Text cannot be empty |
| text | Max 10,000 characters | 422 - Text cannot exceed 10,000 characters |
| voice_id | Must exist in DB | 404 - Voice not found |
| voice_id | Must be active | 404 - Voice inactive |
| speed | 0.5 - 2.0 | 422 - Invalid speed range |
| pitch | 0.5 - 2.0 | 422 - Invalid pitch range |
| volume | 0.1 - 2.0 | 422 - Invalid volume range |

## Rate Limiting Details

### How It Works

1. System tracks IP address from request headers (`X-Forwarded-For`, `X-Real-IP`, or direct IP)
2. Counts generations in last 12-hour window
3. If count >= 3, returns 429 error with `retry_after` timestamp
4. After 12 hours from first use, counter resets automatically

### Database Tracking

```sql
CREATE TABLE FreeVoiceoverUsage (
  id UUID PRIMARY KEY,
  identifier VARCHAR,  -- IP address
  voiceover_id UUID,   -- Reference to generated file
  generated_at TIMESTAMP,
  expires_at TIMESTAMP,
  is_deleted BOOLEAN
);
```

### Bypass Rate Limit

To bypass rate limiting, create an authenticated account and use the standard endpoint:

```
POST /api/voiceover/create
Authorization: Bearer <your_token>
```

## File Cleanup

### Automated Cleanup Script

Location: `cron_job/delete_file.py`

**What it does:**
- Deletes WAV files older than 1 hour from `media/temp/voiceovers/`
- Marks database records as deleted
- Cleans up old usage records (>30 days)
- Logs all operations to `logs/cleanup.log`

**Run manually:**
```bash
python cron_job/delete_file.py
```

**Setup cron (Linux/Mac):**
```bash
# Edit crontab
crontab -e

# Add hourly job at minute 0
0 * * * * cd /path/to/fastapi_web && python cron_job/delete_file.py
```

**Setup Task Scheduler (Windows):**
```powershell
# Create scheduled task (run hourly)
schtasks /create /tn "VoiceoverCleanup" /tr "python d:\dev\fastapi_web\cron_job\delete_file.py" /sc hourly /st 00:00
```

## Best Practices

1. **Download immediately**: Files expire after 1 hour
2. **Check remaining_uses**: Plan multiple generations within limit
3. **Handle 429 errors**: Implement retry logic with exponential backoff
4. **Cache results**: Store audio files locally if reused
5. **Use authenticated API**: For unlimited generations without rate limits

## Error Handling

```python
def generate_with_retry(text, voice_id, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(
            "http://localhost:8000/api/voiceover/free_tool",
            json={"text": text, "voice_id": voice_id}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = response.json()['detail']['retry_after']
            print(f"Rate limited. Retry after {retry_after}")
            return None
        elif response.status_code >= 500:
            print(f"Server error, retrying... (attempt {attempt + 1})")
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            print(f"Client error: {response.json()}")
            return None
    
    return None
```

## Database Schema

### FreeVoiceoverUsage Table

Tracks rate limit usage:

```python
class FreeVoiceoverUsage(SQLModel, table=True):
    id: str                    # UUID primary key
    identifier: str            # IP address (indexed)
    voiceover_id: str          # Reference to GeneratedVoiceover
    generated_at: datetime     # When generated
    expires_at: datetime       # When file expires (1 hour)
    is_deleted: bool           # Cleanup flag
```

### GeneratedVoiceover Table

Stores voiceover metadata:

```python
class GeneratedVoiceover(SQLModel, table=True):
    id: str
    user_id: Optional[int]     # None for free tool
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
    ai_provider: str           # "kokoro"
    ai_model: str              # "kokoro-82m"
    status: str                # "completed"
    created_at: datetime
    updated_at: datetime
```

## Performance

- **Generation Time**: 1-5 seconds (depends on text length)
- **File Size**: ~40KB per second of audio (24kHz, 16-bit PCM WAV)
- **Concurrent Requests**: Handled via FastAPI async
- **Storage**: Temporary files cleaned hourly

## Migration Required

After creating this endpoint, run database migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Add FreeVoiceoverUsage table and make user_id optional"

# Apply migration
alembic upgrade head
```

## Support

For issues or questions:
- Check logs: `logs/cleanup.log`
- View API docs: `http://localhost:8000/docs`
- Contact: support@example.com

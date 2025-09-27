# Backend API Endpoints Needed for Video Display Component

## 1. GET Individual Video Details
**Endpoint:** `GET /api/videos/{video_id}`
**Purpose:** Retrieve complete video information including metadata, parameters, and file URLs

## 2. GET Video File/Stream
**Endpoint:** `GET /api/videos/{video_id}/file` or `GET /api/videos/{video_id}/stream`
**Purpose:** Serve the actual video file for playback

## 3. POST Save Video to Collection
**Endpoint:** `POST /api/user/videos` or `POST /api/videos/{video_id}/save`
**Purpose:** Save video to user's personal collection

## 4. PUT Update Video Metadata
**Endpoint:** `PUT /api/videos/{video_id}`
**Purpose:** Update video title, description, or other metadata

## 5. POST Regenerate Video
**Endpoint:** `POST /api/videos/{video_id}/regenerate`
**Purpose:** Recreate video with same parameters

## 6. GET User's Video Collection
**Endpoint:** `GET /api/user/{user_id}/videos`
**Purpose:** List all videos belonging to a specific user

---

## Implementation Details:

### Video Data Structure Expected by Frontend:
```json
{
  "id": "video_123456",
  "title": "Video Title",
  "description": "Video Description",
  "video_url": "/api/videos/123456/file",
  "thumbnail_url": "/api/videos/123456/thumbnail",
  "duration": 45,
  "resolution": "1920x1080",
  "format": "mp4",
  "status": "completed",
  "created_at": "2025-09-24T10:30:00Z",
  "frontend_data": {
    "script_data": {
      "title": "Original Script Title",
      "category": "Technology", 
      "content": "Full script content..."
    },
    "voiceover_data": {
      "voice_model": "Professional Male Voice",
      "duration": 42.5,
      "language": "en-US"
    },
    "media_data": {
      "selected_media": [...]
    },
    "social_media_data": {
      "hashtags": [...],
      "keywords": [...]
    },
    "video_effects_config": {
      "style": "Modern",
      "transitions": "Fade"
    }
  }
}
```
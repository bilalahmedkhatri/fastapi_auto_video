# AI Video Generation Platform - Copilot Instructions

## Architecture Overview

This is a full-stack AI video generation platform with three main components:
- **Frontend**: Next.js app (`ui_auto_movie/`) with React components and Tailwind CSS
- **Backend API**: FastAPI service (`fastapi_web/`) with PostgreSQL database and Redis
- **Video Engine**: Python video generation system (`auto_movie_editor/`) with Celery task processing

## Key Data Flow

1. **Video Request**: Frontend → FastAPI → Celery task queue
2. **Processing**: Celery worker executes `fastapi/celery_app.py`
3. **Progress Tracking**: Redis stores real-time processing state 
4. **Completion**: Database stores final video metadata + output URL

## Environment Setup Requirements
- Python 3.12.10 (virtual environments recommended)
- activate virtualenvs when open terminal "./fastapp/Scripts/activate"
- start celery worker with "celery -A celery_app worker --loglevel=info --pool=solo"
- start fastapi server with "fastapi dev main.py"

### Python Environments
- **auto_movie_editor**: Uses `gen_vedio` virtual environment (Python 3.8+)
- **fastapi_web**: Uses `fastapp` virtual environment (Python 3.8+)
- **Critical**: Windows requires Celery with `worker_pool='solo'` 

### System Dependencies
- **FFmpeg**: Required for video processing (must be in PATH)
- **PostgreSQL**: Database server (local or cloud)
- **Redis**: Task queue and caching (default: localhost:6379)
- **Node.js**: Version 16+ for Next.js frontend

### Virtual Environment Activation
```bash
# Video engine
cd auto_movie_editor
.\gen_vedio\Scripts\activate  # Windows
# or source gen_vedio/bin/activate  # Linux/Mac

# FastAPI backend  
cd fastapi_web
.\fastapp\Scripts\activate    # Windows
# or source fastapp/bin/activate  # Linux/Mac
```

## Video Format Support

### Target Formats (`VideoBuildConfig.target_format`)
- `"youtube_short"`: 1080x1920 (9:16 vertical)
- `"instagram_story"`: 1080x1920 (9:16 vertical)  
- `"tiktok"`: 1080x1920 (9:16 vertical)
- `"youtube_landscape"`: 1920x1080 (16:9 horizontal)
- `"instagram_post"`: 1080x1080 (1:1 square)

### Aspect Ratio Configuration
Defined in `auto_movie_editor/tools/video_builder.py`:
```python
TARGET_SIZE = {
    "youtube_short": (1080, 1920),
    "instagram_story": (1080, 1920),
    "tiktok": (1080, 1920),
    # Add custom formats here
}
```

### Voice Options
Available voices for `VideoBuildConfig.voice`:
- `"am_puck"`: Default voice
- `"en_male"`: English male voice  
- `"en_female"`: English female voice
- Check Replicate API documentation for full voice list

## Authentication Flow & User Management

### NextAuth.js Setup
- Configuration in `ui_auto_movie/app/api/auth/[...nextauth]/route.js`
- Uses JWT strategy with bcryptjs password hashing
- Session management with secure HTTP-only cookies

### User Registration Flow
```javascript
// Pattern from signup page
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, email, password })
});
```

### Database User Models
- **Prisma Schema** (`ui_auto_movie/prisma/schema.prisma`): User preferences, templates
- **Profile Features**: Avatar upload, social media links, API keys storage
- **User Templates**: `PromptTemplate` model for reusable video prompts

### Protected Routes
Use Next.js middleware pattern:
```javascript
// Check session before video creation
const session = await getServerSession(authOptions);
if (!session) redirect('/auth/login');
```

## Error Handling Patterns

### Video Generation Errors
- **Retry Logic**: Celery tasks have built-in retry with exponential backoff
- **Error States**: `VideoProcessingState` tracks failure reasons in Redis
- **Logging**: Check `auto_movie_editor/logs/` for detailed error traces

### API Error Responses
```python
# FastAPI pattern
raise HTTPException(
    status_code=400, 
    detail={"error": "Video generation failed", "video_id": video_id}
)
```

### Frontend Error Handling
```javascript
// ProcessingModal.js pattern
if (dbData.status === 'failed') {
  setProgress({
    status: 'Failed: ' + (dbData.error || 'Unknown error'),
    stage: 'failed'
  });
}
```

### Common Error Scenarios
1. **API Rate Limits**: OpenAI, Replicate, Pixabay APIs have usage limits
2. **Media Download Failures**: Network timeouts, invalid URLs
3. **Audio Generation**: Voice synthesis can fail with long text
4. **Video Composition**: MoviePy errors with incompatible media formats

## Testing Strategy

### Backend Testing
```bash
# FastAPI tests
cd fastapi_web
python -m pytest tests/ -v

# Test specific endpoints
python test_integration.py
python test_celery.py
```

### Frontend Testing  
```bash
# Next.js tests
cd ui_auto_movie
npm test
npm run test:e2e  # If Cypress/Playwright configured
```

### Video Generation Testing
```bash
# Test video pipeline
cd auto_movie_editor
python tools/run_app.py  # Uses example_run() function
python test_google_integration.py  # Test Google APIs
```

### Integration Testing Files
- `fastapi_web/test_integration.py`: End-to-end video creation
- `fastapi_web/test_celery_monitoring.py`: Task queue testing
- `auto_movie_editor/test_google_integration.py`: External API testing

## Critical Development Patterns

### Video Generation Pipeline
The core video building happens in `auto_movie_editor/tools/run_app.py`:
```python
def build_video(config: VideoBuildConfig) -> Dict[str, Any]:
    # 1. AI text generation using TextGenAPI
    # 2. Media fetching (Pixabay API) 
    # 3. Voice generation via Replicate API
    # 4. Audio transcription with WhisperX
    # 5. Video composition using MoviePy
```

### Progress Monitoring Architecture
Real-time progress uses Redis + polling pattern:
- `VideoProcessingState` class manages Redis state in `fastapi_web/celery_app.py`
- Frontend `ProcessingModal` component polls `/api/redis/processing/{videoId}`
- Key states: `initializing`, `processing`, `completed`, `failed`

### Database Models
- **FastAPI**: SQLModel with PostgreSQL (`fastapi_web/models/db_models.py`)
- **Next.js**: Prisma with PostgreSQL (`ui_auto_movie/prisma/schema.prisma`)
- Both connect to same PostgreSQL instance but have separate schemas

## Essential Commands

### Development Startup (3 terminals required):
```bash
# Terminal 1: FastAPI backend
cd fastapi_web
.\fastapp\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2: Celery worker  
cd fastapi_web
.\fastapp\Scripts\activate
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 3: Next.js frontend
cd ui_auto_movie  
npm run dev
```

### Database Management
```bash
# Prisma migrations (Next.js)
cd ui_auto_movie
npx prisma generate
npx prisma db push
npx prisma studio  # Database GUI

# FastAPI database setup
cd fastapi_web
python models/init_db.py
```

### Video Engine Testing:
```bash
cd auto_movie_editor
.\gen_vedio\Scripts\activate
python tools/run_app.py
```

## Component Integration Patterns

### API Communication
- Frontend makes requests to `http://localhost:8000/api/`
- CORS configured for `localhost:3000`, `3001`, `3002`
- Video creation: `POST /api/videos/create` → returns `video_id` and `task_id`

### Real-time Processing Updates  
```javascript
// ProcessingModal.js pattern
const pollProgress = async () => {
  // Try Redis first for real-time state
  const redisResponse = await fetch(`/api/redis/processing/${videoId}`);
  // Fallback to database for final status
  const dbResponse = await fetch(`/api/videos/status/${videoId}`);
};
```

### Video Configuration
Use `VideoBuildConfig` dataclass in `tools/run_app.py` for all video parameters:
- `target_format`: Format from supported list above
- `voice`: Voice ID for Replicate API
- `use_google_search`: Enable/disable Google Images integration
- `max_words`: Words per transcript segment (default: 5)

## Environment Variables Required

```env
# APIs
OPENAI_API_KEY=
REPLICATE_API_TOKEN= 
PIXABAY_API_KEY=
GOOGLE_CUSTOM_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE=

# Database  
DATABASE_URL=postgresql://user:password@localhost:5432/video_app
POSTGRESQL_DATABASE_URL=postgresql://user:password@localhost:5432/video_app

# Redis/Celery
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# NextAuth.js
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

## Critical Dependencies

- **Video Processing**: MoviePy, FFmpeg
- **AI Services**: OpenAI GPT, Replicate, WhisperX  
- **Task Queue**: Celery + Redis (Windows compatibility requires `pool=solo`)
- **Authentication**: NextAuth.js + bcryptjs
- **Database**: PostgreSQL + Prisma (Next.js) + SQLModel (FastAPI)

## Debugging Workflow

1. **Video Generation Issues**: Check `auto_movie_editor/logs/` and Celery worker output
2. **API Errors**: FastAPI logs at `fastapi_web/logs/auto_video.log`  
3. **Frontend Issues**: Next.js dev server shows React errors
4. **Progress Tracking**: Monitor Redis keys with `redis-cli` or check `/api/redis/processing/{id}`
5. **Database Issues**: Use Prisma Studio or direct PostgreSQL client

## File Organization Logic

- `auto_movie_editor/tools/`: Core video generation engine
- `fastapi_web/models/`: Database models and API logic
- `ui_auto_movie/components/`: Reusable React components (especially `ProcessingModal.js`)
- `ui_auto_movie/app/`: Next.js App Router pages and API routes
- `ui_auto_movie/prisma/`: Database schema and migrations
- `ui_auto_movie/test/`: create test cases for frontend
- `ui_auto_movie/api/`: API routes and handlers
- `ui_auto_movie/auto_task/`: backend task management

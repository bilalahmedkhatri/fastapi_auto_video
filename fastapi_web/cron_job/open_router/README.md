# OpenRouter Models API Client

This module provides a comprehensive solution for fetching AI model information from OpenRouter's API and saving it to your local database.

## Features

- ✅ Fetches all available models from OpenRouter API (327+ models)
- ✅ Parses and normalizes model data (pricing, capabilities, provider info)
- ✅ Saves models to database with intelligent quality scoring
- ✅ Updates existing models and marks inactive ones
- ✅ Comprehensive error handling and logging
- ✅ Command-line interface for automation
- ✅ No API key required for public model listings

## Database Schema

The models are saved to the `AIModel` table with the following fields:

```python
class AIModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: Optional[str] = None                    # e.g., "openai", "anthropic"
    model_name: str = Field(index=True, unique=True)  # e.g., "openai/gpt-4o"
    display_name: Optional[str] = None                # e.g., "OpenAI: GPT-4o"
    is_free: bool = Field(default=False, index=True)
    quality_score: Optional[float] = None             # 0-10 computed score
    context_length: Optional[int] = None
    pricing_prompt: Optional[float] = None            # Per million tokens
    pricing_completion: Optional[float] = None        # Per million tokens
    capabilities: Optional[str] = None                # JSON string
    tags: Optional[str] = None                        # JSON array string
    is_recommended: bool = Field(default=False, index=True)
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    raw_metadata: Optional[str] = None               # Full JSON from API
    active: bool = Field(default=True)
```

## Usage

### Command Line

```bash
# Sync all models from OpenRouter to database
python open_router_models_api.py

# Show current models summary
python open_router_models_api.py --summary

# Use with API key (optional, for rate limiting benefits)
python open_router_models_api.py --api-key YOUR_API_KEY
```

### Python Code

```python
from cron_job.open_router.open_router_models_api import OpenRouterModelsAPI

# Initialize client
client = OpenRouterModelsAPI()

# Sync all models (recommended for first run)
stats = client.sync_models()
print(f"Created: {stats['created']}, Updated: {stats['updated']}")

# Get models summary
summary = client.get_models_summary()
print(f"Total active models: {summary['active_models']}")
print(f"Free models: {summary['free_models']}")
print(f"Recommended models: {summary['recommended_models']}")

# Fetch raw models data (if you need it)
models = client.fetch_models()
print(f"Fetched {len(models)} models from API")
```

### Automated Sync (Cron Job)

Add to your crontab for daily updates:

```bash
# Daily sync at 3 AM
0 3 * * * cd /path/to/your/project && python cron_job/open_router/open_router_models_api.py
```

## Example Output

### Initial Sync
```
INFO:cron_job.open_router.open_router_models_api:Starting OpenRouter models synchronization...
INFO:cron_job.open_router.open_router_models_api:Fetching models from OpenRouter API...
INFO:cron_job.open_router.open_router_models_api:Successfully fetched 327 models from OpenRouter
INFO:cron_job.open_router.open_router_models_api:Database update complete: {'created': 327, 'updated': 0, 'skipped': 0, 'errors': 0}
INFO:cron_job.open_router.open_router_models_api:Synchronization complete: {'created': 327, 'updated': 0, 'skipped': 0, 'errors': 0, 'deactivated': 0}
```

### Summary
```
=== OpenRouter Models Summary ===
Total models: 327
Active models: 327
Free models: 55
Recommended models: 78
Last sync: 2025-09-21 16:23:07

Providers:
  openai: 42
  qwen: 42
  mistralai: 35
  google: 25
  meta-llama: 22
  deepseek: 18
  ...
```

## Model Quality Scoring

The system automatically calculates a quality score (0-10) for each model based on:

- **Context Length**: Higher context = higher score
- **Pricing**: Lower cost = higher score  
- **Free Models**: Get bonus points
- **Popular Providers**: GPT, Claude, etc. get bonus points

Models with quality score > 7 are marked as `is_recommended = True`.

## Model Tags

Automatic tagging based on model characteristics:

- `free` - No cost models
- `openai`, `anthropic`, `meta`, `google` - Provider-based tags
- `multimodal` - Supports multiple input/output types
- `long-context` - Context length > 100K tokens

## Error Handling

- Graceful handling of API failures
- Individual model parsing errors don't stop the entire sync
- Database transaction rollback on commit failures
- Comprehensive logging at all levels

## Performance

- Fetches 327+ models in ~1 second
- Database operations complete in ~2-3 seconds
- Efficient upsert logic (creates new, updates existing)
- Automatic cleanup of inactive models

## Requirements

- `requests` - HTTP client
- `sqlmodel` - Database ORM
- `logging` - Built-in Python logging

## Environment Variables

- `OPENROUTER_API_KEY` - Optional API key for higher rate limits

## Integration

This module integrates seamlessly with the existing FastAPI application and database schema. The `AIModel` table is already defined in `models/db_models.py` and ready to use.
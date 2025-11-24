# Voice Sample Auto-Generation on Server Startup

## Overview
Automatically generates missing voice samples when the FastAPI server starts, with smart checks to avoid unnecessary runs.

## How It Works

### 1. Startup Event (`main.py`)
```python
@app.on_event("startup")
async def on_startup():
    await startup_voice_sample_check()
```

### 2. Smart Checking Logic (`startup_tasks.py`)
The system checks:
- ✅ **Time since last run**: Skip if run < 24 hours ago
- ✅ **Sample count**: Only run if < 40 voices have samples
- ✅ **Background execution**: Doesn't block server startup

### 3. Generation Process
If checks pass:
1. Runs `check_missing_samples()` in background
2. Generates missing voice samples via API
3. Updates database URLs
4. Records completion timestamp

## Configuration

### Thresholds (in `startup_tasks.py`)
```python
MIN_SAMPLE_THRESHOLD = 40      # Run if less than this
CHECK_INTERVAL_HOURS = 24       # Don't run if checked recently
```

### Files
- `server_starting_apps/startup_tasks.py` - Main startup coordinator
- `server_starting_apps/auto_generate_missing_samples.py` - Generation logic
- `server_starting_apps/.last_voice_sample_check` - Timestamp file

## Behavior Examples

### ✅ Will Run
- First server start (no timestamp file)
- < 40 voices have samples
- Last run was > 24 hours ago

### ⏭️ Will Skip
- 46/49 voices have samples (above threshold)
- Last run was 2 hours ago
- Sufficient samples already exist

## Manual Override

### Force Check (ignore timestamp)
```bash
# Delete timestamp file
rm server_starting_apps/.last_voice_sample_check

# Restart server
```

### Run Manually
```bash
python server_starting_apps/auto_generate_missing_samples.py
python server_starting_apps/auto_generate_missing_samples.py --check-only
```

## Logs

### Startup Logs
```
INFO: Voice sample check: Sufficient samples: 46/49
INFO: ⏭️  Skipping voice sample generation
```

OR

```
INFO: Voice sample check: Need samples: 35/49 (threshold: 40)
INFO: 🎙️  Starting voice sample generation...
INFO: ✅ Voice sample generation completed
```

## Rate Limiting
- Free API allows 3 generations per 12 hours
- Script handles rate limits gracefully
- Stops when limit hit, resumes on next run

## Benefits
✅ Hands-off - automatic sample generation
✅ Smart - only runs when needed
✅ Fast - doesn't block server startup
✅ Safe - respects rate limits and intervals
✅ Clean - minimal code changes to main.py

# Rate Limiting Quick Reference

## Quick Start

### Check Current Status
```bash
# Monitor real-time
python server_starting_apps\monitor_openrouter.py

# Run tests
python test\test_rate_limiting.py

# Check account
python -c "from video_builder.ai_apis.text_gen_api import TextGenAPI; print(TextGenAPI().check_openrouter_status())"
```

### Common Commands

```bash
# View logs for rate limiting
tail -f logs/auto_video.log | grep -E "(Rate|429|Retry|Waiting)"

# Update models database
python -m cron_job.open_router.open_router_models_api

# Test single request
curl -X POST http://localhost:8000/script-generator/generate \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "test", "user_id": "test"}'
```

## Rate Limits

| Tier | Rate Limit | Daily Limit |
|------|------------|-------------|
| Free (no credits) | 60 req/min | 50 req/day |
| Free (≥1 credit) | 60 req/min | 500 req/day |
| Our Config | **50 req/min** | N/A |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 429 | Rate Limited | Wait 60s, try different model |
| 500 | Server Error | Retry with backoff |
| 402 | No Credits | Check account balance |

## Backoff Schedule

| Attempt | Delay |
|---------|-------|
| 1st | 1s |
| 2nd | 2s |
| 3rd | 4s |
| 4th | 8s |

## Key Files

```
video_builder/ai_apis/text_gen_api.py    # Main implementation
test/test_rate_limiting.py               # Test suite
server_starting_apps/monitor_openrouter.py  # Monitor
readme_files/openrouter_rate_limiting.md    # Full docs
```

## Troubleshooting

### Still getting 429?
1. Check monitor: `python server_starting_apps\monitor_openrouter.py`
2. Verify limit: Should show <50 req/min
3. Check cooldowns: Monitor shows failed models

### Models not rotating?
1. Run tests: `python test\test_rate_limiting.py`
2. Check failed_models dict in code
3. Verify cooldown_seconds=120

### No delay between retries?
1. Check logs for "Waiting Xs..."
2. Verify time.sleep() is working
3. Run test suite

## Implementation Checklist

- [x] Rate limiting enforcement (50 req/min)
- [x] Model cooldown tracking (120s)
- [x] Exponential backoff (1s, 2s, 4s, 8s)
- [x] 429 error detection
- [x] Model rotation on failure
- [x] Account status monitoring
- [x] Test suite
- [x] Real-time monitor
- [x] Documentation

## Support

**Full Documentation:** `readme_files/openrouter_rate_limiting.md`

**Contact:** Check logs first, then review documentation

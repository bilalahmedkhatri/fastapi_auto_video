# Media Search API Configuration

This document describes the environment variables required for the internet media search functionality.

## Required API Keys

### 1. Pexels API
- **Variable**: `PEXELS_API_KEY`
- **Get your key**: https://www.pexels.com/api/
- **Free tier**: 200 requests per hour
- **Supports**: Photos and Videos
- **License**: Free for commercial use (attribution appreciated)

Example:
```bash
PEXELS_API_KEY=your_pexels_api_key_here
```

### 2. Google Custom Search API
- **Variables**: 
  - `GOOGLE_CUSTOM_SEARCH_API_KEY`
  - `GOOGLE_SEARCH_ENGINE` (Custom Search Engine ID)
- **Get your keys**: 
  - API Key: https://developers.google.com/custom-search/v1/introduction
  - Search Engine ID: https://programmablesearchengine.google.com/
- **Free tier**: 100 queries per day
- **Supports**: Images only
- **License**: Varies by source

Example:
```bash
GOOGLE_CUSTOM_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE=your_custom_search_engine_id_here
```

### 3. Pixabay API (Future)
- **Variable**: `PIXABAY_API_KEY`
- **Status**: Not yet implemented
- **Get your key**: https://pixabay.com/api/docs/

## .env File Template

Add these to your `fastapi_web/.env` file:

```bash
# Pexels API - https://www.pexels.com/api/
PEXELS_API_KEY=

# Google Custom Search - https://developers.google.com/custom-search
GOOGLE_CUSTOM_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE=

# Pixabay API (future) - https://pixabay.com/api/docs/
# PIXABAY_API_KEY=
```

## Checking API Availability

Use the endpoint `/api/media/search/platforms` to check which platforms are configured:

```bash
curl http://localhost:8000/api/media/search/platforms
```

This will return:
```json
{
  "platforms": {
    "pexels": {
      "name": "Pexels",
      "available": true,
      "supports": ["images", "videos"],
      "requires_attribution": true,
      "rate_limit": "200 requests/hour"
    },
    "google": {
      "name": "Google Custom Search",
      "available": true,
      "supports": ["images"],
      "requires_attribution": false,
      "rate_limit": "100 queries/day (free tier)"
    },
    "pixabay": {
      "name": "Pixabay",
      "available": false,
      "supports": ["images", "videos"],
      "requires_attribution": false,
      "rate_limit": "Not implemented"
    }
  },
  "default": "pexels"
}
```

## Testing the Search API

### Example Request

```bash
curl -X POST http://localhost:8000/api/media/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sunset beach",
    "platforms": ["pexels", "google"],
    "media_type": "both",
    "tags": ["nature", "landscape"],
    "keywords": ["ocean", "waves"],
    "per_page": 10,
    "orientation": "landscape"
  }'
```

### Example Response

```json
{
  "status": "success",
  "query": "sunset beach",
  "total_results": 25,
  "results": [
    {
      "id": "pexels-photo-123456",
      "name": "sunset beach - John Doe",
      "type": "image",
      "source": "pexels",
      "url": "https://images.pexels.com/photos/123456/pexels-photo-123456.jpeg",
      "thumbnail": "https://images.pexels.com/photos/123456/pexels-photo-123456.jpeg?auto=compress&cs=tinysrgb&h=350",
      "width": 4000,
      "height": 3000,
      "photographer": "John Doe",
      "license": "Pexels License - Free for commercial use (attribution appreciated)"
    }
  ],
  "platforms_searched": ["pexels", "google"],
  "errors": null
}
```

## Usage in MediaManager

The MediaManager component automatically calls this API when users:
1. Enter a search query
2. Select tags from social media content
3. Add custom keywords
4. Click the "Search" button

The frontend code handles:
- Loading states during search
- Error messages if API fails
- Display of results with source attribution
- Platform availability warnings

## Rate Limits & Best Practices

1. **Pexels**: 200 requests/hour
   - Cache results when possible
   - Don't search on every keystroke
   
2. **Google**: 100 queries/day (free tier)
   - Use sparingly
   - Consider upgrading for production use
   
3. **General**:
   - Implement debouncing on search input
   - Cache popular searches
   - Add loading indicators
   - Handle rate limit errors gracefully

## Attribution Requirements

### Pexels
- Attribution appreciated but not required
- Example: "Photo by [Photographer Name] from Pexels"

### Google
- Varies by image source
- Check individual image licenses

## Troubleshooting

### "API key not configured" error
- Ensure environment variables are set in `.env`
- Restart FastAPI server after adding keys
- Check `.env` file location (should be in `fastapi_web/`)

### Rate limit errors
- Wait until limit resets
- Implement caching
- Consider paid API tiers

### No results found
- Check search query spelling
- Try broader search terms
- Verify API credentials are valid
- Check API status pages

## Next Steps

1. Get API keys from provider websites
2. Add keys to `.env` file
3. Restart FastAPI server
4. Test with `/api/media/search/platforms` endpoint
5. Use MediaManager search functionality

# Cron Job Management System

This directory contains all cron job related automation tools and scripts for the FastAPI application.

## 📁 Directory Structure

### `kokoro_scraper/`
Production-ready Kokoro voice scraping system with comprehensive error handling, monitoring, and database integration.

- **Purpose**: Scrapes 46 Kokoro TTS voices from Replicate
- **Languages**: 7 languages (English US/UK, French, Hindi, Italian, Japanese, Chinese)
- **Features**: File locking, retry mechanisms, health monitoring, alerting
- **Deployment**: Ready for production cron job deployment

## 🚀 Future Cron Jobs

This structure is designed to accommodate additional cron jobs:

```
cron_job/
├── README.md                 # This file
├── kokoro_scraper/          # Kokoro voice scraping system
│   ├── kokoro_voice_scraper.py
│   ├── test_kokoro_scraper.py
│   ├── integrate_kokoro_voices.py
│   └── ... (all Kokoro-related files)
├── future_scraper_1/        # Future: Another scraping system
├── future_automation_2/     # Future: Other automation tools
└── shared_utils/            # Future: Shared utilities across cron jobs
```

## 🔧 Quick Commands

### Kokoro Voice Scraper
```bash
cd kokoro_scraper
python test_kokoro_scraper.py     # Test the system
python integrate_kokoro_voices.py # Add voices to database
python monitor_voice_scraper.py   # Check system health
```

## 📋 Adding New Cron Jobs

When adding new cron job systems:

1. Create a new subdirectory (e.g., `new_scraper/`)
2. Add your scripts and configuration files
3. Include a README.md in the subdirectory
4. Update this main README.md
5. Test thoroughly before production deployment

## 🎯 Current Systems

- ✅ **Kokoro Scraper**: 46 voices across 7 languages - Production Ready
- 🚧 **Future Systems**: Ready for expansion

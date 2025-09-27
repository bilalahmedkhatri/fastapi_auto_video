# Kokoro Voice Scraper

Production-ready scraper for Replicate Kokoro TTS voices with comprehensive error handling, monitoring, and database integration.

## 📊 Overview

- **Total Voices**: 46 across 7 languages
- **Languages**: English (US/UK), French, Hindi, Italian, Japanese, Chinese
- **Status**: Production Ready ✅

## 📁 Files

### Core Scripts
- **`kokoro_voice_scraper.py`** - Main production scraper
- **`integrate_kokoro_voices.py`** - Database integration script
- **`test_kokoro_scraper.py`** - Comprehensive test suite
- **`monitor_voice_scraper.py`** - Health monitoring system

### Configuration & Data
- **`kokoro_voices_backup.json`** - Voice data backup
- **`kokoro_test_results.json`** - Test results
- **`install_voice_scraper.sh`** - Production installation script
- **`solution_summary.py`** - System overview display

### Documentation
- **`AI_VOICES_README.md`** - Complete API documentation
- **`VOICE_SYSTEM_SUMMARY.md`** - System summary
- **`README.md`** - This file

## 🚀 Quick Start

```bash
# Test the system
python test_kokoro_scraper.py

# Integrate voices (one-time setup)
python integrate_kokoro_voices.py

# Manual scrape
python kokoro_voice_scraper.py

# Monitor health
python monitor_voice_scraper.py

# View system overview
python solution_summary.py
```

## 🔧 Cron Job Setup

Weekly execution at 6 AM Sunday:
```bash
0 6 * * 0 cd /path/to/cron_job/kokoro_scraper && python kokoro_voice_scraper.py >> logs/scraper.log 2>&1
```

## 📈 Voice Breakdown

- **American English 🇺🇸**: 18 voices (10F, 8M)
- **British English 🇬🇧**: 8 voices (4F, 4M)  
- **Mandarin Chinese 🇨🇳**: 8 voices (4F, 4M)
- **Japanese 🇯🇵**: 5 voices (4F, 1M)
- **Hindi 🇮🇳**: 4 voices (2F, 2M)
- **Italian 🇮🇹**: 2 voices (1F, 1M)
- **French 🇫🇷**: 1 voice (1F)

## 🎯 Production Features

- ✅ File locking prevents concurrent runs
- ✅ Retry mechanisms with exponential backoff
- ✅ Comprehensive logging with rotation
- ✅ Fallback SQLite database
- ✅ Health monitoring and alerting
- ✅ Windows/Linux compatibility
- ✅ Unicode support for international voices

# Kokoro Voice Scraper - Production Deployment Guide

## 🎯 Overview

This system provides a robust, production-ready scraper for Kokoro TTS voices from Replicate. It's designed specifically for cron job deployment with comprehensive error handling, monitoring, and fallback mechanisms.

## 📁 File Structure

```
kokoro-voice-scraper/
├── kokoro_voice_scraper.py         # Main scraper with production error handling
├── kokoro_scraper.conf             # Configuration file
├── install_voice_scraper.sh        # Production installation script
├── monitor_voice_scraper.py        # Health monitoring and alerts
├── test_kokoro_scraper.py          # Comprehensive test suite
├── integrate_kokoro_voices.py      # Database integration script
└── docs/
    ├── DEPLOYMENT.md               # This file
    ├── CONFIGURATION.md            # Configuration guide
    └── MONITORING.md               # Monitoring setup
```

## 🚀 Features

### Production-Ready Architecture
- **File-based locking** to prevent concurrent executions
- **Comprehensive logging** with configurable retention
- **Retry mechanisms** with exponential backoff
- **Fallback database** for when main DB is unavailable
- **Unicode handling** for international voices
- **Error recovery** and graceful degradation

### Voice Data Extraction
- **46 Kokoro voices** across 7 languages
- **Automated metadata mapping** based on voice IDs
- **Quality grade estimation** using voice patterns
- **Multi-language support** (EN, EN-GB, FR, HI, IT, JA, ZH)
- **Gender detection** from voice ID prefixes

### Monitoring & Alerting
- **Health check endpoints** for monitoring systems
- **Email and Slack alerts** for failures
- **Execution metrics** and statistics
- **Disk space monitoring** for log directories
- **Lock file age detection** for stale processes

## 📊 Voice Data

The scraper extracts **46 voices** from the Kokoro model:

| Language | Voices | Female | Male |
|----------|--------|--------|------|
| American English 🇺🇸 | 18 | 10 | 8 |
| British English 🇬🇧 | 8 | 4 | 4 |
| French 🇫🇷 | 1 | 1 | 0 |
| Hindi 🇮🇳 | 4 | 2 | 2 |
| Italian 🇮🇹 | 2 | 1 | 1 |
| Japanese 🇯🇵 | 5 | 4 | 1 |
| Mandarin Chinese 🇨🇳 | 8 | 4 | 4 |

### Sample Voices
- **af_bella** - High-quality American female voice
- **bf_emma** - British female voice with excellent quality
- **jf_alpha** - Japanese female voice
- **zm_yunxi** - Chinese male voice
- **hf_alpha** - Hindi female voice

## 🛠 Quick Start

### 1. Test the Scraper
```bash
# Basic test (dry run)
python test_kokoro_scraper.py

# Test actual scraping (dry run)
python kokoro_voice_scraper.py --dry-run
```

### 2. Integrate Voices into Database
```bash
# Add voices to your existing database
python integrate_kokoro_voices.py
```

### 3. Set up Production Deployment
```bash
# Install for production (Linux/Unix)
sudo ./install_voice_scraper.sh

# Manual setup (Windows/other)
# See DEPLOYMENT.md for detailed instructions
```

## ⚙️ Configuration

### Environment Variables
```bash
# Database connection
POSTGRES_URL=postgresql://user:pass@localhost/db

# Optional: API keys
REPLICATE_API_TOKEN=your_token_here

# Optional: Alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL=admin@yourcompany.com
```

### Command Line Options
```bash
python kokoro_voice_scraper.py [OPTIONS]

Options:
  --dry-run              Simulate without making changes
  --update-existing      Update existing voice entries
  --languages en,ja      Comma-separated language codes
```

## 🔄 Cron Job Setup

### Traditional Cron
```bash
# Run weekly on Sundays at 6 AM
0 6 * * 0 /opt/voice-scraper/run_scraper.sh >> /var/log/voice-scraper/cron.log 2>&1
```

### Systemd Timer (Recommended)
```bash
# Enable and start the timer
sudo systemctl enable voice-scraper.timer
sudo systemctl start voice-scraper.timer

# Check status
sudo systemctl status voice-scraper.timer
```

## 📈 Monitoring

### Health Check Endpoints
```bash
# Basic health check
curl http://localhost:8000/health/voice-scraper

# Detailed health report
python monitor_voice_scraper.py
```

### Log Analysis
```bash
# View recent logs
tail -f /var/log/voice-scraper/kokoro_scraper_*.log

# Check for errors
grep -i error /var/log/voice-scraper/kokoro_scraper_*.log
```

### Key Metrics to Monitor
- **Execution frequency** - Should run weekly
- **Voice count** - Should be 46 voices
- **Error rates** - Should be < 5%
- **Execution time** - Should be < 30 seconds
- **Disk usage** - Log directory growth

## 🔧 Error Handling

### Common Issues and Solutions

#### 1. No Voices Found
```bash
# Check webpage access
curl -I https://replicate.com/jaaari/kokoro-82m

# Run with debug logging
python kokoro_voice_scraper.py --dry-run 2>&1 | grep -i error
```

#### 2. Database Connection Errors
```bash
# Check database connectivity
python -c "from models.db_models import get_session; next(get_session())"

# Check environment variables
echo $POSTGRES_URL
```

#### 3. Lock File Issues
```bash
# Check for stale locks
ls -la /tmp/kokoro_scraper.lock

# Remove stale lock (only if process is not running)
sudo rm /tmp/kokoro_scraper.lock
```

### Error Recovery
- **Automatic retries** with exponential backoff
- **Fallback database** for critical failures
- **Graceful degradation** when services unavailable
- **Detailed error logging** for troubleshooting

## 🔐 Security Considerations

### File Permissions
```bash
# Scraper files should be owned by scraper user
chown voice-scraper:voice-scraper /opt/voice-scraper/*

# Log directory permissions
chmod 755 /var/log/voice-scraper
```

### Network Security
- Use HTTPS for all external requests
- Validate SSL certificates
- Rate limit API requests
- Use secure webhook URLs for alerts

### Database Security
- Use connection pooling
- Encrypt database connections
- Use least-privilege database users
- Sanitize all inputs

## 📝 Maintenance

### Regular Tasks
- **Weekly**: Check scraper execution logs
- **Monthly**: Review disk usage and clean old logs
- **Quarterly**: Update voice metadata if Replicate changes
- **Yearly**: Review and update security configurations

### Log Rotation
Logs are automatically rotated using logrotate configuration:
```bash
# Check logrotate config
cat /etc/logrotate.d/voice-scraper

# Manual rotation test
sudo logrotate -d /etc/logrotate.d/voice-scraper
```

## 🆘 Troubleshooting

### Debug Mode
```bash
# Enable debug logging
export SCRAPER_LOG_LEVEL=DEBUG
python kokoro_voice_scraper.py --dry-run
```

### Health Check Script
```bash
# Run comprehensive health check
python monitor_voice_scraper.py

# Check specific component
python -c "from monitor_voice_scraper import ScraperMonitor; m = ScraperMonitor({}); print(m.check_recent_execution())"
```

### Recovery Procedures
1. **Stale Lock**: Remove lock file and restart
2. **Database Issues**: Check connection and restart service
3. **Missing Voices**: Verify Replicate page structure
4. **High Error Rate**: Check logs and network connectivity

## 📞 Support

### Log Files Locations
- **Scraper logs**: `/var/log/voice-scraper/`
- **Cron logs**: `/var/log/voice-scraper/cron.log`
- **System logs**: Check systemd journal

### Key Commands
```bash
# Check service status
systemctl status voice-scraper.service

# View logs
journalctl -u voice-scraper.service -f

# Test configuration
python kokoro_voice_scraper.py --help
```

## 🔄 Updates and Maintenance

### Updating the Scraper
```bash
# Backup current version
cp /opt/voice-scraper/kokoro_voice_scraper.py /opt/voice-scraper/kokoro_voice_scraper.py.bak

# Update script
sudo cp new_kokoro_voice_scraper.py /opt/voice-scraper/

# Test new version
sudo -u voice-scraper /opt/voice-scraper/run_scraper.sh --dry-run

# Reload systemd if needed
sudo systemctl daemon-reload
```

This system is designed for reliability and ease of maintenance. For specific deployment scenarios or custom configurations, see the additional documentation files.

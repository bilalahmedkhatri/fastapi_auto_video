#!/bin/bash
# Kokoro Voice Scraper Installation Script
# Sets up the scraper for production cron job deployment

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/voice-scraper"
LOG_DIR="/var/log/voice-scraper"
DATA_DIR="/var/lib/voice-scraper"
BACKUP_DIR="/var/backups/voice-scraper"
USER="voice-scraper"
GROUP="voice-scraper"

echo "🚀 Installing Kokoro Voice Scraper for production..."

# Create system user
if ! id "$USER" &>/dev/null; then
    echo "Creating system user: $USER"
    sudo useradd -r -s /bin/false -d "$DATA_DIR" "$USER"
fi

# Create directories
echo "Creating directories..."
sudo mkdir -p "$INSTALL_DIR" "$LOG_DIR" "$DATA_DIR" "$BACKUP_DIR"
sudo chown "$USER:$GROUP" "$LOG_DIR" "$DATA_DIR" "$BACKUP_DIR"
sudo chmod 755 "$LOG_DIR" "$DATA_DIR" "$BACKUP_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Copy files
echo "Copying scraper files..."
sudo cp "$SCRIPT_DIR/kokoro_voice_scraper.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/kokoro_scraper.conf" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/models" "$INSTALL_DIR/" -r 2>/dev/null || true

# Set permissions
sudo chown -R "$USER:$GROUP" "$INSTALL_DIR"
sudo chmod +x "$INSTALL_DIR/kokoro_voice_scraper.py"

# Create wrapper script for cron
cat << 'EOF' | sudo tee "$INSTALL_DIR/run_scraper.sh"
#!/bin/bash
# Wrapper script for cron job execution

cd /opt/voice-scraper
export PATH="/usr/local/bin:/usr/bin:/bin"
export PYTHONPATH="/opt/voice-scraper:$PYTHONPATH"

# Load environment variables
if [ -f /opt/voice-scraper/.env ]; then
    source /opt/voice-scraper/.env
fi

# Run the scraper
python3 /opt/voice-scraper/kokoro_voice_scraper.py "$@"
EOF

sudo chmod +x "$INSTALL_DIR/run_scraper.sh"
sudo chown "$USER:$GROUP" "$INSTALL_DIR/run_scraper.sh"

# Create environment file template
cat << 'EOF' | sudo tee "$INSTALL_DIR/.env.template"
# Environment variables for Kokoro Voice Scraper
# Copy this to .env and fill in your values

# Database connection
POSTGRES_URL=postgresql://username:password@localhost/database_name

# Optional: API keys for enhanced features
REPLICATE_API_TOKEN=your_token_here

# Optional: Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_EMAIL=admin@yourcompany.com

# Optional: Custom settings
SCRAPER_LOG_LEVEL=INFO
SCRAPER_DRY_RUN=false
EOF

# Create logrotate configuration
cat << 'EOF' | sudo tee /etc/logrotate.d/voice-scraper
/var/log/voice-scraper/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su voice-scraper voice-scraper
}
EOF

# Create systemd service (optional)
cat << 'EOF' | sudo tee /etc/systemd/system/voice-scraper.service
[Unit]
Description=Kokoro Voice Scraper
After=network.target postgresql.service

[Service]
Type=oneshot
User=voice-scraper
Group=voice-scraper
WorkingDirectory=/opt/voice-scraper
Environment=PYTHONPATH=/opt/voice-scraper
EnvironmentFile=-/opt/voice-scraper/.env
ExecStart=/opt/voice-scraper/run_scraper.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for automatic execution
cat << 'EOF' | sudo tee /etc/systemd/system/voice-scraper.timer
[Unit]
Description=Run Kokoro Voice Scraper weekly
Requires=voice-scraper.service

[Timer]
OnCalendar=Sun 06:00
Persistent=true
RandomizedDelaySec=1800

[Install]
WantedBy=timers.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Create health check script
cat << 'EOF' | sudo tee "$INSTALL_DIR/health_check.py"
#!/usr/bin/env python3
"""
Health check script for Kokoro Voice Scraper
Returns 0 if everything is healthy, non-zero otherwise
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def check_recent_execution():
    """Check if scraper ran recently"""
    log_dir = Path("/var/log/voice-scraper")
    if not log_dir.exists():
        return False, "Log directory not found"
    
    # Check for recent log files
    recent_logs = []
    cutoff = datetime.now() - timedelta(days=7)
    
    for log_file in log_dir.glob("kokoro_scraper_*.log"):
        if log_file.stat().st_mtime > cutoff.timestamp():
            recent_logs.append(log_file)
    
    if not recent_logs:
        return False, "No recent execution logs found"
    
    return True, f"Found {len(recent_logs)} recent log files"

def check_database_health():
    """Check fallback database health"""
    fallback_db = Path("/var/lib/voice-scraper/kokoro_voices_fallback.db")
    
    if not fallback_db.exists():
        return True, "Fallback database not created yet"
    
    try:
        conn = sqlite3.connect(str(fallback_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kokoro_voices")
        count = cursor.fetchone()[0]
        conn.close()
        
        return True, f"Fallback database has {count} voices"
    except Exception as e:
        return False, f"Fallback database error: {e}"

def main():
    checks = [
        ("Recent Execution", check_recent_execution),
        ("Database Health", check_database_health),
    ]
    
    all_healthy = True
    results = []
    
    for check_name, check_func in checks:
        try:
            healthy, message = check_func()
            results.append({
                "check": check_name,
                "healthy": healthy,
                "message": message
            })
            
            if not healthy:
                all_healthy = False
                
        except Exception as e:
            results.append({
                "check": check_name,
                "healthy": False,
                "message": f"Check failed: {e}"
            })
            all_healthy = False
    
    # Output results
    print(json.dumps({
        "healthy": all_healthy,
        "checks": results,
        "timestamp": datetime.now().isoformat()
    }, indent=2))
    
    return 0 if all_healthy else 1

if __name__ == "__main__":
    sys.exit(main())
EOF

sudo chmod +x "$INSTALL_DIR/health_check.py"
sudo chown "$USER:$GROUP" "$INSTALL_DIR/health_check.py"

echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Copy .env.template to .env and configure your database connection"
echo "   sudo cp $INSTALL_DIR/.env.template $INSTALL_DIR/.env"
echo "   sudo nano $INSTALL_DIR/.env"
echo ""
echo "2. Test the scraper:"
echo "   sudo -u $USER $INSTALL_DIR/run_scraper.sh --dry-run"
echo ""
echo "3. Set up cron job (choose one option):"
echo "   Option A - Traditional cron:"
echo "   sudo crontab -u $USER -e"
echo "   Add: 0 6 * * 0 $INSTALL_DIR/run_scraper.sh >> /var/log/voice-scraper/cron.log 2>&1"
echo ""
echo "   Option B - Systemd timer (recommended):"
echo "   sudo systemctl enable voice-scraper.timer"
echo "   sudo systemctl start voice-scraper.timer"
echo ""
echo "4. Set up monitoring:"
echo "   curl http://localhost/health/voice-scraper"
echo "   python3 $INSTALL_DIR/health_check.py"
echo ""
echo "📁 Files installed in: $INSTALL_DIR"
echo "📊 Logs will be in: $LOG_DIR"
echo "💾 Data directory: $DATA_DIR"
echo "🔄 Backups in: $BACKUP_DIR"

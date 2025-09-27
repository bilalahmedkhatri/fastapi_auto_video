# Kokoro Voice Scraper - Monitoring and Alerts

import os
import json
import smtplib
import requests
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional

class ScraperMonitor:
    """Monitoring and alerting for the voice scraper"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alerts = []
    
    def check_scraper_health(self) -> Dict:
        """Perform comprehensive health checks"""
        health_status = {
            "overall_healthy": True,
            "checks": [],
            "timestamp": datetime.now().isoformat(),
            "alerts": []
        }
        
        # Check 1: Recent execution
        recent_check = self.check_recent_execution()
        health_status["checks"].append(recent_check)
        if not recent_check["passed"]:
            health_status["overall_healthy"] = False
            self.alerts.append(f"❌ Recent execution check failed: {recent_check['message']}")
        
        # Check 2: Database connectivity
        db_check = self.check_database_connectivity()
        health_status["checks"].append(db_check)
        if not db_check["passed"]:
            health_status["overall_healthy"] = False
            self.alerts.append(f"❌ Database check failed: {db_check['message']}")
        
        # Check 3: Log file health
        log_check = self.check_log_health()
        health_status["checks"].append(log_check)
        if not log_check["passed"]:
            health_status["overall_healthy"] = False
            self.alerts.append(f"❌ Log health check failed: {log_check['message']}")
        
        # Check 4: Disk space
        disk_check = self.check_disk_space()
        health_status["checks"].append(disk_check)
        if not disk_check["passed"]:
            health_status["overall_healthy"] = False
            self.alerts.append(f"❌ Disk space check failed: {disk_check['message']}")
        
        # Check 5: Lock file status
        lock_check = self.check_lock_file_status()
        health_status["checks"].append(lock_check)
        if not lock_check["passed"]:
            self.alerts.append(f"⚠️ Lock file issue: {lock_check['message']}")
        
        health_status["alerts"] = self.alerts
        return health_status
    
    def check_recent_execution(self) -> Dict:
        """Check if scraper executed recently"""
        try:
            log_dir = "/var/log/voice-scraper"
            if not os.path.exists(log_dir):
                return {
                    "name": "Recent Execution",
                    "passed": False,
                    "message": "Log directory does not exist",
                    "details": {"log_dir": log_dir}
                }
            
            # Check for recent log files (within last 7 days)
            import glob
            from datetime import timedelta
            
            recent_logs = []
            cutoff_time = datetime.now() - timedelta(days=7)
            
            for log_file in glob.glob(f"{log_dir}/kokoro_scraper_*.log"):
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if mtime > cutoff_time:
                    recent_logs.append({
                        "file": os.path.basename(log_file),
                        "modified": mtime.isoformat()
                    })
            
            if recent_logs:
                return {
                    "name": "Recent Execution",
                    "passed": True,
                    "message": f"Found {len(recent_logs)} recent executions",
                    "details": {"recent_logs": recent_logs}
                }
            else:
                return {
                    "name": "Recent Execution", 
                    "passed": False,
                    "message": "No recent executions found",
                    "details": {"cutoff_time": cutoff_time.isoformat()}
                }
                
        except Exception as e:
            return {
                "name": "Recent Execution",
                "passed": False,
                "message": f"Check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def check_database_connectivity(self) -> Dict:
        """Check database connectivity"""
        try:
            # Try to import and test database connection
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent.parent))
            
            from models.db_models import get_session, SelectAIVoices
            from sqlmodel import select
            
            with next(get_session()) as session:
                # Simple query to test connectivity
                result = session.exec(select(SelectAIVoices).limit(1))
                voice = result.first()
                
                return {
                    "name": "Database Connectivity",
                    "passed": True,
                    "message": "Database connection successful",
                    "details": {"has_voices": voice is not None}
                }
                
        except ImportError as e:
            return {
                "name": "Database Connectivity", 
                "passed": False,
                "message": "Database models not available",
                "details": {"error": str(e)}
            }
        except Exception as e:
            return {
                "name": "Database Connectivity",
                "passed": False, 
                "message": f"Database connection failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def check_log_health(self) -> Dict:
        """Check log file health and errors"""
        try:
            log_dir = "/var/log/voice-scraper"
            if not os.path.exists(log_dir):
                return {
                    "name": "Log Health",
                    "passed": False,
                    "message": "Log directory missing",
                    "details": {}
                }
            
            # Get most recent log file
            import glob
            log_files = glob.glob(f"{log_dir}/kokoro_scraper_*.log")
            if not log_files:
                return {
                    "name": "Log Health", 
                    "passed": False,
                    "message": "No log files found",
                    "details": {}
                }
            
            latest_log = max(log_files, key=os.path.getmtime)
            
            # Analyze log content
            error_count = 0
            warning_count = 0
            success_indicators = 0
            
            with open(latest_log, 'r') as f:
                for line in f:
                    line_lower = line.lower()
                    if 'error' in line_lower:
                        error_count += 1
                    elif 'warning' in line_lower:
                        warning_count += 1
                    elif any(indicator in line_lower for indicator in ['success', 'completed', 'added voice', 'updated voice']):
                        success_indicators += 1
            
            # Determine health status
            if error_count > 10:  # High error threshold
                passed = False
                message = f"High error count: {error_count} errors"
            elif error_count > 0 and success_indicators == 0:
                passed = False
                message = f"Errors with no success indicators: {error_count} errors"
            else:
                passed = True
                message = f"Log health OK: {error_count} errors, {warning_count} warnings"
            
            return {
                "name": "Log Health",
                "passed": passed,
                "message": message,
                "details": {
                    "latest_log": os.path.basename(latest_log),
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "success_indicators": success_indicators
                }
            }
            
        except Exception as e:
            return {
                "name": "Log Health",
                "passed": False,
                "message": f"Log analysis failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def check_disk_space(self) -> Dict:
        """Check available disk space"""
        try:
            import shutil
            
            paths_to_check = [
                "/var/log/voice-scraper",
                "/var/lib/voice-scraper", 
                "/var/backups/voice-scraper"
            ]
            
            disk_info = {}
            critical_threshold = 0.95  # 95% full
            warning_threshold = 0.85   # 85% full
            
            overall_passed = True
            messages = []
            
            for path in paths_to_check:
                if os.path.exists(path):
                    total, used, free = shutil.disk_usage(path)
                    usage_percent = used / total
                    
                    disk_info[path] = {
                        "total_gb": round(total / (1024**3), 2),
                        "used_gb": round(used / (1024**3), 2),
                        "free_gb": round(free / (1024**3), 2),
                        "usage_percent": round(usage_percent * 100, 1)
                    }
                    
                    if usage_percent > critical_threshold:
                        overall_passed = False
                        messages.append(f"{path}: Critical disk usage {disk_info[path]['usage_percent']}%")
                    elif usage_percent > warning_threshold:
                        messages.append(f"{path}: High disk usage {disk_info[path]['usage_percent']}%")
            
            if overall_passed and not messages:
                message = "Disk space healthy"
            elif overall_passed:
                message = f"Disk space OK with warnings: {'; '.join(messages)}"
            else:
                message = f"Critical disk space issues: {'; '.join(messages)}"
            
            return {
                "name": "Disk Space",
                "passed": overall_passed,
                "message": message,
                "details": disk_info
            }
            
        except Exception as e:
            return {
                "name": "Disk Space",
                "passed": False,
                "message": f"Disk check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def check_lock_file_status(self) -> Dict:
        """Check for stale lock files"""
        try:
            lock_file = "/tmp/kokoro_scraper.lock"
            
            if not os.path.exists(lock_file):
                return {
                    "name": "Lock File Status",
                    "passed": True,
                    "message": "No lock file present",
                    "details": {}
                }
            
            # Check lock file age
            lock_age = datetime.now().timestamp() - os.path.getmtime(lock_file)
            max_age = 3600  # 1 hour
            
            if lock_age > max_age:
                return {
                    "name": "Lock File Status",
                    "passed": False,
                    "message": f"Stale lock file detected ({lock_age/60:.1f} minutes old)",
                    "details": {
                        "lock_file": lock_file,
                        "age_minutes": round(lock_age / 60, 1),
                        "max_age_minutes": max_age / 60
                    }
                }
            else:
                return {
                    "name": "Lock File Status", 
                    "passed": True,
                    "message": f"Recent lock file ({lock_age/60:.1f} minutes old)",
                    "details": {
                        "lock_file": lock_file,
                        "age_minutes": round(lock_age / 60, 1)
                    }
                }
                
        except Exception as e:
            return {
                "name": "Lock File Status",
                "passed": False,
                "message": f"Lock file check failed: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def send_alerts(self, health_status: Dict):
        """Send alerts if there are issues"""
        if health_status["overall_healthy"]:
            return  # No alerts needed
        
        alert_message = self.format_alert_message(health_status)
        
        # Send email alert
        if self.config.get("alert_email"):
            self.send_email_alert(alert_message)
        
        # Send Slack alert  
        if self.config.get("slack_webhook"):
            self.send_slack_alert(alert_message)
    
    def format_alert_message(self, health_status: Dict) -> str:
        """Format alert message"""
        message = "🚨 Kokoro Voice Scraper Health Alert\n\n"
        message += f"Timestamp: {health_status['timestamp']}\n"
        message += f"Overall Status: {'✅ HEALTHY' if health_status['overall_healthy'] else '❌ UNHEALTHY'}\n\n"
        
        message += "Failed Checks:\n"
        for check in health_status["checks"]:
            if not check["passed"]:
                message += f"• {check['name']}: {check['message']}\n"
        
        message += "\nAll Alerts:\n"
        for alert in health_status["alerts"]:
            message += f"• {alert}\n"
        
        message += "\nRecommended Actions:\n"
        message += "1. Check scraper logs: /var/log/voice-scraper/\n" 
        message += "2. Verify database connectivity\n"
        message += "3. Check disk space and clean up if needed\n"
        message += "4. Restart scraper service if necessary\n"
        
        return message
    
    def send_email_alert(self, message: str):
        """Send email alert"""
        try:
            # This is a basic example - configure SMTP settings as needed
            msg = MimeText(message)
            msg['Subject'] = 'Kokoro Voice Scraper Alert'
            msg['From'] = 'voice-scraper@yourcompany.com'
            msg['To'] = self.config["alert_email"]
            
            # Note: Configure SMTP server settings
            # server = smtplib.SMTP('localhost')
            # server.send_message(msg)
            # server.quit()
            
            print(f"Email alert would be sent to: {self.config['alert_email']}")
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, message: str):
        """Send Slack alert"""
        try:
            payload = {
                "text": "Kokoro Voice Scraper Alert",
                "attachments": [
                    {
                        "color": "danger",
                        "text": message,
                        "ts": datetime.now().timestamp()
                    }
                ]
            }
            
            response = requests.post(self.config["slack_webhook"], json=payload)
            response.raise_for_status()
            
            print("Slack alert sent successfully")
            
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")

def main():
    """Main monitoring function"""
    config = {
        "alert_email": os.getenv("ALERT_EMAIL"),
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL")
    }
    
    monitor = ScraperMonitor(config)
    health_status = monitor.check_scraper_health()
    
    # Print status
    print(json.dumps(health_status, indent=2))
    
    # Send alerts if needed
    monitor.send_alerts(health_status)
    
    # Return exit code for monitoring systems
    return 0 if health_status["overall_healthy"] else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

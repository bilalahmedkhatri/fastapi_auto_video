"""
OpenRouter API Monitor

Real-time monitoring script for OpenRouter API usage and rate limiting.
Displays current status, request counts, and alerts when approaching limits.

Usage:
    python monitor_openrouter.py [--interval SECONDS]
    
Example:
    python monitor_openrouter.py --interval 5
"""

import sys
import os
import time
import argparse
from datetime import datetime
from collections import deque

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_builder.ai_apis.text_gen_api import TextGenAPI


class OpenRouterMonitor:
    """Monitor OpenRouter API usage and rate limits"""
    
    def __init__(self):
        self.api = TextGenAPI()
        self.request_history = deque(maxlen=1000)
        
    def get_current_stats(self):
        """Get current API statistics"""
        now = time.time()
        
        # Count requests in last minute
        recent_requests = [ts for ts in self.api.request_timestamps if now - ts < 60]
        requests_per_minute = len(recent_requests)
        
        # Count requests in last 10 minutes
        ten_min_requests = [ts for ts in self.api.request_timestamps if now - ts < 600]
        
        # Get failed models count
        active_cooldowns = [
            model for model, ts in self.api.failed_models.items()
            if now - ts < 120
        ]
        
        return {
            "requests_last_minute": requests_per_minute,
            "requests_last_10min": len(ten_min_requests),
            "total_requests": len(self.api.request_timestamps),
            "cooldown_models": len(active_cooldowns),
            "cooldown_models_list": active_cooldowns,
            "timestamp": datetime.now()
        }
    
    def display_stats(self, stats):
        """Display statistics in terminal"""
        # Clear screen (works on Windows and Unix)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 70)
        print("OpenRouter API Monitor".center(70))
        print("=" * 70)
        print(f"Time: {stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        
        # Rate limit status
        rpm = stats['requests_last_minute']
        limit = 60
        percentage = (rpm / limit) * 100
        
        print(f"\n📊 RATE LIMIT STATUS:")
        print(f"  Requests/Minute: {rpm}/{limit} ({percentage:.1f}%)")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * rpm / limit)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Color based on usage
        if percentage < 50:
            status = "🟢 SAFE"
        elif percentage < 80:
            status = "🟡 CAUTION"
        else:
            status = "🔴 DANGER"
        
        print(f"  [{bar}] {status}")
        
        # Other stats
        print(f"\n📈 ACTIVITY:")
        print(f"  Last 10 minutes: {stats['requests_last_10min']} requests")
        print(f"  Total tracked: {stats['total_requests']} requests")
        
        # Cooldown models
        print(f"\n⏳ MODELS IN COOLDOWN: {stats['cooldown_models']}")
        if stats['cooldown_models_list']:
            for model in stats['cooldown_models_list']:
                print(f"  - {model}")
        else:
            print(f"  - None")
        
        # OpenRouter account status
        print(f"\n💳 ACCOUNT STATUS:")
        try:
            account_status = self.api.check_openrouter_status()
            if account_status:
                print(f"  Label: {account_status.get('label', 'N/A')}")
                print(f"  Usage: {account_status.get('usage', 'N/A')}")
                print(f"  Limit: {account_status.get('limit', 'N/A')}")
            else:
                print(f"  Status: Unable to fetch (check API key)")
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        print("\n" + "=" * 70)
        print("Press Ctrl+C to stop monitoring")
        print("=" * 70)
    
    def run(self, interval=5):
        """Run monitoring loop"""
        print(f"Starting OpenRouter API monitor (refresh every {interval}s)...\n")
        
        try:
            while True:
                stats = self.get_current_stats()
                self.display_stats(stats)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user.")
            print(f"Final stats:")
            final_stats = self.get_current_stats()
            print(f"  Total requests tracked: {final_stats['total_requests']}")
            print(f"  Models in cooldown: {final_stats['cooldown_models']}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor OpenRouter API usage and rate limits"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )
    
    args = parser.parse_args()
    
    monitor = OpenRouterMonitor()
    monitor.run(interval=args.interval)


if __name__ == "__main__":
    main()

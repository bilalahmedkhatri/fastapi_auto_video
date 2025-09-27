#!/usr/bin/env python3
"""
Kokoro Voices Scraper for Cron Job
A robust scraper for Replicate Kokoro voices with comprehensive error handling,
logging, retry mechanisms, and database integration suitable for production cron jobs.

Usage:
    python kokoro_voice_scraper.py [--dry-run] [--update-existing] [--languages en,ja]
    
Cron job example:
    0 6 * * 0 /usr/bin/python3 /path/to/kokoro_voice_scraper.py >> /var/log/voice_scraper.log 2>&1
"""

import os
import sys
import re
import json
import time
import logging
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import sqlite3
from contextlib import contextmanager

# Add models directory to path
sys.path.append(str(Path(__file__).parent / 'models'))
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from models.db_models import SelectAIVoices, get_session, engine
    from sqlmodel import Session, select
    DB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Database models not available: {e}")
    DB_AVAILABLE = False

# Configuration
class Config:
    REPLICATE_URL = "https://replicate.com/jaaari/kokoro-82m"
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    REQUEST_TIMEOUT = 30
    LOG_RETENTION_DAYS = 30
    BACKUP_FILE = "kokoro_voices_backup.json"
    LOCK_FILE = os.path.join(os.getenv('TEMP', '.'), "kokoro_scraper.lock")
    
    # Fallback database for when main DB is unavailable
    FALLBACK_DB = "kokoro_voices_fallback.db"

@dataclass
class VoiceData:
    """Data class for voice information"""
    voice_id: str
    gender: str
    language: str
    language_code: str
    accent: str
    quality_grade: str
    training_duration: str
    overall_grade: str
    hash_id: str
    special_features: Optional[str] = None
    provider: str = "kokoro"
    is_premium: bool = True
    is_demo: bool = False
    
    def to_db_dict(self) -> Dict:
        """Convert to database format"""
        return {
            "voice_id": self.voice_id,
            "voice_name": self.voice_id.replace('_', ' ').title(),
            "voice_description": self.generate_description(),
            "gender": self.gender,
            "age_group": "adult",  # Default for Kokoro voices
            "accent": self.accent,
            "language": self.language_code,
            "voice_sample_url": f"https://replicate.com/jaaari/kokoro-82m?voice={self.voice_id}",
            "is_demo": self.is_demo,
            "is_premium": self.is_premium,
            "provider": self.provider,
            "model_name": "kokoro-82m",
            "voice_settings": json.dumps({
                "quality_grade": self.quality_grade,
                "training_duration": self.training_duration,
                "overall_grade": self.overall_grade,
                "hash_id": self.hash_id,
                "special_features": self.special_features
            }),
            "is_active": True
        }
    
    def generate_description(self) -> str:
        """Generate voice description"""
        base = f"{self.gender.title()} {self.accent} voice"
        
        if self.special_features:
            if "🔥" in self.special_features:
                base += " (high quality)"
            if "🎧" in self.special_features:
                base += " (studio quality)"
        
        quality_desc = {
            "A": "excellent quality",
            "B": "good quality", 
            "C": "standard quality",
            "D": "basic quality"
        }.get(self.quality_grade, "")
        
        if quality_desc:
            base += f" with {quality_desc}"
            
        return base

class KokoroVoiceScraper:
    """Main scraper class with comprehensive error handling"""
    
    def __init__(self, dry_run: bool = False, update_existing: bool = False):
        self.dry_run = dry_run
        self.update_existing = update_existing
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.stats = {
            "start_time": datetime.now(),
            "voices_found": 0,
            "voices_added": 0,
            "voices_updated": 0,
            "errors": 0,
            "warnings": 0
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Clean old logs
        self.cleanup_old_logs(log_dir)
        
        # Setup logging with UTF-8 encoding for Windows
        log_file = log_dir / f"kokoro_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure logging with UTF-8 encoding
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Set formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    def cleanup_old_logs(self, log_dir: Path):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=Config.LOG_RETENTION_DAYS)
            for log_file in log_dir.glob("kokoro_scraper_*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    print(f"Deleted old log: {log_file}")
        except Exception as e:
            print(f"Warning: Could not cleanup old logs: {e}")
    
    @contextmanager
    def file_lock(self):
        """File-based locking to prevent concurrent runs"""
        lock_file = Path(Config.LOCK_FILE)
        
        if lock_file.exists():
            # Check if process is still running
            try:
                with open(lock_file) as f:
                    pid = int(f.read().strip())
                    
                # Check if PID exists (Unix-like systems)
                try:
                    os.kill(pid, 0)
                    raise RuntimeError(f"Another scraper instance is running (PID: {pid})")
                except OSError:
                    # Process doesn't exist, remove stale lock
                    lock_file.unlink()
            except (ValueError, FileNotFoundError):
                lock_file.unlink()
        
        # Create lock file
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            yield
        finally:
            # Remove lock file
            try:
                lock_file.unlink()
            except FileNotFoundError:
                pass
    
    def fetch_webpage_with_retry(self) -> str:
        """Fetch webpage with retry mechanism"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                self.logger.info(f"Fetching webpage (attempt {attempt + 1}/{Config.MAX_RETRIES})")
                
                response = self.session.get(
                    Config.REPLICATE_URL,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                
                self.logger.info(f"Successfully fetched webpage ({len(response.text)} bytes)")
                return response.text
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                self.stats["warnings"] += 1
                
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch webpage after {Config.MAX_RETRIES} attempts")
                    self.stats["errors"] += 1
                    raise
    
    def parse_voice_data(self, html_content: str) -> List[VoiceData]:
        """Parse voice data from HTML API schema (not tables)"""
        voices = []
        
        try:
            # Extract voice enum from API schema since the page is JavaScript-rendered
            voice_enum_pattern = r'"enum":\s*\[(.*?)\]'
            matches = re.findall(voice_enum_pattern, html_content, re.DOTALL)
            
            # Find the voice list (longest enum with voice-like IDs)
            voice_list = None
            max_length = 0
            
            for match in matches:
                try:
                    voices_raw = json.loads('[' + match + ']')
                    if len(voices_raw) > max_length and all(isinstance(v, str) and '_' in v for v in voices_raw):
                        voice_list = voices_raw
                        max_length = len(voices_raw)
                except json.JSONDecodeError:
                    continue
            
            if not voice_list:
                self.logger.error("Could not find voice list in API schema")
                return voices
            
            self.logger.info(f"Found {len(voice_list)} voices in API schema")
            
            # Language and gender mapping based on voice ID prefixes
            voice_mappings = {
                'af_': {'language': 'American English 🇺🇸', 'code': 'en', 'accent': 'american', 'gender': 'female'},
                'am_': {'language': 'American English 🇺🇸', 'code': 'en', 'accent': 'american', 'gender': 'male'},
                'bf_': {'language': 'British English 🇬🇧', 'code': 'en-gb', 'accent': 'british', 'gender': 'female'},
                'bm_': {'language': 'British English 🇬🇧', 'code': 'en-gb', 'accent': 'british', 'gender': 'male'},
                'ff_': {'language': 'French 🇫🇷', 'code': 'fr', 'accent': 'french', 'gender': 'female'},
                'fm_': {'language': 'French 🇫🇷', 'code': 'fr', 'accent': 'french', 'gender': 'male'},
                'hf_': {'language': 'Hindi 🇮🇳', 'code': 'hi', 'accent': 'hindi', 'gender': 'female'},
                'hm_': {'language': 'Hindi 🇮🇳', 'code': 'hi', 'accent': 'hindi', 'gender': 'male'},
                'if_': {'language': 'Italian 🇮🇹', 'code': 'it', 'accent': 'italian', 'gender': 'female'},
                'im_': {'language': 'Italian 🇮🇹', 'code': 'it', 'accent': 'italian', 'gender': 'male'},
                'jf_': {'language': 'Japanese 🇯🇵', 'code': 'ja', 'accent': 'japanese', 'gender': 'female'},
                'jm_': {'language': 'Japanese 🇯🇵', 'code': 'ja', 'accent': 'japanese', 'gender': 'male'},
                'zf_': {'language': 'Mandarin Chinese 🇨🇳', 'code': 'zh', 'accent': 'chinese', 'gender': 'female'},
                'zm_': {'language': 'Mandarin Chinese 🇨🇳', 'code': 'zh', 'accent': 'chinese', 'gender': 'male'},
            }
            
            for voice_id in voice_list:
                try:
                    # Extract prefix
                    prefix = voice_id[:3]
                    
                    if prefix not in voice_mappings:
                        self.logger.warning(f"Unknown voice prefix for {voice_id}")
                        continue
                    
                    mapping = voice_mappings[prefix]
                    
                    # Create VoiceData object with default metadata
                    # Note: For production, you might want to scrape individual voice pages for exact metadata
                    voice = VoiceData(
                        voice_id=voice_id,
                        gender=mapping['gender'],
                        language=mapping['language'],
                        language_code=mapping['code'],
                        accent=mapping['accent'],
                        quality_grade=self.get_default_quality_grade(voice_id),
                        training_duration=self.get_default_training_duration(voice_id),
                        overall_grade=self.get_default_overall_grade(voice_id),
                        hash_id=self.get_placeholder_hash(),
                        special_features=self.get_special_features(voice_id)
                    )
                    
                    voices.append(voice)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing voice {voice_id}: {e}")
                    self.stats["warnings"] += 1
                    continue
            
            self.logger.info(f"Successfully parsed {len(voices)} voices")
            self.stats["voices_found"] = len(voices)
            
        except Exception as e:
            self.logger.error(f"Critical error parsing voice data: {e}")
            self.stats["errors"] += 1
            raise
        
        return voices
    
    def get_default_quality_grade(self, voice_id: str) -> str:
        """Get default quality grade based on voice characteristics"""
        # High-quality voices based on common patterns
        if any(pattern in voice_id for pattern in ['bella', 'emma', 'alpha', 'nova', 'echo']):
            return 'A'
        elif voice_id.startswith(('af_', 'am_', 'bf_', 'bm_')):
            return 'B'  # English voices generally higher quality
        else:
            return 'C'  # Other languages
    
    def get_default_training_duration(self, voice_id: str) -> str:
        """Get default training duration estimate"""
        # American/British English typically have more data
        if voice_id.startswith(('af_', 'am_', 'bf_', 'bm_')):
            if voice_id in ['af_bella', 'af_nova', 'am_michael', 'bf_emma']:
                return 'HH hours'  # High-quality voices
            else:
                return 'H hours'
        else:
            return 'MM minutes'  # Other languages typically less data
    
    def get_default_overall_grade(self, voice_id: str) -> str:
        """Get default overall grade"""
        quality = self.get_default_quality_grade(voice_id)
        if quality == 'A':
            return 'A-'
        elif quality == 'B':
            return 'B-'
        else:
            return 'C+'
    
    def get_placeholder_hash(self) -> str:
        """Generate a placeholder hash"""
        import hashlib
        import time
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    def get_special_features(self, voice_id: str) -> str:
        """Get special features for voice"""
        # High-quality voices get special features
        if voice_id in ['af_bella', 'bf_emma', 'af_nova']:
            return '🔥'
        elif voice_id in ['af_nicole', 'af_aoede']:
            return '🎧'
        else:
            return None
    
    def extract_voices_for_language(self, html_content: str, lang_display: str, lang_info: Dict) -> List[VoiceData]:
        """Extract voices for a specific language section"""
        voices = []
        
        try:
            # Find the section for this language - use simpler pattern
            section_pattern = f"### {re.escape(lang_display)}"
            section_start = html_content.find(section_pattern)
            
            if section_start == -1:
                # Try without the flag emoji (fallback)
                lang_name = lang_display.split(' ')[0] + ' ' + lang_display.split(' ')[1]
                section_pattern = f"### {re.escape(lang_name)}"
                section_start = html_content.find(section_pattern)
                
                if section_start == -1:
                    self.logger.warning(f"No section found for language: {lang_display}")
                    return voices
            
            # Find the end of this section (next ### or end of document)
            next_section_start = html_content.find("###", section_start + len(section_pattern))
            if next_section_start == -1:
                section_content = html_content[section_start:]
            else:
                section_content = html_content[section_start:next_section_start]
            
            # Extract voice table entries from this section
            # Look for table patterns more carefully
            lines = section_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('|'):
                    continue
                
                # Parse table row: | voice_id | gender+special | grade | duration | overall | hash | [optional] |
                parts = [part.strip() for part in line.split('|')]
                if len(parts) < 7:  # Need at least 7 parts for a valid row
                    continue
                
                # Skip header rows
                if parts[1] == '' or 'voice' in parts[1].lower() or parts[1] == '--':
                    continue
                
                try:
                    voice_id = parts[1]
                    gender_info = parts[2]  # Contains gender symbol and special features
                    quality = parts[3]
                    duration = parts[4]
                    overall = parts[5]
                    hash_id = parts[6]
                    note = parts[7] if len(parts) > 7 else ""
                    
                    # Validate voice_id pattern (language_gender_name)
                    if not re.match(r'^[a-z]{2}_[a-z]+$', voice_id):
                        continue
                    
                    # Extract gender and special features
                    gender_symbol = "🚺" if "🚺" in gender_info else ("🚹" if "🚹" in gender_info else "")
                    if not gender_symbol:
                        continue
                        
                    special_features = ""
                    if "🔥" in gender_info:
                        special_features += "🔥"
                    if "🎧" in gender_info:
                        special_features += "🎧"
                    
                    # Validate quality grade
                    if not re.match(r'^[A-D]$', quality):
                        continue
                    
                    # Validate hash
                    if not re.match(r'^[a-f0-9]{8}$', hash_id):
                        continue
                    
                    # Clean up note
                    note = note.strip() if note and note.strip() else None
                    
                    voice = VoiceData(
                        voice_id=voice_id,
                        gender="female" if gender_symbol == "🚺" else "male",
                        language=lang_display,
                        language_code=lang_info["code"],
                        accent=lang_info["accent"],
                        quality_grade=quality,
                        training_duration=duration.strip(),
                        overall_grade=overall,
                        hash_id=hash_id,
                        special_features=special_features if special_features else note
                    )
                    
                    voices.append(voice)
                    self.logger.debug(f"Parsed voice: {voice_id} from {lang_display}")
                    
                except (IndexError, ValueError) as e:
                    self.logger.debug(f"Skipping invalid table row: {line[:50]}...")
                    continue
                except Exception as e:
                    self.logger.warning(f"Error parsing voice entry: {e}")
                    self.stats["warnings"] += 1
                    continue
            
            self.logger.info(f"Extracted {len(voices)} voices from {lang_display}")
            
        except Exception as e:
            self.logger.error(f"Error extracting voices for {lang_display}: {e}")
            self.stats["errors"] += 1
        
        return voices
    
    def save_backup(self, voices: List[VoiceData]):
        """Save backup of scraped data"""
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "voices": [asdict(voice) for voice in voices],
                "stats": {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in self.stats.items()}
            }
            
            with open(Config.BACKUP_FILE, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Backup saved to {Config.BACKUP_FILE}")
            
        except Exception as e:
            self.logger.error(f"Failed to save backup: {e}")
            self.stats["errors"] += 1
    
    def update_database(self, voices: List[VoiceData]):
        """Update database with error handling and fallback"""
        if self.dry_run:
            self.logger.info("DRY RUN: Would update database with voices")
            for voice in voices:
                self.logger.info(f"  Would add/update: {voice.voice_id}")
            return
        
        if DB_AVAILABLE:
            try:
                self.update_main_database(voices)
            except Exception as e:
                self.logger.error(f"Main database update failed: {e}")
                self.stats["errors"] += 1
                self.update_fallback_database(voices)
        else:
            self.logger.warning("Main database not available, using fallback")
            self.update_fallback_database(voices)
    
    def update_main_database(self, voices: List[VoiceData]):
        """Update main PostgreSQL database"""
        with next(get_session()) as session:
            for voice in voices:
                try:
                    # Check if voice exists
                    existing_voice = session.exec(
                        select(SelectAIVoices).where(SelectAIVoices.voice_id == voice.voice_id)
                    ).first()
                    
                    if existing_voice:
                        if self.update_existing:
                            # Update existing voice
                            voice_data = voice.to_db_dict()
                            for key, value in voice_data.items():
                                if hasattr(existing_voice, key):
                                    setattr(existing_voice, key, value)
                            
                            existing_voice.updated_at = datetime.now()
                            self.stats["voices_updated"] += 1
                            self.logger.info(f"Updated voice: {voice.voice_id}")
                        else:
                            self.logger.info(f"Skipped existing voice: {voice.voice_id}")
                    else:
                        # Add new voice
                        new_voice = SelectAIVoices(**voice.to_db_dict())
                        session.add(new_voice)
                        self.stats["voices_added"] += 1
                        self.logger.info(f"Added new voice: {voice.voice_id}")
                
                except Exception as e:
                    self.logger.error(f"Error processing voice {voice.voice_id}: {e}")
                    self.stats["errors"] += 1
                    continue
            
            session.commit()
            self.logger.info("Database transaction committed successfully")
    
    def update_fallback_database(self, voices: List[VoiceData]):
        """Update SQLite fallback database"""
        try:
            conn = sqlite3.connect(Config.FALLBACK_DB)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kokoro_voices (
                    voice_id TEXT PRIMARY KEY,
                    voice_data TEXT,
                    timestamp TEXT
                )
            ''')
            
            for voice in voices:
                voice_json = json.dumps(asdict(voice))
                cursor.execute('''
                    INSERT OR REPLACE INTO kokoro_voices 
                    (voice_id, voice_data, timestamp) 
                    VALUES (?, ?, ?)
                ''', (voice.voice_id, voice_json, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Updated fallback database with {len(voices)} voices")
            
        except Exception as e:
            self.logger.error(f"Fallback database update failed: {e}")
            self.stats["errors"] += 1
    
    def generate_report(self):
        """Generate execution report"""
        end_time = datetime.now()
        duration = end_time - self.stats["start_time"]
        
        report = f"""
=== Kokoro Voice Scraper Report ===
Start Time: {self.stats["start_time"]}
End Time: {end_time}
Duration: {duration}
Voices Found: {self.stats["voices_found"]}
Voices Added: {self.stats["voices_added"]}
Voices Updated: {self.stats["voices_updated"]}
Errors: {self.stats["errors"]}
Warnings: {self.stats["warnings"]}
Status: {'SUCCESS' if self.stats["errors"] == 0 else 'COMPLETED WITH ERRORS'}
=====================================
"""
        
        self.logger.info(report)
        return report
    
    def run(self) -> bool:
        """Main execution method"""
        try:
            with self.file_lock():
                self.logger.info("Starting Kokoro voice scraper")
                
                # Fetch webpage
                html_content = self.fetch_webpage_with_retry()
                
                # Parse voices
                voices = self.parse_voice_data(html_content)
                
                if not voices:
                    self.logger.warning("No voices found in webpage")
                    return False
                
                # Save backup
                self.save_backup(voices)
                
                # Update database
                self.update_database(voices)
                
                # Generate report
                self.generate_report()
                
                return self.stats["errors"] == 0
                
        except Exception as e:
            self.logger.error(f"Critical error in main execution: {e}")
            self.stats["errors"] += 1
            return False

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="Kokoro Voices Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making changes")
    parser.add_argument("--update-existing", action="store_true", help="Update existing voice entries")
    parser.add_argument("--languages", help="Comma-separated language codes to scrape (e.g., en,ja)")
    
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = KokoroVoiceScraper(
        dry_run=args.dry_run,
        update_existing=args.update_existing
    )
    
    # Run scraper
    success = scraper.run()
    
    # Exit with appropriate code for cron job monitoring
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

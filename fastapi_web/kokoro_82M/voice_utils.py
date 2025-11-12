"""
Kokoro Voice Generation Utilities

Helper functions for voice processing, validation, and file management.

Author: Auto Video Generator Team
Date: 2025-11-11
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import re


class VoiceValidator:
    """Utility class for validating voice inputs and configurations."""
    
    @staticmethod
    def validate_text(
        text: str,
        min_length: int = 1,
        max_length: int = 5000,
        logger: Optional[logging.Logger] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate text input for voice generation.
        
        Args:
            text (str): Text to validate
            min_length (int): Minimum text length
            max_length (int): Maximum text length
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(text, str):
            error = f"Text must be a string, got {type(text).__name__}"
            if logger:
                logger.error(error)
            return False, error
        
        text = text.strip()
        
        if len(text) < min_length:
            error = f"Text is too short (minimum {min_length} characters)"
            if logger:
                logger.warning(error)
            return False, error
        
        if len(text) > max_length:
            error = f"Text is too long (maximum {max_length} characters)"
            if logger:
                logger.warning(error)
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_speed(
        speed: float,
        min_speed: float = 0.5,
        max_speed: float = 2.0,
        logger: Optional[logging.Logger] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate speech speed parameter.
        
        Args:
            speed (float): Speed multiplier
            min_speed (float): Minimum allowed speed
            max_speed (float): Maximum allowed speed
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(speed, (int, float)):
            error = f"Speed must be a number, got {type(speed).__name__}"
            if logger:
                logger.error(error)
            return False, error
        
        if speed < min_speed or speed > max_speed:
            error = f"Speed must be between {min_speed} and {max_speed}, got {speed}"
            if logger:
                logger.warning(error)
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_filename(
        filename: str,
        logger: Optional[logging.Logger] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate filename for safety.
        
        Args:
            filename (str): Filename to validate
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            error = "Filename cannot be empty"
            if logger:
                logger.error(error)
            return False, error
        
        # Remove .wav extension if present
        name = filename.replace('.wav', '')
        
        # Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(invalid_chars, name):
            error = f"Filename contains invalid characters: {name}"
            if logger:
                logger.error(error)
            return False, error
        
        if len(name) > 255:
            error = "Filename is too long (max 255 characters)"
            if logger:
                logger.error(error)
            return False, error
        
        return True, None


class AudioMetadataManager:
    """Manage audio file metadata operations."""
    
    @staticmethod
    def save_metadata(
        metadata: Dict[str, Any],
        filepath: Path,
        logger: Optional[logging.Logger] = None
    ) -> bool:
        """
        Save metadata to JSON file.
        
        Args:
            metadata (Dict): Metadata to save
            filepath (Path): Path for metadata file
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            bool: True if successful
        """
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            if logger:
                logger.info(f"Metadata saved: {filepath}")
            return True
        
        except Exception as e:
            if logger:
                logger.error(f"Failed to save metadata: {str(e)}")
            return False
    
    @staticmethod
    def load_metadata(
        filepath: Path,
        logger: Optional[logging.Logger] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load metadata from JSON file.
        
        Args:
            filepath (Path): Path to metadata file
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Dict or None if file not found/invalid
        """
        if not filepath.exists():
            if logger:
                logger.warning(f"Metadata file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if logger:
                logger.debug(f"Metadata loaded: {filepath}")
            return metadata
        
        except Exception as e:
            if logger:
                logger.error(f"Failed to load metadata: {str(e)}")
            return None
    
    @staticmethod
    def merge_metadata(
        *metadata_dicts: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> Dict[str, Any]:
        """
        Merge multiple metadata dictionaries.
        
        Args:
            *metadata_dicts: Variable number of metadata dictionaries
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Dict: Merged metadata
        """
        merged = {}
        
        for meta in metadata_dicts:
            if isinstance(meta, dict):
                merged.update(meta)
        
        if logger:
            logger.debug(f"Merged {len(metadata_dicts)} metadata dictionaries")
        
        return merged


class FileOrganizer:
    """Organize and manage voice files."""
    
    @staticmethod
    def organize_by_date(
        source_dir: Path,
        target_base_dir: Path,
        logger: Optional[logging.Logger] = None
    ) -> Dict[str, List[Path]]:
        """
        Organize voice files into date-based subdirectories.
        
        Args:
            source_dir (Path): Source directory with voice files
            target_base_dir (Path): Base target directory
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Dict: Mapping of dates to organized files
        """
        organized = {}
        
        if not source_dir.exists():
            return organized
        
        for wav_file in source_dir.glob("*.wav"):
            try:
                # Extract date from filename (YYYY-MM-DD format expected)
                filename = wav_file.stem
                date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    date_dir = target_base_dir / date_str
                    date_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Move metadata too if exists
                    metadata_file = source_dir / f"{filename}_metadata.json"
                    
                    # Track organized files
                    if date_str not in organized:
                        organized[date_str] = []
                    organized[date_str].append(wav_file)
                    
                    if logger:
                        logger.debug(f"Organized: {wav_file.name} -> {date_str}")
            
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to organize {wav_file.name}: {str(e)}")
                continue
        
        if logger:
            logger.info(f"Organized {sum(len(v) for v in organized.values())} files into {len(organized)} date groups")
        
        return organized
    
    @staticmethod
    def organize_by_voice(
        source_dir: Path,
        target_base_dir: Path,
        logger: Optional[logging.Logger] = None
    ) -> Dict[str, List[Path]]:
        """
        Organize voice files by voice type.
        
        Args:
            source_dir (Path): Source directory with voice files
            target_base_dir (Path): Base target directory
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Dict: Mapping of voice types to files
        """
        organized = {}
        
        if not source_dir.exists():
            return organized
        
        for wav_file in source_dir.glob("*.wav"):
            try:
                metadata_file = source_dir / f"{wav_file.stem}_metadata.json"
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    voice_type = metadata.get('voice_type', 'unknown')
                    voice_dir = target_base_dir / voice_type
                    voice_dir.mkdir(parents=True, exist_ok=True)
                    
                    if voice_type not in organized:
                        organized[voice_type] = []
                    organized[voice_type].append(wav_file)
                    
                    if logger:
                        logger.debug(f"Organized: {wav_file.name} -> {voice_type}")
            
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to organize {wav_file.name}: {str(e)}")
                continue
        
        if logger:
            logger.info(f"Organized {sum(len(v) for v in organized.values())} files into {len(organized)} voice groups")
        
        return organized
    
    @staticmethod
    def cleanup_old_files(
        directory: Path,
        days_old: int = 30,
        dry_run: bool = True,
        logger: Optional[logging.Logger] = None
    ) -> List[Path]:
        """
        Find and optionally delete files older than specified days.
        
        Args:
            directory (Path): Directory to clean
            days_old (int): Age threshold in days
            dry_run (bool): If True, only report files without deleting
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            List: Paths of files that would be/were deleted
        """
        from datetime import datetime, timedelta
        
        deleted_files = []
        threshold_date = datetime.now() - timedelta(days=days_old)
        
        if not directory.exists():
            return deleted_files
        
        for wav_file in directory.glob("*.wav"):
            try:
                file_date = datetime.fromtimestamp(wav_file.stat().st_mtime)
                
                if file_date < threshold_date:
                    deleted_files.append(wav_file)
                    
                    if not dry_run:
                        wav_file.unlink()
                        
                        # Also delete metadata
                        metadata_file = directory / f"{wav_file.stem}_metadata.json"
                        if metadata_file.exists():
                            metadata_file.unlink()
                        
                        if logger:
                            logger.info(f"Deleted: {wav_file.name}")
                    else:
                        if logger:
                            logger.debug(f"Would delete: {wav_file.name} (from {file_date})")
            
            except Exception as e:
                if logger:
                    logger.warning(f"Error processing {wav_file.name}: {str(e)}")
                continue
        
        if logger:
            mode = "Would delete" if dry_run else "Deleted"
            logger.info(f"{mode} {len(deleted_files)} files older than {days_old} days")
        
        return deleted_files


class VoiceStatistics:
    """Generate statistics about generated voices."""
    
    @staticmethod
    def analyze_directory(
        directory: Path,
        logger: Optional[logging.Logger] = None
    ) -> Dict[str, Any]:
        """
        Analyze a directory of voice files.
        
        Args:
            directory (Path): Directory to analyze
            logger (logging.Logger, optional): Logger instance
        
        Returns:
            Dict: Statistics about the directory
        """
        stats = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "by_voice_type": {},
            "by_date": {},
            "average_duration": 0.0,
            "total_duration": 0.0,
        }
        
        if not directory.exists():
            return stats
        
        total_duration = 0.0
        duration_count = 0
        
        for wav_file in directory.glob("*.wav"):
            stats["total_files"] += 1
            stats["total_size_mb"] += wav_file.stat().st_size / (1024 * 1024)
            
            # Extract date
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', wav_file.stem)
            if date_match:
                date = date_match.group(1)
                stats["by_date"][date] = stats["by_date"].get(date, 0) + 1
            
            # Extract voice type and duration from metadata
            metadata_file = directory / f"{wav_file.stem}_metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    voice_type = metadata.get('voice_type', 'unknown')
                    stats["by_voice_type"][voice_type] = stats["by_voice_type"].get(voice_type, 0) + 1
                    
                    duration = metadata.get('duration_seconds', 0)
                    total_duration += duration
                    duration_count += 1
                
                except Exception as e:
                    if logger:
                        logger.warning(f"Could not read metadata for {wav_file.name}: {str(e)}")
        
        if duration_count > 0:
            stats["average_duration"] = total_duration / duration_count
            stats["total_duration"] = total_duration
        
        if logger:
            logger.info(f"Analysis complete: {stats['total_files']} files, {stats['total_size_mb']:.2f} MB")
        
        return stats
    
    @staticmethod
    def format_statistics(stats: Dict[str, Any]) -> str:
        """
        Format statistics for display.
        
        Args:
            stats (Dict): Statistics dictionary
        
        Returns:
            str: Formatted statistics string
        """
        lines = [
            "📊 Voice Generation Statistics",
            "=" * 40,
            f"Total Files: {stats['total_files']}",
            f"Total Size: {stats['total_size_mb']:.2f} MB",
            f"Total Duration: {stats['total_duration']:.2f} seconds",
            f"Average Duration: {stats['average_duration']:.2f} seconds",
            "",
            "By Voice Type:",
        ]
        
        for voice_type, count in sorted(stats['by_voice_type'].items()):
            lines.append(f"  {voice_type}: {count} files")
        
        lines.append("")
        lines.append("By Date:")
        
        for date, count in sorted(stats['by_date'].items()):
            lines.append(f"  {date}: {count} files")
        
        return "\n".join(lines)


# Convenience functions

def validate_input(
    text: str,
    speed: float = 1.0,
    logger: Optional[logging.Logger] = None
) -> tuple[bool, Optional[str]]:
    """Quick validation of text and speed."""
    text_valid, text_error = VoiceValidator.validate_text(text, logger=logger)
    if not text_valid:
        return False, text_error
    
    speed_valid, speed_error = VoiceValidator.validate_speed(speed, logger=logger)
    if not speed_valid:
        return False, speed_error
    
    return True, None


def get_directory_stats(
    directory: str,
    logger: Optional[logging.Logger] = None
) -> str:
    """Get formatted statistics for a directory."""
    stats = VoiceStatistics.analyze_directory(Path(directory), logger)
    return VoiceStatistics.format_statistics(stats)


if __name__ == "__main__":
    # Example usage
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Test validator
    is_valid, error = validate_input("Hello world", 1.0, logger)
    print(f"Validation: {is_valid}, Error: {error}")
    
    # Test statistics
    stats = VoiceStatistics.analyze_directory(Path("media/voiceover/user"), logger)
    print(VoiceStatistics.format_statistics(stats))

from pathlib import Path
from typing import List, Union, Optional
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

from moviepy import ImageClip

import os

BASE_DIR = Path(__file__).resolve().parent.parent

class FileDirectory:
    """Utility class for handling file operations and media file management."""
    
    def __init__(self):
        self.supported_image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
        self.supported_audio_extensions = {'.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg', '.wma'}
        self.supported_video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    
    def get_image_files(self, directory_path: Union[str, Path], load_clips: bool = True) -> List:
        """
        Get image files from directory and optionally load them as MoviePy clips.
        
        Args:
            directory_path: Path to directory containing images
            load_clips: If True, returns ImageFileClip objects, else returns file paths
            
        Returns:
            List of ImageFileClip objects or file paths
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            print(f"Directory does not exist: {directory_path}")
            return []
        
        image_files = []
        
        # Get all image files from directory
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_image_extensions:
                if load_clips:
                    try:
                        # from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
                        clip = ImageClip(img=str(file_path))
                        image_files.append(clip)
                    except Exception as e:
                        print(f"Error loading image {file_path}: {e}")
                        continue
                else:
                    image_files.append(str(file_path))
        
        print(f"Found {len(image_files)} image files in {directory_path}")
        return image_files
    
    def get_audio_files(self, directory_path: Union[str, Path], load_clips: bool = True) -> List:
        """
        Get audio files from directory and optionally load them as MoviePy clips.
        
        Args:
            directory_path: Path to directory containing audio files
            load_clips: If True, returns AudioFileClip objects, else returns file paths
            
        Returns:
            List of AudioFileClip objects or file paths
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            print(f"Directory does not exist: {directory_path}")
            return []
        
        audio_files = []
        
        # Get all audio files from directory
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_audio_extensions:
                if load_clips:
                    try:
                        clip = AudioFileClip(str(file_path))
                        audio_files.append(clip)
                    except Exception as e:
                        print(f"Error loading audio {file_path}: {e}")
                        continue
                else:
                    audio_files.append(str(file_path))
        
        print(f"Found {len(audio_files)} audio files in {directory_path}")
        return audio_files
    
    def get_video_files(self, directory_path: Union[str, Path], load_clips: bool = True, file_name: Optional[str] = None) -> List:
        """
        Get video files from directory and optionally load them as MoviePy clips.
        
        Args:
            directory_path: Path to directory containing video files
            load_clips: If True, returns VideoFileClip objects, else returns file paths
            file_name: If provided, only return file(s) matching this name
            
        Returns:
            List of VideoFileClip objects or file paths
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            print(f"Directory does not exist: {directory_path}")
            return []
        
        video_files = []
        
        # Get all video files from directory
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_video_extensions:
                if file_name and file_path.name != file_name:
                    continue
                if load_clips:
                    try:
                        clip = VideoFileClip(str(file_path))
                        video_files.append(clip)
                    except Exception as e:
                        print(f"Error loading video {file_path}: {e}")
                        continue
                else:
                    video_files.append(str(file_path))
        
        print(f"Found {len(video_files)} video files in {directory_path}" + (f" matching '{file_name}'" if file_name else ""))
        return video_files
    
    def get_all_files(self, directory_path: Union[str, Path], extensions: Optional[List[str]] = None) -> List[str]:
        """
        Get all files from directory with optional extension filtering.
        
        Args:
            directory_path: Path to directory
            extensions: List of extensions to filter by (e.g., ['.jpg', '.png'])
            
        Returns:
            List of file paths as strings
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            print(f"Directory does not exist: {directory_path}")
            return []
        
        files = []
        
        for file_path in directory_path.iterdir():
            if file_path.is_file():
                if extensions:
                    if file_path.suffix.lower() in [ext.lower() for ext in extensions]:
                        files.append(str(file_path))
                else:
                    files.append(str(file_path))
        
        return files
    
    def create_directory(self, directory_path: Union[str, Path]) -> list:
        """
        Create directory if it doesn't exist.
        
        Args:
            directory_path: Path to directory to create
            
        Returns:
            True if directory was created or already exists, False on error
        """
        try:
            directory_path = Path(directory_path)
            directory_path.mkdir(parents=True, exist_ok=True)
            return [str(directory_path)]
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return []

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except Exception:
            return 0
    
    def get_directory_size(self, directory_path: Union[str, Path]) -> int:
        """Get total size of all files in directory."""
        directory_path = Path(directory_path)
        total_size = 0
        
        if directory_path.exists():
            for file_path in directory_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        return total_size
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename by removing invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def get_unique_filename(self, directory_path: Union[str, Path], filename: str) -> str:
        """Get unique filename by adding number suffix if file exists."""
        directory_path = Path(directory_path)
        file_path = directory_path / filename
        
        if not file_path.exists():
            return filename
        
        name_part = file_path.stem
        extension = file_path.suffix
        counter = 1
        
        while True:
            new_filename = f"{name_part}_{counter}{extension}"
            new_file_path = directory_path / new_filename
            if not new_file_path.exists():
                return new_filename
            counter += 1
    
    def get_secret_token(self, token_path: Union[str, Path]) -> Optional[str]:
        """
        Get secret token from file.
        
        Args:
            token_path: Path to token file
            
        Returns:
            Token string if found, None otherwise
        """
        token_path = Path(token_path)
        
        if not token_path.exists():
            print(f"Token file does not exist: {token_path}")
            return None
            
        try:
            with open(token_path, 'r') as f:
                token = f.read().strip()
                if not token:
                    print(f"Token file is empty: {token_path}")
                    return None
                return token
        except Exception as e:
            print(f"Error reading token file {token_path}: {e}")
            return None


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_media_directory(directory_path: Union[str, Path], media_type: str = "image") -> dict:
    """
    Validate media directory and return status information.
    
    Args:
        directory_path: Path to media directory
        media_type: Type of media ('image', 'audio', 'video')
        
    Returns:
        Dictionary with validation results
    """
    directory_path = Path(directory_path)
    file_directory = FileDirectory()
    
    result = {
        'exists': directory_path.exists(),
        'is_directory': directory_path.is_dir() if directory_path.exists() else False,
        'file_count': 0,
        'total_size': 0,
        'files': []
    }
    
    if result['exists'] and result['is_directory']:
        if media_type == "image":
            result['files'] = file_directory.get_all_files(directory_path, list(file_directory.supported_image_extensions))
        elif media_type == "audio":
            result['files'] = file_directory.get_all_files(directory_path, list(file_directory.supported_audio_extensions))
        elif media_type == "video":
            result['files'] = file_directory.get_all_files(directory_path, list(file_directory.supported_video_extensions))
        else:
            result['files'] = file_directory.get_all_files(directory_path)
        
        result['file_count'] = len(result['files'])
        result['total_size'] = file_directory.get_directory_size(directory_path)
    
    return result


def calculate_video_timing(
    audio_path,
    image_count,
    preferred_fps=24,
    min_fps=10,
    max_fps=60,
    auto_adjust_fps=True,
    transition_duration=0
):
    """
    Calculate image view duration and fps based on audio length and image count.

    :param audio_path: Path to audio file
    :param image_count: Total number of images
    :param preferred_fps: Default FPS if auto adjust is disabled
    :param min_fps: Minimum fps allowed
    :param max_fps: Maximum fps allowed
    :param auto_adjust_fps: Whether to calculate fps based on audio length
    :param transition_duration: Optional crossfade time in seconds
    :return: (image_duration, fps, total_duration)
    """

    audio_clip = AudioFileClip(str(audio_path))
    audio_duration = audio_clip.duration

    if image_count <= 0:
        raise ValueError("Image count must be greater than 0.")

    # Total duration to be split across images (with transitions considered)
    total_transitions = (image_count - 1) * transition_duration
    total_image_time = audio_duration + total_transitions
    image_duration = total_image_time / image_count

    if auto_adjust_fps:
        total_frames = int(audio_duration * preferred_fps)
        fps = total_frames / audio_duration
        fps = max(min(fps, max_fps), min_fps)  # Clamp fps between min and max
    else:
        fps = preferred_fps

    return round(image_duration, 2), round(fps, 2), round(audio_duration, 2)


# 🧪 Example usage
# if __name__ == "__main__":
#     audio_file = Path("media/audio/my_voice.mp3")
#     num_images = 10

#     duration_per_image, fps, audio_len = calculate_video_timing(
#         audio_path=audio_file,
#         image_count=num_images,
#         preferred_fps=25,
#         transition_duration=1.0,
#         auto_adjust_fps=True
#     )

#     print(f"Audio Duration: {audio_len}s")
#     print(f"Image Duration: {duration_per_image}s")
#     print(f"Adjusted FPS: {fps}")

from moviepy import ImageClip, VideoFileClip, concatenate_videoclips
import os

class TransitionBase:
    def __init__(self, sources, duration=2, size=(720, 720)):
        """
        sources: list of file paths (images or videos)
        duration: duration of each transition (used for images, not videos)
        size: resize target (width, height)
        """
        self.sources = sources
        self.duration = duration
        self.size = size
        self.clips = [self._load_clip(path) for path in sources]

    def _load_clip(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
            return ImageClip(path).resized(self.size).with_duration(self.duration)
        elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
            return VideoFileClip(path).resized(self.size)
        else:
            raise ValueError(f"Unsupported file format: {path}")

    def build_transition(self, clip1, clip2):
        """Override in subclasses with effect logic"""
        raise NotImplementedError

    def build(self):
        """Apply transition between each pair of clips"""
        results = []
        for i in range(len(self.clips) - 1):
            results.append(self.build_transition(self.clips[i], self.clips[i+1]))
        return concatenate_videoclips(results, method="compose")

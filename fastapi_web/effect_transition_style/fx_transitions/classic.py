import cv2
from .base import TransitionBase
from moviepy import *
from moviepy.video import fx as vfx

class Fade(TransitionBase):
    
    def __init__(self, sources, duration=1, size=(640, 480)):
        self.sources = sources
        self.duration = duration
        self.size = size
        self.clips = []
        for src in sources:
            if src.lower().endswith((".jpg", ".jpeg", ".png")):
                clip = ImageClip(src).with_duration(duration).resized(size)
            else:
                clip = VideoFileClip(src).subclipped(0, min(duration, VideoFileClip(src).with_duration)).resized(size)
            self.clips.append(clip)

    def build(self):
        clip1 = vfx.FadeOut(self.clips[0].with_duration(self.duration), self.duration)
        clip2 = vfx.FadeIn(self.clips[1].with_duration(self.duration), self.duration)
        return concatenate_videoclips([clip1, clip2], method="compose")
        
class Slide(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.with_frame(min(t, clip1.with_duration-0.01))
            frame2 = clip2.with_frame(min(t, clip2.with_duration-0.01))
            width = self.size[0]
            x_offset = int(width * progress)
            frame = frame1.copy()
            frame[:, x_offset:] = frame2[:, :width-x_offset]
            return frame
        return VideoClip(make_frame, duration=self.duration)

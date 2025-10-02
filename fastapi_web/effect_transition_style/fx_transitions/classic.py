import cv2
from moviepy import VideoClip
from .base import TransitionBase

class Fade(TransitionBase):
    def build_transition(self, clip1, clip2):
        return clip1.crossfadeout(self.duration).set_end(self.duration).crossfadein(self.duration).set_duration(self.duration)

class Slide(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            width = self.size[0]
            x_offset = int(width * progress)
            frame = frame1.copy()
            frame[:, x_offset:] = frame2[:, :width-x_offset]
            return frame
        return VideoClip(make_frame, duration=self.duration)

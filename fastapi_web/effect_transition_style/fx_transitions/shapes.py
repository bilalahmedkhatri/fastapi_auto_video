import numpy as np
from moviepy import VideoClip
from .base import TransitionBase

class CircleWipe(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01)).copy()
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            cx, cy = self.size[0]//2, self.size[1]//2
            r = int(progress * (self.size[0]//1.2))
            y, x = np.ogrid[:self.size[1], :self.size[0]]
            mask = (x - cx)**2 + (y - cy)**2 <= r**2
            frame1[mask] = frame2[mask]
            return frame1
        return VideoClip(make_frame, duration=self.duration)

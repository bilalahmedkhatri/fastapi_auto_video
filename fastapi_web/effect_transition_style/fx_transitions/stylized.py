from moviepy import VideoClip
from .base import TransitionBase
import numpy as np
import cv2

class Flash(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            frame = cv2.addWeighted(frame1, 1-progress, frame2, progress, 0)

            brightness = int(255 * abs(np.sin(progress * np.pi)))
            overlay = np.full_like(frame, brightness)
            return cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        return VideoClip(make_frame, duration=self.duration)

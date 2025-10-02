from moviepy import VideoClip
from .base import TransitionBase
import cv2

class Zoom(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            scale = 1 + 0.5*progress
            frame1 = clip1.resize(scale).get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))

            h, w = self.size[1], self.size[0]
            y, x = frame1.shape[0]//2 - h//2, frame1.shape[1]//2 - w//2
            frame1 = frame1[y:y+h, x:x+w]

            return cv2.addWeighted(frame1, 1-progress, frame2, progress, 0)
        return VideoClip(make_frame, duration=self.duration)

class Spin(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.rotate(progress*360).get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            return cv2.addWeighted(frame1, 1-progress, frame2, progress, 0)
        return VideoClip(make_frame, duration=self.duration)

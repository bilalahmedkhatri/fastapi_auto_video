import numpy as np, cv2, random
from moviepy import VideoClip
from .base import TransitionBase

class Pixelate(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            pixels = int(20*(1-progress)+1)
            small = cv2.resize(frame1, (pixels, pixels))
            pixel_frame = cv2.resize(small, self.size, interpolation=cv2.INTER_NEAREST)
            return cv2.addWeighted(pixel_frame, 1-progress, frame2, progress, 0)
        return VideoClip(make_frame, duration=self.duration)

class Glitch(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            frame = cv2.addWeighted(frame1, 1-(t/self.duration), frame2, t/self.duration, 0)
            if random.random() < 0.3:
                shift = random.randint(-20, 20)
                frame[:, :, 0] = np.roll(frame[:, :, 0], shift, axis=1)
            return frame
        return VideoClip(make_frame, duration=self.duration)

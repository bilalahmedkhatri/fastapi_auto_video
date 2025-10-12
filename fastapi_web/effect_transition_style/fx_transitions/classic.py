import cv2
from .base import TransitionBase
from moviepy import *
from moviepy.video import fx as vfx

class Fade(TransitionBase):
    
    def build_transition(self, clip1, clip2):
        # Create fade out on first clip
        clip1_fadeout = clip1.with_duration(self.duration).with_effects([vfx.FadeOut(self.duration)])
        # Create fade in on second clip  
        clip2_fadein = clip2.with_duration(self.duration).with_effects([vfx.FadeIn(self.duration)])
        return concatenate_videoclips([clip1_fadeout, clip2_fadein], method="compose")
        
class Slide(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            frame1 = clip1.get_frame(min(t, clip1.duration-0.01)).copy()
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            width = self.size[0]
            x_offset = int(width * progress)
            frame1[:, x_offset:] = frame2[:, :width-x_offset]
            return frame1
        return VideoClip(make_frame, duration=self.duration)

from moviepy import CompositeVideoClip
from .base import TransitionBase

class SplitScreen(TransitionBase):
    def build_transition(self, clip1, clip2):
        left = clip1.crop(x1=0, x2=self.size[0]//2)
        right = clip2.crop(x1=self.size[0]//2, x2=self.size[0])
        return CompositeVideoClip([
            left.with_pos(("left","center")),
            right.with_pos(("right","center"))
        ]).with_duration(self.duration)

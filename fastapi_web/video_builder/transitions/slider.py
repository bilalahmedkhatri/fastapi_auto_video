from moviepy import CompositeVideoClip, VideoClip

class SliderTransition:
    """
    Slide transition effect for MoviePy clips.
    Supports directions: left, right, up, down.
    """
    def __init__(self, direction='left'):
        assert direction in ('left', 'right', 'up', 'down'), "Direction must be left/right/up/down"
        self.direction = direction

    def apply(self, clip1, clip2, duration, size):
        """
        Returns a CompositeVideoClip that slides clip1 out and clip2 in.
        Args:
            clip1: outgoing VideoClip
            clip2: incoming VideoClip
            duration: transition duration (seconds)
            size: (width, height) tuple
        """
        w, h = size
        # Animate positions
        if self.direction == 'left':
            pos1 = lambda t: (int(-w * t / duration), 0)
            pos2 = lambda t: (int(w - w * t / duration), 0)
        elif self.direction == 'right':
            pos1 = lambda t: (int(w * t / duration), 0)
            pos2 = lambda t: (int(-w + w * t / duration), 0)
        elif self.direction == 'up':
            pos1 = lambda t: (0, int(-h * t / duration))
            pos2 = lambda t: (0, int(h - h * t / duration))
        elif self.direction == 'down':
            pos1 = lambda t: (0, int(h * t / duration))
            pos2 = lambda t: (0, int(-h + h * t / duration))
        # Set positions for transition
        moving1 = clip1.set_start(0).set_duration(duration).set_position(pos1)
        moving2 = clip2.set_start(0).set_duration(duration).set_position(pos2)
        # Composite for transition duration
        transition = CompositeVideoClip([moving1, moving2], size=size).set_duration(duration)
        return transition

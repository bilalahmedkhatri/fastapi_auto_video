from .classic import Fade, Slide
from .motion import Zoom, Spin
from .stylized import Flash
from .shapes import CircleWipe
from .abstract import Pixelate, Glitch
from .multilayer import SplitScreen

class TransitionFactory:
    # Classic
    fade = Fade
    slide = Slide

    # Motion
    zoom = Zoom
    spin = Spin

    # Stylized
    flash = Flash

    # Shapes
    circle = CircleWipe

    # Abstract
    pixelate = Pixelate
    glitch = Glitch

    # Multi-layer
    split = SplitScreen

import numpy as np
from video_builder import logger


def add_vignette_effect(clip, intensity=0.5):
    """
    Apply vignette effect (darkened edges) to a clip.
    Custom implementation for MoviePy 2.x compatibility.
    
    Args:
        clip: The video clip to apply vignette to
        intensity: Darkness of the vignette (0.0-1.0), default 0.5
    
    Returns:
        Clip with vignette effect applied
    """
    try:
        from PIL import Image as PILImage, ImageDraw
        
        w, h = clip.size
        
        # Create vignette mask
        mask = PILImage.new('L', (w, h), 255)
        draw = ImageDraw.Draw(mask)
        
        # Create radial gradient for vignette
        for i in range(int(min(w, h) * 0.4)):
            alpha = int(255 * (1 - (i / (min(w, h) * 0.4)) * intensity))
            draw.ellipse(
                [i, i, w-i, h-i],
                fill=alpha
            )
        
        mask_array = np.array(mask) / 255.0
        
        def apply_vignette(get_frame, t):
            frame = get_frame(t)
            # Apply vignette by darkening edges
            vignette_frame = (frame * mask_array[:, :, np.newaxis]).astype('uint8')
            return vignette_frame
        
        return clip.transform(apply_vignette)
    except Exception as e:
        logger.warning(f"Could not apply vignette effect: {e}")
        return clip
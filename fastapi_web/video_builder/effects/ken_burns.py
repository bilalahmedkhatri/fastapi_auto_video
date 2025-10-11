from PIL import Image
import math
import numpy as np


def ken_burns_effect(clip, zoom_ratio):
    """Apply Ken Burns (zoom) effect to a clip"""
    def effect_func(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame)
        base_size = img.size

        # Calculate zoom
        zoom_factor = 1 + (zoom_ratio * t / clip.duration)
        new_size = [
            math.ceil(img.size[0] * zoom_factor),
            math.ceil(img.size[1] * zoom_factor)
        ]

        # Ensure even dimensions
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)
        # Resize and crop
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)
        # Correct crop box: (left, upper, right, lower)
        img = img.crop((
            x, y, x + base_size[0], y + base_size[1]
        )).resize(base_size, Image.Resampling.LANCZOS)

        result = np.array(img)
        img.close()
        return result

    try:
        return clip.transform(effect_func)
    except Exception as e:
        logging.error(f"Error applying Ken Burns effect: {e}")
        return clip  # fallback to original
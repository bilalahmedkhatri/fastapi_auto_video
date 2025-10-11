from moviepy import ColorClip, CompositeVideoClip

def create_base_composite_clip(
    image_clip,
    duration,
    background_color=(0, 0, 0),
    overlays=None,
    size=None,
    logger=None
):
    """
    Create a base composite video clip with a background, the main image, and optional overlays.
    """
    try:
        # Ensure the main image is centered and has the correct duration
        main_image = image_clip.with_position('center').with_duration(duration)

        # Create the background color clip
        background = ColorClip(
            size=size, color=background_color, duration=duration)

        # Compose the list of layers: background, main image, then overlays
        layers = [background, main_image]
        if overlays:
            layers.extend(overlays)

        composite = CompositeVideoClip(
            layers, size=size).with_duration(duration)
        return composite
    except Exception as e:
        logger.error(f"Error creating base composite clip: {e}")
        return image_clip.with_duration(duration)
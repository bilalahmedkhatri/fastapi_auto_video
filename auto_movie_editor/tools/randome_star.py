from moviepy import VideoFileClip, CompositeVideoClip
from moviepy.video.VideoClip import ColorClip
import numpy as np
import random

def make_star(size=3):
    return ColorClip(size=(size, size), color=(255, 255, 255)).with_duration(10)

def random_star_position(t, video_w, video_h):
    x = random.randint(0, video_w)
    y = int((t * 100) % video_h)  # Move vertically
    return x, y

def generate_stars(num_stars, video_w, video_h, duration):
    stars = []
    for _ in range(num_stars):
        star = make_star()
        x0 = random.randint(0, video_w)
        star = star.with_position(lambda t: random_star_position(t, video_w, video_h))
        stars.append(star)
    return stars

# 📹 Load your base video
video = VideoFileClip(r"G:\Development\\auto_movie_editor\\tools\\output_woz.mp4")
video_w, video_h = video.size
duration = video.duration

# ✨ Generate multiple stars
stars = generate_stars(num_stars=50, video_w=video_w, video_h=video_h, duration=duration)

# 🎬 Merge video with stars
final = CompositeVideoClip([video] + stars)
final.write_videofile("video_with_stars.mp4", codec='libx264')


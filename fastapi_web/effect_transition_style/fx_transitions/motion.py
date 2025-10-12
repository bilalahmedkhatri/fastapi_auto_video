from moviepy import VideoClip
from .base import TransitionBase
import cv2
import numpy as np

class Zoom(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            scale = 1 + 0.5*progress
            resized_clip = clip1.resized(scale)
            frame1 = resized_clip.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))

            h, w = self.size[1], self.size[0]
            # Crop the center of the zoomed frame
            if frame1.shape[0] >= h and frame1.shape[1] >= w:
                y, x = frame1.shape[0]//2 - h//2, frame1.shape[1]//2 - w//2
                frame1 = frame1[y:y+h, x:x+w]
            else:
                frame1 = cv2.resize(frame1, (w, h))
            
            # Ensure both frames have the same dtype
            frame1 = frame1.astype('float32')
            frame2 = frame2.astype('float32')

            result = cv2.addWeighted(frame1, 1-progress, frame2, progress, 0)
            return result.astype('uint8')
        
        clip = VideoClip(make_frame, duration=self.duration)
        clip.size = self.size
        return clip

class Spin(TransitionBase):
    def build_transition(self, clip1, clip2):
        def make_frame(t):
            progress = t / self.duration
            rotated_clip = clip1.rotated(progress*360)
            frame1 = rotated_clip.get_frame(min(t, clip1.duration-0.01))
            frame2 = clip2.get_frame(min(t, clip2.duration-0.01))
            
            # Ensure both frames have the same shape and dtype
            if frame1.shape != frame2.shape:
                frame1 = cv2.resize(frame1, (self.size[0], self.size[1]))
                frame2 = cv2.resize(frame2, (self.size[0], self.size[1]))
            
            # Ensure both frames have the same dtype
            frame1 = frame1.astype('float32')
            frame2 = frame2.astype('float32')
            
            result = cv2.addWeighted(frame1, 1-progress, frame2, progress, 0)
            return result.astype('uint8')
        
        clip = VideoClip(make_frame, duration=self.duration)
        clip.size = self.size
        return clip

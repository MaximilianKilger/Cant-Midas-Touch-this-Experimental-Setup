import cv2

# Wrapper class for everything that outputs an image.
class VideoSource:

    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def run(self):
        pass

    def stop(self):
        pass

    def get_last_frame(self):
        pass
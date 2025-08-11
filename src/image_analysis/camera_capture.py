import cv2
import yaml
import numpy as np
from collections import deque

from image_analysis.video_source import VideoSource

# Stores frames from a camera and makes them available to other processes.
# Also stores a camera's intrinsic calibration - can be run without a calibrated camera, but several other components require it.
class CameraCapture (VideoSource) :
    
    cap = None
    # @param calibration_filepath: Filepath to a OpenCV-style yaml-file with camera calibration
    def __init__(self,camera_id, num_cached_frames=1, calibration_filepath=None, width=None, height=None, fps=None):
        super().__init__(width, height)
        self.cap = cv2.VideoCapture()
        self.cap.open(camera_id, apiPreference=cv2.CAP_DSHOW)
        #self.cap.open(camera_id)
        if not self.cap.isOpened():
            print("unable to open video capture")
            exit()
        else:
            print("CAMERA OPENED")
        
        fourcc = cv2.VideoWriter_fourcc("M","J","P","G")
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if fps:
            self.cap.set(cv2.CAP_PROP_FPS, fps)

        self.frames = deque([], maxlen=num_cached_frames)
        if not calibration_filepath is None:
            fs = cv2.FileStorage(calibration_filepath, cv2.FILE_STORAGE_READ)
            self.camera_matrix = fs.getNode("mtx").mat()
            self.dist_coefficients = fs.getNode("dist").mat()
        
    # capture frames in an endless loop
    def run(self):
        self.running = True
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("No image")
                continue
            self.frames.append(frame)
            if cv2.waitKey(1) == ord('q'):
                break
    
    def get_last_frame(self):
        if len(self.frames) > 0:
            return self.frames[-1]
        else:
            return None
        
    def get_calibration(self):
        return self.camera_matrix, self.dist_coefficients
    
    def stop(self):
        self.running = False
        self.cap.release()


if __name__ == "__main__":
    capture = CameraCapture(0)
    capture.run()  
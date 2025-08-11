import cv2
from cv2.aruco import drawDetectedMarkers
import numpy as np
from image_analysis.camera_capture import CameraCapture
from image_analysis.aruco_tracker import ArucoTracker
from image_analysis.apriltag_tracker import ApriltagTracker
from image_analysis.hand_tracker import HandTracker, HandLandmarkID
from image_analysis.tangible_activeness_feedback import ActivenessFeedback
from image_analysis.video_source import VideoSource


from controls.rotation_valuator import RotationValuator
from controls.finger_slider_2d import FingerSlider2d
from controls.marker_visibility import MarkerVisibility
from controls.launchpad_controls import launchpadControls
from util.constants import CALIBRATION_FILEPATH
import threading
import time
import pygame
import pathlib

from util.constants import FRAME_WIDTH, FRAME_HEIGHT, FPS

# Takes frame from a VideoSource and displays it in an OpenCV window.
class FrameRenderer():
    def __init__(self, capture:VideoSource, win_name:str="frame"):
        self.capture = capture
        self.win_name = win_name
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        #cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        self.is_fullscreen = False
    
    def fullscreen_on(self):
        print("Fullscreen ON")
        self.is_fullscreen = True
        cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def fullscreen_off(self):
        print("Fullscreen OFF")
        self.is_fullscreen = False
        cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.fullscreen_off()
        else:
            self.fullscreen_on()

    def show_frame(self):
    
        frame = self.capture.get_last_frame()
        
        if not type(frame) is np.ndarray:
            return
        if not frame.shape[-1] > 0:
            return
        cv2.imshow(self.win_name, frame)

# Main Loop for handling several renderers at once
def run_all_displays(renderers:list[FrameRenderer]):
    time.sleep(1)
    while True:
        for renderer in renderers:
            renderer.show_frame()
        if cv2.waitKey(1) == ord('q'):
            return
        #time.sleep(0.01)

if __name__=="__main__":
    # some test code
    try:
        cap = CameraCapture(1, 7, CALIBRATION_FILEPATH, width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=FPS)
    except RuntimeError as e:
        print(e)
        exit(1)

    shower = FrameRenderer(cap)
    running = [True]

    display_list = [shower]  

    def onstop(running):
        cap.stop()
        running[0] = False

    try:
        capthread = threading.Thread(target=cap.run)
        capthread.start()
        run_all_displays(display_list)

        
    except RuntimeError as e:
        onstop(running)
        print("ERROR", e)
        raise e
    onstop(running)
    exit(0)
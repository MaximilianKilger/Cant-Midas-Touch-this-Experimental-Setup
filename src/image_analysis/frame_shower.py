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
from controls.key_button import KeyButton
from pynput import keyboard
import threading
import time
import pygame
import pathlib

from util.constants import FRAME_WIDTH, FRAME_HEIGHT, FPS

marker_app_map = {
        42: "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        44: "C:\\Windows\\System32\\notepad.exe"
    }

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
        #allcorners = []
        #
        #for id in aprilfinder.get_marker_ids():
        #    allcorners.append([aprilfinder.get_marker_data(id).get_corners_smoothed()])
        #    
        #if len(allcorners) > 0:
        #    if len(allcorners)== 1:
        #        
        #        allcorners = np.array(allcorners)
        #    else:
        #        
        #        allcorners = np.array(allcorners)
        #    
        #    drawDetectedMarkers(frame, allcorners)

        #if not fingerslider_2d.warped_boundaries is None:
        #    for boundary_point in fingerslider_2d.warped_boundaries[0].astype(int):
        #        cv2.circle(frame, boundary_point, 10, (0,128,255))

        #for fingertip in handfinder.findFingertips(landmark_id=8):
        #    cv2.circle(frame, fingertip, 10, (255,0,128))
                
        #cv2.imshow(self.win_name, cv2.resize(frame, (1280, 720)))
        cv2.imshow(self.win_name, frame)
    
def run_all_displays(renderers:list[FrameRenderer]):
    time.sleep(1)
    while True:
        for renderer in renderers:
            renderer.show_frame()
        if cv2.waitKey(1) == ord('q'):
            return
        #time.sleep(0.01)
if __name__=="__main__":
    try:
        cap = CameraCapture(1, 7, "./util/Logitech BRIO 0 2K.yml", width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=FPS)
    except RuntimeError as e:
        print(e)
        exit(1)
    
    bound_points_fp = str(pathlib.PurePath(pathlib.Path(__file__).parent.parent, "config_files/boundaries_trackpad_test_paper.json"))

    markerfinder = ArucoTracker()
    aprilfinder = ApriltagTracker()
    handfinder = HandTracker()
    shower = FrameRenderer(cap)
    rot_valuator = RotationValuator(markerfinder, 42, -20* np.pi, 20*np.pi)
    marker_visibility = MarkerVisibility(markerfinder, marker_app_map)
    fingerslider_2d = FingerSlider2d(aprilfinder, handfinder, 3, bound_points_fp)
    lc = launchpadControls(rot_valuator, fingerslider_2d, marker_visibility)

    running = [True]

    #def onpress(key):
    #    if hasattr(key, 'char'):
    #        if key.char == 'f':
    #            
    #            if feedback_shower.is_fullscreen:
    #                feedback_shower.fullscreen_off()
    #            else:
    #                feedback_shower.fullscreen_on()
        
    def keep_reading_value ():
        
        while running[0]:
            #value = rot_valuator.getValue()
            #print("Status:", rot_valuator.isActive())
            #print("Rotation value", value)
            value = fingerslider_2d.getValue()
            rot = rot_valuator.getValue()
            marker = marker_visibility.update()
            #print("Status: ", fingerslider_2d.isActive())
            print("Slider",value )
            print("Rotation: ", rot)
            print("Marker: ", marker)
           # marker_visibility.update()
            #lc.update()
           
            
            #print(keybutton.getState())
           # if not value is None:
           #     print(round(value, 2))
           # print(fingerslider_2d.getValue())
        time.sleep(0.01)
            #Changes End

        bound_points = np.array([
        [-10.2, -15.2],
        [-10.2,  14.2],
        [ 10.7,  14.2],
        [ 10.7, -15.2]
    ])

    keybutton = KeyButton(keyboard.KeyCode(char="a"), toggle=False)
    display_list = [shower]  

    def onstop(running):
        cap.stop()
        markerfinder.stop_tracking()
        aprilfinder.stop_tracking()
        handfinder.stop_tracking()
        running[0] = False

    try:
        capthread = threading.Thread(target=cap.run)
        capthread.start()

        aruco_thread = threading.Thread(target = lambda: markerfinder.run_tracking(cap))
        aruco_thread.start()

        april_thread = threading.Thread(target = lambda: aprilfinder.run_tracking(cap))
        april_thread.start()

        handfinder_thread = threading.Thread(target=lambda: handfinder.run_tracking(cap))
        handfinder_thread.start()
        
        rotator_thread = threading.Thread(target=keep_reading_value)
        rotator_thread.start()

        lc_thread = threading.Thread(target=lc.update)
        lc_thread.start()
        
        run_all_displays(display_list)
        #shower.show_frame()

        
    except RuntimeError as e:
        onstop(running)
        print("ERROR", e)
        raise e
    onstop(running)
    exit(0)
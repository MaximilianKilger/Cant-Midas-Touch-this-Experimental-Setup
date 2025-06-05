import cv2
import numpy as np
import sys
import pyautogui
import pathlib
import threading
import time
from pynput import keyboard

from image_analysis.camera_capture import CameraCapture
from image_analysis.apriltag_tracker import ApriltagTracker
from image_analysis.frame_shower import FrameRenderer, run_all_displays
from image_analysis.hand_tracker import HandTracker, HandLandmarkID
from image_analysis.tangible_activeness_feedback import ActivenessFeedback

from controls.finger_slider_2d import FingerSlider2d
from controls.launchpad_controls import launchpadControls
from controls.rotation_valuator import RotationValuator
from controls.manual_controls import manualControls
from controls.marker_visibility import MarkerVisibility
from controls.window_manager import WindowManager

from util.constants import *

#Add comment in texteditor with ctr + alt + m
#@staticmethod
def add_comment():
    print("Tacker verwendet")
    pyautogui.hotkey("ctrl", "alt", "m")


# Undo with ctrl +z
#@staticmethod
def undo_comment():
    print("Radierer verwendet")
    pyautogui.hotkey("esc")

def undo():
    print("Radierer verwendet")
    pyautogui.hotkey("ctrl", "z")

#Insert text with ctrl + v
def paste():
    pyautogui.hotkey("ctrl", "v")

#Cut element/text with ctrl + x
#@staticmethod
def cut():
    print("Schere verwendet")
    pyautogui.hotkey("ctrl", "x")

def cut_once():
    print("Schere verwendet")
    #with pyautogui.hold('shift'):
    pyautogui.press('delete')
    #time.sleep(0.01)
    #pyautogui.hotkey("ctrl", "x")

#Highlight all with ctrl + a
#@staticmethod
def select_all():
    print("Textmarker benutzt")
    pyautogui.hotkey("ctrl", "a")




if __name__ == "__main__":

    condition = 0

    if len(sys.argv) >= 2:
        condition = int(sys.argv[1])

    print(f"Condition: {condition}")



    #rotator_marker_id = 26
    #trackpad_marker_id = 3
    
    #pageturner_marker_ids = {7:0,
    #                         8:1}
    
    #highlighter_marker_id = 20
    #scissors_marker_id = 21
    #glue_marker_id = 22
    #stapler_marker_id = 0
    #eraser_marker_id = 24

    state_to_app_path = {}
    if condition == 0 or condition == '0':

        state_to_app_path = {
            0: "https://docs.google.com/document/d/19IPy1auMKH6U8BtKvGb_GYpp5umxtI2Q7_6l2DvNI-Q/edit?tab=t.0",
            #0: "https://docs.google.com/document/d/1H5BQ1pPgICF9F91iXpshlsbpfMD4u4AGcJvliv1l8tk/edit?tab=t.0",
            1: "C:\\Users\\LocalAdmin\\Desktop\\Textausschnitt_1.txt"
            #1: "C:\\Users\\LocalAdmin\\Desktop\\Textausschnitt_2.txt"
        }
    elif condition == 1 or condition == '1':
        state_to_app_path = {
            0: "https://docs.google.com/document/d/1H5BQ1pPgICF9F91iXpshlsbpfMD4u4AGcJvliv1l8tk/edit?tab=t.0",
            1: "C:\\Users\\LocalAdmin\\Desktop\\Textausschnitt_2.txt"
        }
    else:
        print("unknown condition")
        exit(1)

    bound_points_fp = str(pathlib.PurePath(pathlib.Path(__file__).parent.parent, "config_files/boundaries_trackpad_test_paper.json"))
    
    apriltag_lengths = {} # TODO: Fill as needed
    marker_tracker = ApriltagTracker(apriltag_lengths)
    hand_tracker = HandTracker()
    capture = CameraCapture(CAMERA_ID, width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=FPS)
    capture_renderer = FrameRenderer(capture, "frame")

    rotator = RotationValuator(marker_tracker, ROTATOR_MARKER_ID, -20*np.pi, 20*np.pi)
    trackpad = FingerSlider2d(marker_tracker, hand_tracker, TRACKPAD_MARKER_ID, bound_points_fp)
    pageturner = MarkerVisibility(marker_tracker,PAGETURNER_MARKER_IDS)
    marker = manualControls(select_all)
    scissors = manualControls(cut)
    glue = manualControls(paste)
    stapler = manualControls(add_comment)
    eraser = manualControls(undo_comment)
    eraser2 = manualControls(undo)
    scissors2 = manualControls(cut_once)

    window_manager = WindowManager(state_to_app_path)

    feedback_controls = {
        ROTATOR_MARKER_ID: rotator,
        "(14,5)": pageturner,
        "(13,6)": pageturner,
        "(16,7)":pageturner,
        f"({TRACKPAD_MARKER_ID}, 15)": trackpad,
        HIGHLIGHTER_MARKER_ID: marker,
        SCISSORS_MARKER_ID: scissors,
        GLUE_MARKER_ID: glue,
        STAPLER_MARKER_ID: stapler,
        ERASER_MARKER_ID: eraser
    }

    feedback_manager = ActivenessFeedback(PROJECTOR_WIDTH, PROJECTOR_HEIGHT, feedback_controls, FEEDBACK_OFFSETS, FEEDBACK_RADII, marker_tracker, "./config_projector.ini")
    feedback_renderer = FrameRenderer(feedback_manager, "FEEDBACK")

    #TODO: Turn actions we need to do during the experiment into manualControls and map them to a launchpad button, e.g. maximizing and minimizing the feedback view
    

    #pageturner.activate()
    last_scroll_delta = [0]
    def scroll(value):
        
        scroll_speed = -100000
        scroll_delta = int(value * scroll_speed)

        if abs(scroll_delta - last_scroll_delta[0]) > 1:
            try:
                pyautogui.scroll(scroll_delta - last_scroll_delta[0])  
            except pyautogui.FailSafeException as e:
                print(e)
            print(f"Scroll Units: {scroll_delta - last_scroll_delta[0]}, Wert: {value}")

        last_scroll_delta[0] = scroll_delta

    control_loop_delay = 1/CONTROL_UPDATE_FREQUENCY_HZ
    def update_automatic_controls():
        while(running[0]):
            rot_value = rotator.getValue()
            page_state = pageturner.getState()
            #print("STATE",page_state)
            if not rot_value is None:
                scroll(rot_value)
            if not page_state is None:
                window_manager.switch_to_window(page_state)
            time.sleep(control_loop_delay)

    def all_windows_fullscreen ():
        feedback_renderer.toggle_fullscreen()
    
    manual_fullscreener = manualControls(all_windows_fullscreen)
    manual_fullscreener.activate()
        



    function_map = {
            (0, 7): marker,#MARKER
            (1, 7): scissors,#SCISSORS
            (1, 6): scissors2,#SCISSORS
            (2, 7): glue,#GLUE
            (3, 7): stapler,#STAPLER
            (4, 7): eraser,#ERASER
            (4, 6): eraser2,
            (5, 7): rotator,
            (6, 7): trackpad,
            (7, 7): pageturner,
            (0, 1): manual_fullscreener
        }
    

    lc = launchpadControls(function_map)

    def on_press(key):
        if key == keyboard.Key.f22:
            delay = np.random.normal(PEDAL_DELAY_MEAN_SECONDS, PEDAL_DELAY_STANDARD_DEVIATION_SECONDS)
            time.sleep(delay)
            lc.toggle_all_functions(pressed=True)
    
    

    running = [True] #wrapping the bool in a list to circumvent call-by-value-behavior in function calls

    def onstop(running):
        capture.stop()
        marker_tracker.stop_tracking()
        hand_tracker.stop_tracking()
        lc.stop()
        
        key_listener.stop()
        feedback_manager.stop()
        running[0] = False

    capthread = threading.Thread(target=capture.run)
    capthread.start()

    marker_thread = threading.Thread(target = lambda: marker_tracker.run_tracking(capture))
    marker_thread.start()

    hand_thread = threading.Thread(target=lambda: hand_tracker.run_tracking(capture))
    hand_thread.start()
    
    automatic_thread = threading.Thread(target=update_automatic_controls)
    automatic_thread.start()

    lc_thread = threading.Thread(target=lc.update)
    lc_thread.start()

    feedback_thread = threading.Thread(target = feedback_manager.run)
    feedback_thread.start()
    
    key_listener = keyboard.Listener(on_press=on_press)
    key_listener.start()

    run_all_displays([capture_renderer, feedback_renderer])

    onstop(running)

        

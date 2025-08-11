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

# Define what each of the tangibles simulated with a Wizard-of-Oz approach should do (in the form of a function).

#Add comment in texteditor with ctr + alt + m
#@staticmethod
def add_comment():
    print("Tacker verwendet")
    pyautogui.hotkey("ctrl", "alt", "m")


# Undo creation of comment
#@staticmethod
def undo_comment():
    print("Radierer verwendet")
    pyautogui.hotkey("esc")

# undo general actions
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

#Cut one character at a time
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

    # read first CLI argument as condition
    if len(sys.argv) >= 2:
        condition = int(sys.argv[1])

    print(f"Condition: {condition}")
    
    # create a dict for the page turning / application switching tangible
    state_to_app_path = {}
    # depending on condition, change the files used in the trial
    if condition == 0 or condition == '0':
        state_to_app_path = {
            # key is a state, outputted by a StateSelector.
            # value is an URL or local file to be accessed when a given state is outputted.
            0: "https://docs.google.com/document/d/19IPy1auMKH6U8BtKvGb_GYpp5umxtI2Q7_6l2DvNI-Q/edit?tab=t.0",
            1: "C:\\Users\\LocalAdmin\\Desktop\\Textausschnitt_1.txt"
        }
    elif condition == 1 or condition == '1':
        state_to_app_path = {
            0: "https://docs.google.com/document/d/1H5BQ1pPgICF9F91iXpshlsbpfMD4u4AGcJvliv1l8tk/edit?tab=t.0",
            1: "C:\\Users\\LocalAdmin\\Desktop\\Textausschnitt_2.txt"
        }
    else:
        print("unknown condition")
        exit(1)

    # read boundary points of interactable area on the folder tangible (relative to the position of the AprilTag) from a file
    bound_points_fp = str(pathlib.PurePath(pathlib.Path(__file__).parent.parent, "config_files/boundaries_trackpad_test_paper.json"))
    
    # Initialize all OpportunisticControls used in the experiment
    apriltag_lengths = {} # TODO: Fill as needed
    marker_tracker = ApriltagTracker(apriltag_lengths)
    hand_tracker = HandTracker()
    capture = CameraCapture(CAMERA_ID, width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=FPS)
    # output camera frame to researcher screen
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

    # Bind marker IDs to OpportunisticControls for the FeedbackManager
    feedback_controls = {
        ROTATOR_MARKER_ID: rotator,
        5: pageturner,
        6: pageturner,
        7:pageturner,
        TRACKPAD_MARKER_ID: trackpad,
        HIGHLIGHTER_MARKER_ID: marker,
        SCISSORS_MARKER_ID: scissors,
        GLUE_MARKER_ID: glue,
        STAPLER_MARKER_ID: stapler,
        ERASER_MARKER_ID: eraser
    }

    feedback_manager = ActivenessFeedback(PROJECTOR_WIDTH, PROJECTOR_HEIGHT, feedback_controls, FEEDBACK_OFFSETS, FEEDBACK_RADII, marker_tracker, "./config_projector.ini")
    # output of feedback manager goes to the projector
    feedback_renderer = FrameRenderer(feedback_manager, "FEEDBACK")

    #pageturner.activate()
    last_scroll_position = [0] #wrapped in a list to circumvent weird python behavior with call-by-value variables
    # Takes the value of a RotationValuator, compares it to the last value, scrolls by that amount
    def scroll(value):
        
        scroll_speed = -100000
        scroll_position = int(value * scroll_speed)

        if abs(scroll_position - last_scroll_position[0]) > 1:
            try:
                pyautogui.scroll(scroll_position - last_scroll_position[0])
            except pyautogui.FailSafeException as e:
                print(e)
            print(f"Scroll Units: {scroll_position - last_scroll_position[0]}, Wert: {value}")

        last_scroll_position[0] = scroll_position

    control_loop_delay = 1/CONTROL_UPDATE_FREQUENCY_HZ
    # continuously reads values from rotationvaluator and state selector and processes them
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

    # convenience function - just turns all of our windows fullscreen
    def all_windows_fullscreen ():
        feedback_renderer.toggle_fullscreen()
    
    manual_fullscreener = manualControls(all_windows_fullscreen)
    manual_fullscreener.activate()
        


    # maps ManualControls to buttons on the Launchpad
    function_map = {
            (0, 7): marker,#MARKER
            (1, 7): scissors,#SCISSORS
            (1, 6): scissors2,#SCISSORS
            (2, 7): glue,#GLUE
            (3, 7): stapler,#STAPLER
            (4, 7): eraser,#ERASER
            (4, 6): eraser2,
            (5, 7): rotator,#Trackpad, Rotator and Pageturner are not triggered by the launchpad, but this way, it automatically sets the right buttons for clutching
            (6, 7): trackpad, 
            (7, 7): pageturner,
            (0, 1): manual_fullscreener
        }
    

    lc = launchpadControls(function_map)

    # handles "keyboard input" triggered by the pedal
    def on_press(key):
        if key == keyboard.Key.f22:
            # introduce gaussian random delay to simulate human reaction time in Wizard-of-Oz conditions
            delay = np.random.normal(PEDAL_DELAY_MEAN_SECONDS, PEDAL_DELAY_STANDARD_DEVIATION_SECONDS)
            time.sleep(delay)
            lc.toggle_all_functions(pressed=True)
    
    

    running = [True] #wrapping the bool in a list to circumvent call-by-value-behavior in function calls

    # stop all threads
    def onstop(running):
        capture.stop()
        marker_tracker.stop_tracking()
        hand_tracker.stop_tracking()
        lc.stop()
        
        key_listener.stop()
        feedback_manager.stop()
        running[0] = False

    #start all threads
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

        

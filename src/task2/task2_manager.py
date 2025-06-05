from task2.slideshow_viewer import SlideshowViewer
from image_analysis.frame_shower import FrameRenderer
from image_analysis.apriltag_tracker import ApriltagTracker
from image_analysis.aruco_tracker import ArucoTracker
from image_analysis.hand_tracker import HandTracker
from controls.finger_slider_2d import FingerSlider2d
from image_analysis.camera_capture import CameraCapture
from controls.launchpad_controls import launchpadControls
from controls.rotation_valuator import RotationValuator
from controls.marker_visibility import MarkerVisibility
from controls.trackpad import Trackpad
import threading
import numpy as np

from pynput import keyboard
import cv2
import time
import sys
import pathlib
from controls.manual_controls import manualControls
from image_analysis.tangible_activeness_feedback import ActivenessFeedback
from util.constants import FRAME_WIDTH, FRAME_HEIGHT, FPS, ZOOM_SPEED, PROJECTOR_WIDTH, PROJECTOR_HEIGHT, FEEDBACK_RADII, FEEDBACK_OFFSETS, CAMERA_ID, ROTATOR_MARKER_ID,TRACKPAD_MARKER_ID
from util.constants import *

if __name__ == "__main__":
    task_condition = 0
    if len(sys.argv) >= 2:
        task_condition = sys.argv[1]
    print(f"Condition: {task_condition}")
    running = [True]

    filepaths_cond1 = [
        "./task2/task2_images/Wimmelbild_06.png",
        "./task2/task2_images/Wimmelbild_07.png",
        "./task2/task2_images/Wimmelbild_08.png"
    ]

    filepaths_cond2 = [
        "./task2/task2_images/Wimmelbild_09.png",
        "./task2/task2_images/Wimmelbild_10.png",
        "./task2/task2_images/Wimmelbild_12.png"
    ]

    filepaths = None
    if task_condition == 0 or task_condition == "0":
        filepaths = filepaths_cond1
    elif task_condition == 1 or task_condition == "1":
        filepaths = filepaths_cond2
    else:
        print("Unidentified task condition")

    bound_points_fp = str(pathlib.PurePath(pathlib.Path(__file__).parent.parent, "config_files/boundaries_trackpad_test_paper.json"))
    slideshow = SlideshowViewer(1280, 720, filepaths, blocking_mode=True)
    frame_shower = FrameRenderer(slideshow)



    pageturner_marker_ids = {5:0,
                            6:1,
                            7:2
                            }
    
    def dummy():
        print("DUMMY")
    
    
    marker = manualControls(slideshow.mark)
    scissors = manualControls(dummy)
    glue = manualControls(dummy)
    stapler = manualControls(dummy)
    eraser = manualControls(dummy)

    trackpad_marker_id = 3

    apriltag_lengths = {} # TODO: Fill as needed
    marker_tracker = ApriltagTracker(apriltag_lengths)
    hand_tracker = HandTracker()

    rotator = RotationValuator(marker_tracker, ROTATOR_MARKER_ID, -20*np.pi, 20*np.pi)
    trackpad = FingerSlider2d(marker_tracker, hand_tracker, TRACKPAD_MARKER_ID, bound_points_fp)
    pageturner = MarkerVisibility(marker_tracker,pageturner_marker_ids)
    
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

    
    def all_windows_fullscreen ():
        feedback_renderer.toggle_fullscreen()
        frame_shower.toggle_fullscreen()
        
    
    manual_fullscreener = manualControls(all_windows_fullscreen)
    manual_fullscreener.activate()
        

    function_map = {
        (0, 7): marker,#MARKER
        (1, 7): scissors,#SCISSORS
        (2, 7): glue,#GLUE
        (3, 7): stapler,#STAPLER
        (4, 7): eraser,#ERASER
        (5, 7): rotator,
        (6, 7): trackpad,
        (7, 7): pageturner,
        (0, 1): manual_fullscreener
    }

    lc = launchpadControls(function_map)
    trackpad = Trackpad(trackpad, slideshow)

    
    def on_press(key):
        
        if key == keyboard.Key.f22:
            delay = np.random.normal(PEDAL_DELAY_MEAN_SECONDS, PEDAL_DELAY_STANDARD_DEVIATION_SECONDS)
            time.sleep(delay)
            lc.toggle_all_functions(pressed=True)
    
    


    cap = CameraCapture(
        camera_id=CAMERA_ID,
        num_cached_frames=7,
        calibration_filepath="./util/Logitech BRIO 0 2K.yml",
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        fps=FPS
    )
    camera_renderer = FrameRenderer(cap, "OVERHEAD CAMERA")

    def slideshow_controls():
        previous_value = rotator.getValue()
        while running[0]:
            time.sleep(0.01)
            previous_value = zoom(previous_value)
            change_image()
    

    def zoom(previous_value):
        
        current_value = rotator.getValue()
        if current_value is not None and previous_value is not None:
            delta = (current_value - previous_value) * ZOOM_SPEED
            slideshow.zoom(delta)
            print("DELTA" , delta)
        return current_value

    def change_image():
        marker_value = pageturner.getState()
        slideshow.jump_to_image(marker_value)
            

    camera_thread = threading.Thread(target=cap.run)
    camera_thread.start()

    capthread = threading.Thread(target=cap.run)
    capthread.start()

    hand_thread = threading.Thread(target=lambda: hand_tracker.run_tracking(cap))
    hand_thread.start()

    marker_thread = threading.Thread(target = lambda: marker_tracker.run_tracking(cap))
    marker_thread.start()

    trackpad_thread = threading.Thread(target = lambda: trackpad.update(running, cap))
    trackpad_thread.start()
    
    slideshow_thread = threading.Thread(target=slideshow.start)
    slideshow_thread.start()

    rotator_thread = threading.Thread(target=slideshow_controls)
    rotator_thread.start()

    lc_thread = threading.Thread(target=lc.update)
    lc_thread.start()

    key_listener = keyboard.Listener(on_press=on_press)
    key_listener.start()

    feedback_thread = threading.Thread(target = feedback_manager.run)
    feedback_thread.start()

    while running[0]:
        #frame = cap.get_last_frame()
        feedback_frame = feedback_manager.get_last_frame()

        #if frame is not None:
            #cv2.imshow("Trackpad View", frame)
        frame_shower.show_frame()
        feedback_renderer.show_frame()
        camera_renderer.show_frame()

            

        if cv2.waitKey(1) == ord('q'):
            running[0] = False

    cap.stop()  
    cv2.destroyAllWindows()
    slideshow.stop()
    #trackpad_thread.join()
    #slideshow_thread.join()
    #camera_thread.join()
    cap.stop()
    lc.stop()
    key_listener.stop()
    feedback_manager.stop()

    marker_tracker.stop_tracking()
    hand_tracker.stop_tracking()

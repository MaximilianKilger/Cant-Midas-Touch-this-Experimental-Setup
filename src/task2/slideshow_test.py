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

from util.constants import FRAME_WIDTH, FRAME_HEIGHT, FPS

if __name__ == "__main__":

    running = [True]

    def panleft():
        slideshow.pan(-15, 0)

    def panright():
        slideshow.pan(15, 0)

    def panup():
        slideshow.pan(0, -15)

    def pandown():
        slideshow.pan(0, 15)

    def zoomin():
        slideshow.zoom(0.2)

    def zoomout():
        slideshow.zoom(-0.2)

    def onpress(keycode):
        if keycode == keyboard.Key.left:
            panleft()
        elif keycode == keyboard.Key.right:
            panright()
        elif keycode == keyboard.Key.up:
            panup()
        elif keycode == keyboard.Key.down:
            pandown()
        elif hasattr(keycode, "char"):
            if keycode.char == "+":
                zoomin()
            elif keycode.char == '-':
                zoomout()
            elif keycode.char == 'p':
                slideshow.previous_image()
            elif keycode.char == 'n':
                slideshow.next_image()
            elif keycode.char == 'm':
                slideshow.mark()
        elif keycode == keyboard.Key.esc:
            slideshow.kill()
            running[0] = False

    filepaths = [
        "./task2/task2_images/10x10.png",
        "./task2/task2_images/20x10.png",
        "./task2/task2_images/supper.jpg"
    ]

    pageturner_marker_ids = {7:0,
                            8:1}

    marker_tracker = ApriltagTracker()
    hand_tracker = HandTracker()
    aruco_tracker = ArucoTracker()
    marker_id = 3
    bound_points = np.array([
        [-10.2, -15.2],
        [-10.2,  14.2],
        [ 10.7,  14.2],
        [ 10.7, -15.2]
    ])


    finger_slider = FingerSlider2d(marker_tracker, hand_tracker, marker_id, bound_points)
    rotation = RotationValuator(aruco_tracker, 42, -20* np.pi, 20*np.pi) 
    visibility = MarkerVisibility(marker_tracker, pageturner_marker_ids)
    slideshow = SlideshowViewer(1280, 720, filepaths, blocking_mode=True)
    frame_shower = FrameRenderer(slideshow)
   # lc = launchpadControls(rotation, finger_slider, visibility)
    trackpad = Trackpad(finger_slider, slideshow)

    cap = CameraCapture(
        camera_id=0,
        num_cached_frames=7,
        calibration_filepath="./util/Logitech BRIO 0 2K.yml",
        width=FRAME_WIDTH,
        height=FRAME_HEIGHT,
        fps=FPS
    )

    camera_thread = threading.Thread(target=cap.run)
    camera_thread.start()


    #finger_thread = threading.Thread(target=finger_slider)
    #finger_thread.start()
    capthread = threading.Thread(target=cap.run)
    capthread.start()

    hand_thread = threading.Thread(target=lambda: hand_tracker.run_tracking(cap))
    hand_thread.start()

    marker_thread = threading.Thread(target = lambda: marker_tracker.run_tracking(cap))
    marker_thread.start()

    trackpad_thread = threading.Thread(target = lambda: trackpad.update(running, cap))
    trackpad_thread.start()

    listener = keyboard.Listener(on_press=onpress)
    listener.start()

    slideshow_thread = threading.Thread(target=slideshow.start)
    slideshow_thread.start()

    #lc_thread = threading.Thread(target=lc.update)
    #lc_thread.start()


    while running[0]:
        frame = cap.get_last_frame()
        if frame is not None:
            cv2.imshow("Trackpad View", frame)
            frame_shower.show_frame()

        if cv2.waitKey(1) == ord('q'):
            running[0] = False

    cap.stop()  
    cv2.destroyAllWindows()
    listener.stop()
    slideshow.stop()
    trackpad_thread.join()
    slideshow_thread.join()
    camera_thread.join()

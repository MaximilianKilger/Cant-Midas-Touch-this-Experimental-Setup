import numpy as np
from controls.valuator import Valuator
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from scipy.spatial.transform import Rotation
import cv2  # only for visualization
from util.constants import MIN_SKIPPABLE_ROTATION, MARKER_MAX_TIME_MISSING
import pyautogui

VISUALIZE_ROTATION = False


class RotationValuator(Valuator):
    def __init__(self, marker_tracker, marker_id, min_gamma=-np.pi, max_gamma=np.pi, initialValue=0.5):
        self.tracker: MarkerTracker = marker_tracker
        self.marker_id = marker_id
        self.num_full_rotations = 0
        self.last_gamma = None
        self.cumulative_gamma = min_gamma + initialValue * (max_gamma - min_gamma)
        self.min_gamma = min_gamma
        self.max_gamma = max_gamma
        self.last_scroll_delta = 0  
        self.deactivate()

    def update_angle(self):
        #rmat, tvec = self.tracker.get_marker_transformation(self.marker_id)
        #if rmat is None:
        #    return None
        #rot = Rotation.from_matrix(rmat)
        #euler = rot.as_euler("zyx", degrees=False)
        #gamma = euler[0] 

        gamma = self.tracker.get_marker_rotation(self.marker_id)

        if gamma is None:
            return
        if self.last_gamma is None:
            self.last_gamma = gamma
        delta_gamma = gamma - self.last_gamma

        if abs(delta_gamma) >= 2 * np.pi * MIN_SKIPPABLE_ROTATION:
            print("Rotation skip triggered")
            sign = np.sign(delta_gamma)
            delta_gamma = sign * -2 * np.pi + delta_gamma

        if abs(delta_gamma) < 0.01:  
            delta_gamma = 0

        self.cumulative_gamma = min(self.max_gamma, max(self.min_gamma, self.cumulative_gamma + delta_gamma))
        self.last_gamma = gamma

        if VISUALIZE_ROTATION:
            self.visualize(gamma)

    def visualize(self, gamma=None):
        SIZE = 50
        COLOR_CUMUL_GAMMA = (255, 255, 255)
        COLOR_GAMMA = (255, 0, 0)

        img = np.zeros((2 * SIZE, 2 * SIZE, 3))

        if gamma:
            x_gamma = int(np.sin(gamma) * SIZE + SIZE)
            y_gamma = int(np.cos(gamma) * SIZE + SIZE)
            cv2.line(img, (SIZE, SIZE), (x_gamma, y_gamma), COLOR_GAMMA)

        x_cumulative_gamma = int(np.sin(self.cumulative_gamma) * SIZE + SIZE)
        y_cumulative_gamma = int(np.cos(self.cumulative_gamma) * SIZE + SIZE)
        cv2.line(img, (SIZE, SIZE), (x_cumulative_gamma, y_cumulative_gamma), COLOR_CUMUL_GAMMA)
        cv2.imshow("Rotation Valuator", img)
        cv2.waitKey(1)

    def getValue(self):
        if not self.isActive():
            return

        missing_time = self.tracker.get_marker_missing_time(self.marker_id)
        if missing_time is None or missing_time > MARKER_MAX_TIME_MISSING:
            self.last_scroll_delta = 0
            return

        self.update_angle()

        value = self.cumulative_gamma / (self.max_gamma - self.min_gamma)
        #print(f"Cumulative Gamma: {self.cumulative_gamma}, Value: {value}")

        #scroll_speed = 50000
        #scroll_delta = int(value * scroll_speed)

        #if abs(scroll_delta - self.last_scroll_delta) > 1:
        #    pyautogui.scroll(scroll_delta - self.last_scroll_delta)  
        #    print(f"Scroll Units: {scroll_delta - self.last_scroll_delta}, Wert: {value}")

        #self.last_scroll_delta = scroll_delta

        return value


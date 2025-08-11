import numpy as np
from controls.valuator import Valuator
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from scipy.spatial.transform import Rotation
import cv2  # only for visualization
from util.constants import MIN_SKIPPABLE_ROTATION, MARKER_MAX_TIME_MISSING
import pyautogui

VISUALIZE_ROTATION = False

# Tracks the rotation angle γ of a marker and turns it into a value between 0 and 1.
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
        # get rotation angle of marker as gamma
        gamma = self.tracker.get_marker_rotation(self.marker_id)

        if gamma is None:
            return
        if self.last_gamma is None:
            self.last_gamma = gamma
        # compute difference between the gamme this frame and last frame
        delta_gamma = gamma - self.last_gamma

        # if the angle skips from almost 0° to almost 360° in a single frame or vice versa, 
        # we assume that it rotated past 0° or 360° and was clamped to a valid angle.
        if abs(delta_gamma) >= 2 * np.pi * MIN_SKIPPABLE_ROTATION:
            print("Rotation skip triggered")
            sign = np.sign(delta_gamma)
            # we subtract this huge skip from a full rotation to get the true delta.
            delta_gamma = sign * -2 * np.pi + delta_gamma

        # don't count very small rotations
        if abs(delta_gamma) < 0.01:  
            delta_gamma = 0

        # add the difference from last frame to the cumulative gamma value and clamp between min and max
        self.cumulative_gamma = min(self.max_gamma, max(self.min_gamma, self.cumulative_gamma + delta_gamma))
        self.last_gamma = gamma

        if VISUALIZE_ROTATION:
            self.visualize(gamma)

    # opens a new small window to visualize the true rotation vs the current value of cumulative_gamma.
    # helps with debugging.
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

    # turn current cumulative_gamma into a value between 0 and 1
    def getValue(self):
        if not self.isActive():
            return

        missing_time = self.tracker.get_marker_missing_time(self.marker_id)
        if missing_time is None or missing_time > MARKER_MAX_TIME_MISSING:
            self.last_scroll_delta = 0
            return

        self.update_angle()

        value = self.cumulative_gamma / (self.max_gamma - self.min_gamma)
        return value


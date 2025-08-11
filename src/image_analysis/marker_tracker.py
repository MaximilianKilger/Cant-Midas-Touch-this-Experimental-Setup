import numpy as np
from image_analysis.camera_capture import CameraCapture
import time
import cv2
from collections import deque
from util.constants import BUFFERED_MARKER_CORNERS
from util.util import calculate_angle

from threading import Lock

# Generic class for storing corner points and orientation of Aruco-Style fiducial markers.
# Also keeps track of the time since that marker was last detected.
# The last n corner points are buffered, to enable smoothing. Otherwise the cornerpoints get very jittery.
class MarkerData:
    #corners = np.empty((4,2))

    def __init__(self, id):
        self.id = id
        self.corners:deque[np.ndarray] = deque(maxlen=BUFFERED_MARKER_CORNERS)
        self.rotation = np.empty((4,3))
        self.translation = np.empty((3,1))
        self.marker_length = None
        id = None
        self.missing_time_ms = -1 # time since the last detection of the marker in milliseconds

    # sets side length of a marker in cm.
    def set_length(self, marker_length):
        self.marker_length = marker_length

    # updates detected corner points of the marker (in image space)
    def update_corners(self, corners):
        if type(corners) == np.ndarray:
            if corners.shape == (4,2):
                self.corners.appendleft(corners)

    # sets both rotation and translation of markers.
    def set_transformation(self, rmat, tvec):
        self.rotation = rmat
        self.translation = tvec

    def reset_missing_time(self):
        self.missing_time_ms = 0

    # delta: time to be added to missing_time in milliseconds
    def add_to_missing_time(self, delta):
        self.missing_time_ms += delta

    
    def get_length(self):
        return self.marker_length
    
    def get_corners(self):
        return self.corners[0]
    
    #computes the median corner coordinates over a rolling window of the detected marker corners within the last n frames.
    def get_corners_smoothed(self, n=None):
        if not n is None and n <= len(self.corners):
            return np.mean(np.array(self.corners[:n]), axis=0)
        return np.mean(np.array(self.corners), axis=0)
    
    def get_transformation(self):
        return self.rotation, self.translation
    
    def get_missing_time(self):
        return self.missing_time_ms
    
# generic class for tracking Aruco-style fiducial markers.
class MarkerTracker:

    # if lengths of markers is known, 
    def __init__(self, predefined_marker_lengths=dict([])):
        self.marker_lengths:dict[str, float] = predefined_marker_lengths
        self.marker_state:dict[str, MarkerData] = {}
        #TODO: Reevaluate if the mutex is necessary
        self.mutex_state:Lock = Lock()
        self.last_frame_timestamp = None

    #please override this function
    def find_markers(self, frame):
        pass

    # returns rotation and translation of marker relative to camera
    def get_marker_transformation(self, id):
        if not id in self.marker_state.keys():
            return None, None
        with self.mutex_state:
            corners = self.marker_state[id].get_corners_smoothed()
            marker_length = self.marker_state[id].get_length()
        return self._find_marker_transformation(corners, marker_length)

    # calculates rotation and translation of markers in 3D space from their corners and side lengths.
    def _find_marker_transformation(self, corners, marker_length):
        
        object_points = np.array([
            [-marker_length/2, marker_length/2, 0],
            [marker_length/2, marker_length/2, 0],
            [marker_length/2, -marker_length/2, 0],
            [-marker_length/2, -marker_length/2, 0]
        ])
        
        ret, rotation, translation = cv2.solvePnP(object_points, corners, self.capture.camera_matrix, self.capture.dist_coefficients)
        rmat, jacobian = cv2.Rodrigues(rotation)
        return rmat, translation
    
    # get a marker's 2d rotation in a camera image
    def get_marker_rotation(self, id):
        with self.mutex_state:
            if not id in self.marker_state.keys():
                return None
            corners = self.marker_state[id].get_corners_smoothed()
        return self._calculate_aruco_marker_rotation(corners) / 360 * 2 * np.pi # degrees -> radians

    #von Vitus
    def _calculate_aruco_marker_rotation(self, aruco_marker_corners):
        tracker_point_one = aruco_marker_corners[0]
        tracker_point_two = aruco_marker_corners[1]
        vector_one = np.array([1, 0])
        vector_two = np.array([tracker_point_two[0] - tracker_point_one[0], tracker_point_two[1] - tracker_point_one[1]])

        angle = calculate_angle(vector_one, vector_two)
        return angle
    
    # nicht mehr von Vitus

    def get_marker_ids(self):
        with self.mutex_state:
            return self.marker_state.keys()

    def get_marker_data(self, id):
        with self.mutex_state:
            if id in self.marker_state.keys():
                return self.marker_state[id]
        
        
    def get_marker_missing_time(self, id):
        with self.mutex_state:
            if id in self.marker_state.keys():
                return self.marker_state[id].get_missing_time()


    # Continually update marker positions from a camera capture's frame
    def run_tracking(self, capture:CameraCapture):
        self.running = True
        self.capture:CameraCapture = capture
        while self.running:
            frame = capture.get_last_frame()
            if not type(frame) is np.ndarray:
                continue
            if not self.last_frame_timestamp:
                self.last_frame_timestamp = time.time()
            self.find_markers(frame)
            self.last_frame_timestamp = time.time()

    def stop_tracking(self):
        if self.running:
            self.running = False


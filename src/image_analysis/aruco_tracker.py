import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


import cv2
from cv2 import aruco
import numpy as np
from image_analysis.camera_capture import CameraCapture
import time
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from util.constants import ARUCO_DEFAULT_LENGTH

# detects 4X4 Aruco markers using OpenCVs built-in solution.
class ArucoTracker(MarkerTracker):
    
    def __init__(self, predefined_marker_lengths=dict([])):
        super().__init__(predefined_marker_lengths)
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)        
        self.aruco_parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_parameters)


    # finds markers in frame and updates their position
    def find_markers(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = self.detector.detectMarkers(gray)

        deltatime = time.time() - self.last_frame_timestamp

        if not ids is None:
            detected_ids = ids.flatten()
            for i, id in enumerate(ids[0]):
                # If not detected before, add new marker to the list
                if not id in self.marker_state.keys():
                    self.marker_state[id] = MarkerData(id)
                    if id in self.marker_lengths.keys():
                        self.marker_state[id].set_length(self.marker_lengths[id])
                    else:
                        self.marker_state[id].set_length(ARUCO_DEFAULT_LENGTH)
                
                # update marker
                self.marker_state[id].reset_missing_time()
                self.marker_state[id].update_corners(corners[i][0])

            # update missing time for markers that were not found
            for marker_id in list(self.marker_state):
                if marker_id not in detected_ids:
                    self.marker_state[marker_id].add_to_missing_time(deltatime)
            
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        else: # update missing time for all markers
            for marker_id in list(self.marker_state):
                self.marker_state[marker_id].add_to_missing_time(deltatime)
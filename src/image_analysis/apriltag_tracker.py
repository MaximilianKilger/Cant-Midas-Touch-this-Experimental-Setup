import pyapriltags as april
import cv2
from image_analysis.camera_capture import CameraCapture
import time
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from util.constants import APRIL_FAMILIES, APRIL_DEFAULT_LENGTH, APRIL_MAX_HAMMING, APRIL_MIN_DECISION_MARGIN
import numpy as np

# tracks apriltags using the pyapriltags library.
class ApriltagTracker (MarkerTracker):

    def __init__ (self, predefined_marker_lengths=dict([])):
        super().__init__(predefined_marker_lengths)
        self.detector = april.Detector(APRIL_FAMILIES)
        
    def find_markers(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect markers
        tags = self.detector.detect(gray)
        # update deltatime
        deltatime = time.time() - self.last_frame_timestamp
        ids = []
        for tag in tags:
            # threshold hamming distance of a Tag
            if tag.hamming > APRIL_MAX_HAMMING:
                continue
            id = tag.tag_id
            if tag.decision_margin < APRIL_MIN_DECISION_MARGIN:
                continue
            ids.append(id)
            with self.mutex_state:    
                # if marker has not been detected before, add it to the list
                if not id in self.marker_state.keys():
                    self.marker_state[id] = MarkerData(id)
                    if id in self.marker_lengths.keys():
                        self.marker_state[id].set_length(self.marker_lengths[id])
                    else:
                        self.marker_state[id].set_length(APRIL_DEFAULT_LENGTH)
                # reset missing time, now that we have confirmation that this marker still exists
                self.marker_state[id].reset_missing_time()
                
                corners = np.roll(np.flip(tag.corners, axis=0), -1, axis=0) #pyapriltags returns the marker corners in anticlockwise order. MarkerTracker is based on CV2s Aruco detection, which returns corners in clockwise order, so we need to reverse it. np.roll() brings the upper left corner back to index 0.        
                
                self.marker_state[id].update_corners(corners)
            id = None
        for recorded_id in self.marker_state.keys():
            
            if not ids is None:
                if recorded_id in ids:
                    continue 
            with self.mutex_state:
                # update missing time to undetected markers
                self.marker_state[recorded_id].add_to_missing_time(deltatime)
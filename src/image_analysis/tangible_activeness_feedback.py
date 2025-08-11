import numpy as np
import cv2
import configparser

from controls.opportunistic_control import OpportunisticControl
from image_analysis.video_source import VideoSource
from .marker_tracker import MarkerData, MarkerTracker
from util.util import parse_tuple_notation
from util.constants import *
from collections import deque

import time

# draws circles around active tangibles as feedback.
# outputs a frame that is intended to be projected onto the table.
class ActivenessFeedback(VideoSource):

    # @param controls: A dictionary of the opportunistic controls. key is the id of the marker it uses.
    # @param offsets: A dict of the geometric center points of the tangibles in relation to the centerpoint of its marker
    # @param radii: A dict of the intended radius of the projected circle around a tangible. 
    def __init__(self, width, height, controls:dict[OpportunisticControl], offsets:dict,radii:dict[float], marker_tracker:MarkerTracker, config_filepath:str):
        super().__init__(width,height)
        self.controls:dict[OpportunisticControl] = controls
        self.offsets = offsets
        self.radii:dict[float] = radii
        self.marker_tracker:MarkerTracker = marker_tracker
        ## Read the config file
        self.config = configparser.ConfigParser()
        self.config.read(config_filepath)
        self.calculate_procam_homography()
        self.frame = np.array([[[]]])
        self.projection_master = np.zeros((self.height, self.width, 3))
        #self.setup_window()

    def toggle_window_fullscreen(self):
        if self.window_small:
            cv2.setWindowProperty(FEEDBACK_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(FEEDBACK_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    # reads the pixel coordinates of the projector's image in the camera frame 
    # and computes a homography matrix between the two coordinate systems
    def calculate_procam_homography(self):
        projector_corner_points = np.array([
            [0,0],
            [0, self.height],
            [self.width, self.height],
            [self.width, 0]
        ])
        camera_corner_points = np.array([
            parse_tuple_notation(self.config[PROCAM_SETUP]['cornertopleft']),
            parse_tuple_notation(self.config[PROCAM_SETUP]['cornerbottomleft']),
            parse_tuple_notation(self.config[PROCAM_SETUP]['cornerbottomright']),
            parse_tuple_notation(self.config[PROCAM_SETUP]['cornertopright'])
        ]).astype(int)
        self.homography, _ = cv2.findHomography(camera_corner_points, projector_corner_points)

    # draw all feedback circles
    def project_feedback(self):
        # initialize output frame
        projection = np.zeros((self.height, self.width, 3))
        for id in self.controls.keys():
            if self.controls[id].isActive(): # find all active controls
                if id in self.marker_tracker.get_marker_ids():
                    if self.marker_tracker.get_marker_missing_time(id) > MARKER_MAX_TIME_MISSING:
                        continue
                    # get center point of a marker in the projector's image
                    center_x, center_y = self.calculate_center_point(id)
                    
                    if center_x is None:
                        continue
                    radius = self.radii[id]
                    # draw a circle around that point
                    cv2.circle(projection, (center_x, center_y), radius=radius, color=FEEDBACK_CIRCLE_COLOR, thickness=FEEDBACK_CIRCLE_THICKNESS)
                    center_x, center_y = None, None




        self.frame = projection

    # uses corners of a marker to calculate the position of its centerpoint (with offset) in the projector's image.
    def calculate_center_point(self, id):
        # get a homography matrix between marker space and camera space
        marker_cam_homography = self.get_marker_homography(id)
        if marker_cam_homography is None:
            return None, None
        # get center point at (0,0) + offset and convert into a format that OpenCV accepts
        center_point = np.array(self.offsets[id])[np.newaxis][np.newaxis].astype(np.float64)
        
        #transform center point of the marker into the camera image
        center_point_cam = cv2.perspectiveTransform(center_point,marker_cam_homography)
        # apply a correction for the perspective offset when the marker is outside the projection surface
        if id in FEEDBACK_PERSPECTIVE_CORRECTIONS.keys():
            center_point_cam -= np.array(CAM_CENTER)
            center_point_cam = center_point_cam * np.array(FEEDBACK_PERSPECTIVE_CORRECTIONS[id])
            center_point_cam += np.array(CAM_CENTER)
        # transform the center point from the camera's image coordinates to the projector's image coordinates
        center_point_proj = cv2.perspectiveTransform(center_point_cam, self.homography).flatten()

        return tuple(center_point_proj.astype(int))
    
    # calculates the homography between two coordinate systems:
    # a 2d real-world coordinate system centered on a marker with a given id
    # and the pixel coordinate system of the camera's frame.
    def get_marker_homography(self, id):
        # from the size of a marker, calculate the location of its corners in marker coordinates
        marker_size = self.marker_tracker.get_marker_data(id).get_length()
        object_points = np.array([
            [-marker_size/2, -marker_size/2],
            [-marker_size/2,  marker_size/2],
            [ marker_size/2,  marker_size/2],
            [ marker_size/2, -marker_size/2]
        ])
        # fetch the location of the marker corners in image coordinates
        marker_corners = self.marker_tracker.get_marker_data(id).get_corners_smoothed()
        if marker_corners is None or marker_corners is np.nan:
            return
        # find the homography matrix that transforms points between those two coordinate systems
        homography, ret = cv2.findHomography(object_points, marker_corners)
        
        return homography
    
    def get_last_frame(self):
        return self.frame

    def run(self):
        self.running = True

        while self.running:
            self.project_feedback()
            
    def stop(self):
        self.running = False
        
        
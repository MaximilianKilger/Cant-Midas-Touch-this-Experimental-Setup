import numpy as np
import cv2
import configparser

from controls.opportunistic_control import OpportunisticControl
from image_analysis.video_source import VideoSource
from .marker_tracker import MarkerData, MarkerTracker
from util.util import parse_tuple_notation
from util.constants import MARKER_MAX_TIME_MISSING, FEEDBACK_PERSPECTIVE_CORRECTIONS, CAM_CENTER
from collections import deque

import time

FEEDBACK_CIRCLE_THICKNESS = 25
FEEDBACK_CIRCLE_COLOR = (0.5,0.5,0.5)
FEEDBACK_WINDOW = "Feedback"
PROCAM_SETUP = "1.103_dev_setup"

# TODO (when publishing the code): Refactor caffeinated, well rested and without a headache.
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
        ## Do stuff with the file path. 
        self.config = configparser.ConfigParser()
        self.config.read(config_filepath)
        self.calculate_procam_homography()
        self.frame = np.array([[[]]])
        self.projection_master = np.zeros((self.height, self.width, 3))
        #self.setup_window()

        
     
    #def setup_window(self):
    #    self.window_small = True
    #    cv2.namedWindow(FEEDBACK_WINDOW)
    #    cv2.setWindowProperty(FEEDBACK_WINDOW, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)

    def toggle_window_fullscreen(self):
        if self.window_small:
            cv2.setWindowProperty(FEEDBACK_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(FEEDBACK_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

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

    def project_feedback(self):
        #projection = self.projection_master.copy()
        projection = np.zeros((self.height, self.width, 3))
        for id in self.controls.keys():
            #print(id, " active? ", self.controls[id].isActive())
            if self.controls[id].isActive():
                if type(id) == int:
                    if id in self.marker_tracker.get_marker_ids():
                        if self.marker_tracker.get_marker_missing_time(id) > MARKER_MAX_TIME_MISSING:
                            continue
                        center_x, center_y = self.calculate_center_point(id)
                        #print("2 with id",id,":",center_x, "|" ,center_y)
                        if center_x is None:
                            continue

                        radius = self.radii[id]
                        
                        cv2.circle(projection, (center_x, center_y), radius=radius, color=FEEDBACK_CIRCLE_COLOR, thickness=FEEDBACK_CIRCLE_THICKNESS)
                        center_x, center_y = None, None
                if type(id) == str:
                    ids = parse_tuple_notation(id)
                    if ids is None:
                        continue
                    centers = []

                    for part_id in ids:
                        part_id = int(part_id)
                        if part_id in self.marker_tracker.get_marker_ids():
                            
                            if not self.marker_tracker.get_marker_missing_time(part_id) is None:
                                if self.marker_tracker.get_marker_missing_time(part_id) > MARKER_MAX_TIME_MISSING:
                                    continue
                            marker_data = self.marker_tracker.get_marker_data(part_id)
                            if marker_data is None:
                                continue
                            corners = marker_data.get_corners_smoothed()
                            center = np.mean(corners, axis=0)
                            centers.append(center)
                    if len(centers) <= 0:
                        continue
                    center_point_cam = np.mean(np.array(centers), axis=0)[np.newaxis][np.newaxis]
                    
                    center_point_proj = cv2.perspectiveTransform(center_point_cam, self.homography)
                    
                    radius = self.radii[id]
                    cv2.circle(projection, center_point_proj.astype(int).flatten(), radius=radius, color=FEEDBACK_CIRCLE_COLOR, thickness=FEEDBACK_CIRCLE_THICKNESS)




        self.frame = projection


    def calculate_center_point(self, id):
        marker_cam_homography = self.get_marker_homography(id)
        if marker_cam_homography is None:
            return None, None
        center_point = np.array(self.offsets[id])[np.newaxis][np.newaxis].astype(np.float64)
        #calculate center point of the marker in the camera image
        center_point_cam = cv2.perspectiveTransform(center_point,marker_cam_homography)
        if id in FEEDBACK_PERSPECTIVE_CORRECTIONS.keys():
            center_point_cam -= np.array(CAM_CENTER)
            center_point_cam = center_point_cam * np.array(FEEDBACK_PERSPECTIVE_CORRECTIONS[id])
            center_point_cam += np.array(CAM_CENTER)
        #center_point_proj = center_point_cam
        center_point_proj = cv2.perspectiveTransform(center_point_cam, self.homography).flatten()

        #print("l81 for", id, ":", center_point_proj)
        return tuple(center_point_proj.astype(int))
    
    def get_marker_homography(self, id):
        marker_size = self.marker_tracker.get_marker_data(id).get_length()
        object_points = np.array([
            [-marker_size/2, -marker_size/2],
            [-marker_size/2,  marker_size/2],
            [ marker_size/2,  marker_size/2],
            [ marker_size/2, -marker_size/2]
        ])
        marker_corners = self.marker_tracker.get_marker_data(id).get_corners_smoothed()
        #print(marker_corners)
        if marker_corners is None or marker_corners is np.nan:
            return
        #print("l95 marker corners", marker_corners)
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
        
        
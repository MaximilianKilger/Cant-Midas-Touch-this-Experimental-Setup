import numpy as np
import cv2
import json
from matplotlib.path import Path

from controls.valuator_2d import Valuator2D
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from image_analysis.hand_tracker import HandTracker, HandLandmarkID
from util.util import is_iterable

class FingerSlider2d (Valuator2D):
    
    def __init__(self, marker_tracker, hand_tracker, marker_id, boundary_points):
        self.marker_tracker:MarkerTracker = marker_tracker
        self.hand_tracker:HandTracker = hand_tracker
        self.marker_id = marker_id
        self.deactivate()
        
        print(boundary_points)
        print(type(boundary_points))
        if type(boundary_points) == str:
            print("received filepath", boundary_points)
            with open(boundary_points) as fhandle:
                self.boundary_points = json.loads(fhandle.read())
                print(self.boundary_points)

        elif is_iterable(boundary_points):
            self.boundary_points = boundary_points
        

        self.warped_boundaries = None # Nur für debugs


    def get_marker_homography (self):
        marker_size = self.marker_tracker.get_marker_data(self.marker_id).get_length()
        object_points = np.array([
            [-marker_size/2, -marker_size/2],
            [-marker_size/2,  marker_size/2],
            [ marker_size/2,  marker_size/2],
            [ marker_size/2, -marker_size/2]
        ])
        marker_corners = self.marker_tracker.get_marker_data(self.marker_id).get_corners_smoothed()
        #print("marker_corners: ", marker_corners)
        homography, ret = cv2.findHomography(object_points, marker_corners)
        
        
        return homography
    
    def check_fingertip_in_boundaries(self, fingertip_coords, boundaries):
        
        polygon = Path(boundaries)
        #return x <= fingertip_coords[0] <= x + w and y <= fingertip_coords[1] <= y + h
        return polygon.contains_point(fingertip_coords)
    
    def normalize_position(self, fingertip_coords):
        xcoords = np.array(self.boundary_points)[:,0]
        ycoords = np.array(self.boundary_points)[:,1]
        
        max_x = np.max(xcoords)
        min_x = np.min(xcoords)
        max_y = np.max(ycoords)
        min_y = np.min(ycoords)

        norm_x = (fingertip_coords[0] - min_x) / (max_x - min_x)
        norm_y = (fingertip_coords[1] - min_y) / (max_y - min_y)

        return norm_x, norm_y

    def getValue(self):
        #print(self.marker_tracker.get_marker_ids())
        if not self.isActive():
            return
        if self.marker_tracker.get_marker_data(self.marker_id) is None:
            return None
        homography = self.get_marker_homography()
        #print("boundaries: ", self.boundary_points)
        #print("matrix: ", homography)
        fingertips = self.hand_tracker.findFingertips(HandLandmarkID.INDEX_FINGER_TIP.value)
        #print("Fingertips", fingertips)
        if len(fingertips) == 0:
            return None 
        
        self.warped_boundaries = cv2.perspectiveTransform(np.array([self.boundary_points]), homography)
        warped_fingertips = cv2.perspectiveTransform(np.array([fingertips]).astype(np.float32), np.linalg.inv(homography))
        #print(warped_fingertips)
        for fingertip in warped_fingertips[0]:
            if self.check_fingertip_in_boundaries(fingertip, self.boundary_points):
                return self.normalize_position(fingertip)
            
        return None, None
                
                

    
        


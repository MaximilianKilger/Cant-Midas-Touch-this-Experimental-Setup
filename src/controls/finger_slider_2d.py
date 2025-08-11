import numpy as np
import cv2
import json
from matplotlib.path import Path

from controls.valuator_2d import Valuator2D
from image_analysis.marker_tracker import MarkerData, MarkerTracker
from image_analysis.hand_tracker import HandTracker, HandLandmarkID
from util.util import is_iterable

# returns a 2d output based on the position of a fingertip in a rectangle marked with a fiducial marker
class FingerSlider2d (Valuator2D):
    
    # @paramn marker_id:    id of the fiducial marker used to track this tangible.
    # @param boundary_points:   either a filepath to a json file with points, or directly an iterable of points.
    #                           these points mark the boundary of the interactable surface, in coordinates relative to the marker.
    def __init__(self, marker_tracker, hand_tracker, marker_id, boundary_points):
        self.marker_tracker:MarkerTracker = marker_tracker
        self.hand_tracker:HandTracker = hand_tracker
        self.marker_id = marker_id
        self.deactivate()
        
        # if given a filepath, load the boundary from a file
        if type(boundary_points) == str:
            with open(boundary_points) as fhandle:
                self.boundary_points = json.loads(fhandle.read())
                
        elif is_iterable(boundary_points):
            self.boundary_points = boundary_points
        


    # computes homography matrix between pixel coordinates in the camera image and a coordinate system centered on the marker
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
        return polygon.contains_point(fingertip_coords)
    
    # given the coordinates of the fingertip relative to the marker, 
    # normalizes the coordinates to the bounding box of the trackpad boundaries.
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
        if not self.isActive():
            return
        if self.marker_tracker.get_marker_data(self.marker_id) is None:
            return None
        homography = self.get_marker_homography()
        
        fingertips = self.hand_tracker.findFingertips(HandLandmarkID.INDEX_FINGER_TIP.value)
        
        if len(fingertips) == 0:
            return None 
        
        # transform fingertip position from image coordinates to marker coordinates.
        warped_fingertips = cv2.perspectiveTransform(np.array([fingertips]).astype(np.float32), np.linalg.inv(homography))
        
        for fingertip in warped_fingertips[0]:
            if self.check_fingertip_in_boundaries(fingertip, self.boundary_points):
                return self.normalize_position(fingertip)
            
        return None, None
                
                

    
        


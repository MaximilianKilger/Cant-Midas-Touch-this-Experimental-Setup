import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from matplotlib.path import Path
from image_analysis.hand_tracker import HandTracker
from image_analysis.aruco_tracker import ArucoTracker
from image_analysis.camera_capture import CameraCapture
from util.util import polar2cartesian
from util.constants import CALIBRATION_FILEPATH
import threading
import cv2
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d

# Brauchen wir vorerst nicht

class TouchButton:

    def __init__(self, handTracker, arucoTracker, marker_id=42):
        self.handTracker = handTracker
        self.arucoTracker = arucoTracker
        self.marker_id = marker_id
        self.boundaries = None  
        self.color_bounds = None
    
    def getFingertipPosition(self, frame, handNo=0):
        fingerPosition = self.handTracker.findHands(frame, draw=False)
        print("Fingerposition ", fingerPosition)
        return self.handTracker.findFingertips(img=frame, handNo=handNo)

#    def setBoundaries(self, frame):
#        marker_data = self.arucoTracker.get_marker_data(self.marker_id)
#        if marker_data:
#            marker_corners = marker_data.get_corners()
#            if marker_corners is not None:
#                self.boundaries = cv2.boundingRect(marker_corners)
#                
#                # Boundaries mit expand_boundaries_with_edges erweitern
#                expanded_boundaries = self.expand_boundaries_with_edges(frame)
#                if expanded_boundaries is not None:
#                    self.boundaries = expanded_boundaries
#        
#        print("Updated Boundaries with Edge Detection and Padding: ", self.boundaries)


    def setBoundaries(self, frame=None):
            marker_data = self.arucoTracker.get_marker_data(self.marker_id)
            if marker_data:
                marker_corners = marker_data.get_corners().astype(int)
                rotation_matrix , translation_vector= self.arucoTracker.get_marker_transformation(self.marker_id)

                rotation_matrix, _ = cv2.Rodrigues(rotation_matrix)
                mtx, dist = self.arucoTracker.capture.get_calibration()
                
                

                print("Marker corners: ", marker_corners)

                if marker_corners is not None:

                    #self.boundaries = cv2.boundingRect(marker_corners)
                    #marker_corners = np.array(marker_corners, dtype=np.int32)

                    x_marker = int(marker_corners[:, 0].mean())
                    y_marker = int(marker_corners[:, 1].mean())
                    marker_center = (x_marker, y_marker)

                    distances_cm = {

                        "top" : 700 , #13.9,
                        "bottom" : 700,#12.9,
                        "right" : 500,#9.4,
                        "left" : 500#8.9
                    }

                    top = float(y_marker + distances_cm["top"])
                    bottom =float(y_marker + distances_cm["bottom"])
                    right = float(x_marker + distances_cm["right"])
                    left = float(x_marker + distances_cm["left"])

                    self.boundaries = (left, top, right - left, bottom - top)

                    self.paper_corners = np.array([
                        (left, top, 0),
                        (right, top, 0),
                        (right, bottom,0),
                        (left, bottom, 0)
                    ]).astype(np.float32)


                    imagePoints, jacobian = cv2.projectPoints(self.paper_corners, rotation_matrix, translation_vector, mtx, dist)
                    imagePoints = imagePoints.reshape((len(imagePoints), 2)).astype(int)
                    print("ImgPoints", imagePoints)
                    if frame:
                        for i in range(len(imagePoints)):
                            start_point = tuple(imagePoints[i])
                            end_point = tuple(imagePoints[(i + 1) % len(imagePoints)])
                            cv2.line(frame, start_point, end_point, (0, 255, 0), 2)

                    self.boundaries = imagePoints

                    """"
                    roi = frame[y:y+h, x:x+w]
                    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)#

                    marker_mask = np.zeros(roi.shape).astype(np.uint8)+255
                    print(marker_mask.shape)
                    cv2.polylines(marker_mask, marker_corners, True, (0, 0, 0))
                    marker_mask = cv2.cvtColor(marker_mask, cv2.COLOR_BGR2GRAY)
                    mean_color = cv2.mean(roi_hsv, marker_mask)[:3]

                    lower_bound = np.array ([max(0, mean_color[0] - 20), max(0, mean_color[1] -80), max(0, mean_color[2] -80)])
                    upper_bound = np.array([min(255, mean_color[0] + 20), min(255, mean_color[1] + 80), min(255, mean_color[2] + 80)])

                    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
                    polar_center =  marker_corners[0].mean(axis=0)
                    mask = cv2.warpPolar(mask, mask.shape,polar_center, mask.shape[0]/2, cv2.INTER_LINEAR)
                    cv2.imshow("MASKE: ", mask)

                    # Konturen in der Maske finden
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if contours:
                        # Größte Kontur finden und Boundaries erweitern
                        largest_contour = max(contours, key=cv2.contourArea)
                        print("largest contour", largest_contour)
                        largest_contour = np.apply_along_axis(lambda point:polar2cartesian(point, polar_center), 0, largest_contour).astype(int)
                        x_contour, y_contour, w_contour, h_contour = cv2.boundingRect(largest_contour)

                        # Erweiterte Boundaries um den Marker
                        padding = 50  
                        self.boundaries = (
                            max(0, x_contour - padding),
                            max(0, y_contour - padding),
                            min(frame.shape[1], w_contour + 2 * padding),
                            min(frame.shape[0], h_contour + 2 * padding)
                        )"""
                    
            print("Updated Boundaries with color similarity and padding: ", self.boundaries)



    def getMarkerPosition(self, frame=None):
        marker_data = self.arucoTracker.get_marker_data(self.marker_id)
        if marker_data:
            return marker_data.get_corners()
        
        print("MarkerPosition ", marker_data)
        return None

    def isFingertipInsideBoundaries(self, fingertip_coords):
        if self.boundaries is None:
            return False
        #x, y, w, h = self.boundaries

        print("Finger in Boundary ", fingertip_coords)
        polygon = Path(self.boundaries)
        #return x <= fingertip_coords[0] <= x + w and y <= fingertip_coords[1] <= y + h
        return polygon.contains_point(fingertip_coords)


#    def detectObject(self, frame):
#        if self.boundaries is None:
#            return None
#        x, y, w, h = self.boundaries
#        roi = frame[y:y+h, x:x+w]
        # Detect corners in ROI
#        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#        edges = cv2.Canny(gray, 100, 200)
#
#        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#        if contours:
#            largest_contour = max(contours, key=cv2.contourArea)
#            # Adjust contour coordinates
#            for point in largest_contour:
#                point[0][0] += x
#                point[0][1] += y
#            return largest_contour
#        return None

    # apparently unused
    def expand_boundaries_with_edges(self, frame):
        if self.boundaries is None:
            return None
            
        x, y, w, h = self.boundaries
        padding = 50  # ROI erweitern
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2 * padding)
        h = min(frame.shape[0] - y, h + 2 * padding)

        roi = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

            # Konturen finden
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Größte Kontur relativ zur ROI finden
            largest_contour = max(contours, key=cv2.contourArea)
            for point in largest_contour:
                point[0][0] += x
                point[0][1] += y
            return cv2.boundingRect(largest_contour)
            
        return self.boundaries

    def getState(self):
        self.setBoundaries()
        
        fingertips = self.getFingertipPosition()
        #for fingertip_id, coords in fingertips.items():
        #    cv2.circle(frame, (coords[1], coords[2]), 5, (0, 255, 0), -1)  
        #    if button.isFingertipInsideBoundaries((coords[1], coords[2])):
        #        cv2.putText(frame, "Touch Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #        print("Marker touched!")



#Test
def main():
    capture = CameraCapture(0, calibration_filepath="../util/Logitech BRIO 0.yml")
    
    hand_tracker = HandTracker()
    aruco_tracker = ArucoTracker()
    button = TouchButton(hand_tracker, aruco_tracker)
    aruco_thread = threading.Thread(target=lambda: aruco_tracker.run_tracking(capture))
    aruco_thread.start()

    capture_thread = threading.Thread(target=capture.run)
    capture_thread.start()

    while True:
        frame = capture.get_last_frame()
        if frame is None:
            continue

        # Aktualisieren der Boundaries
        button.setBoundaries(frame)

        # Zeichnen der Boundaries auf dem Frame
        #if button.boundaries:
        #    x, y, w, h = button.boundaries
        #    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Erkennung und Interaktion
        fingertips = button.getFingertipPosition(frame)
        for fingertip_id, coords in fingertips.items():
            cv2.circle(frame, (coords[1], coords[2]), 5, (0, 255, 0), -1)  
            if button.isFingertipInsideBoundaries((coords[1], coords[2])):
                cv2.putText(frame, "Touch Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print("Marker touched!")

        # Position des Markers anzeigen
        marker_position = button.getMarkerPosition(frame)
        if marker_position is not None:
            for i in range(len(marker_position[0])):
                start_point = marker_position[0][i]
                end_point = marker_position[0][(i + 1) % len(marker_position[0])]
                cv2.line(frame, start_point.astype(int), end_point.astype(int), (255, 0, 0), 2)

        # Frame anzeigen
        cv2.imshow("Touch Button", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.stop()
    aruco_tracker.stop_tracking()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

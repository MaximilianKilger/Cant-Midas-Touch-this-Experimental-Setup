import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import cv2
import numpy as np
import mediapipe as mp
import time
from enum import Enum

import inspect

from image_analysis.camera_capture import CameraCapture


class HandLandmarkID(Enum):
    WRIST = 0
    THUMB_TIP = 4
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_TIP = 16
    PINKY_TIP = 20

#Evtl z Koordinaten?

class HandTracker:

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)
        self.results = None

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
    
    def run_tracking(self, capture:CameraCapture):
        self.capture = capture
        self.running = True
        while self.running:
            frame = capture.get_last_frame()
            if not type(frame) is np.ndarray:
                continue
            self.findHands(frame, draw=False)

    def stop_tracking(self):
        self.running = False

    def findHands(self, img, draw=False):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        self.frame_width, self.frame_height, channels = img.shape

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img=None, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                if not img is None:
                    h, w, c = img.shape
                else:
                    h, w = self.frame_width, self.frame_height
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
                if draw and not img is None:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
        return lmlist

    def get_number_of_hands(self):
        if self.results is None:
            return 0
        if self.results.multi_handedness is None:
            return 0
        return len(self.results.multi_handedness)

    def findFingertips(self, landmark_id=None, handNo=None, img=None, draw=True):
        hand_indices = [handNo]
        
        #print(f"we have {self.get_number_of_hands()} hands here" )
        if handNo is None:
            hand_indices = range(self.get_number_of_hands())

        results = []
        # ('multi_hand_landmarks', 'multi_hand_world_landmarks', 'multi_handedness')
        for i in hand_indices:
            fingertips = {}
            lmlist = self.findPosition(img=img, handNo=i, draw=False) 
            fingertips_ids = [4, 8, 12, 16, 20]

            for id in fingertips_ids:
                if id < len(lmlist):
                    fingertips[id] = lmlist[id]  
                    if draw and not img is None:
                        cv2.circle(img, (lmlist[id][1], lmlist[id][2]), 10, (0, 255, 0), cv2.FILLED)
            #print("fingertips id ", i, ":",fingertips)
            if landmark_id is None:
                results.append(fingertips[1:])
            else:
                results.append(fingertips[landmark_id][1:])
        #print("Fingertipresults ",results)
        if handNo is None:
            return results
        else:
            return results[0]


#Testing
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = HandTracker()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        fingertips = detector.findFingertips(img = img)

        if fingertips:
            print(f"Fingertips: {fingertips}")

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()

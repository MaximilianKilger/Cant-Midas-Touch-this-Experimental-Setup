import numpy as np

# Configurations for both modalities of marker trackers
BUFFERED_MARKER_CORNERS = 5 #size of the rolling window saving marker positions over multiple frames.
MARKER_MAX_TIME_MISSING = 1.2 #time until a missing marker is considered inactive

# Configurations for ArucoTracker
ARUCO_DEFAULT_LENGTH = 4.1

#Configurations for ApriltagTracker
APRIL_FAMILIES = "tag16h5"
APRIL_DEFAULT_LENGTH = 2.66
APRIL_MAX_HAMMING = 0
APRIL_MIN_DECISION_MARGIN = 24

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

FPS = 60

#Zoom Speed for Task2
ZOOM_SPEED = 30

# Configurations for Rotation Valuator

# if the tangible's difference in rotation between two frames is bigger than this threshold, it probably looped back around.
MIN_SKIPPABLE_ROTATION = 0.75 # as a fraction of a full rotation, e.g. 1.0 = 360°


ROTATOR_MARKER_ID = 9
TRACKPAD_MARKER_ID = 8
        
PAGETURNER_MARKER_IDS = {5:0,
                        6:1,
                        7:2}

HIGHLIGHTER_MARKER_ID = 1
SCISSORS_MARKER_ID = 2
GLUE_MARKER_ID = 4
STAPLER_MARKER_ID = 0
ERASER_MARKER_ID = 3


# Configurations for projector output
PROJECTOR_WIDTH = 1920#3840
PROJECTOR_HEIGHT = 1080#2160

FEEDBACK_BUFFERED_CENTER_POSITIONS = 1

FEEDBACK_OFFSETS = {
    ROTATOR_MARKER_ID: (0,0),
    5: (8.125,12.4),
    "(14,5)": (8.125,12.4),
    6: (8.125,12.4),
    "(13,6)": (8.125,12.4),
    7: (8.125,12.4),
    "(16,7)": (8.125,12.4),
    TRACKPAD_MARKER_ID: (-10.1,12.5),
    HIGHLIGHTER_MARKER_ID: (0,0),
    SCISSORS_MARKER_ID: (0,0),
    GLUE_MARKER_ID: (0,0),
    STAPLER_MARKER_ID: (0,0),
    ERASER_MARKER_ID: (0,0)
}

FEEDBACK_RADII = {
    #26: 200,
   ROTATOR_MARKER_ID: 100,
    5: 100,
    "(14,5)": 100,
    6: 100,
    "(13,6)":100,
    7: 100,
    "(16,7)": 100,
    TRACKPAD_MARKER_ID: 220,
    f"({TRACKPAD_MARKER_ID}, 15)":220,
    HIGHLIGHTER_MARKER_ID: 100,
    SCISSORS_MARKER_ID: 150,
    GLUE_MARKER_ID: 100,
    STAPLER_MARKER_ID: 100,
    ERASER_MARKER_ID: 100
}

FEEDBACK_PERSPECTIVE_CORRECTIONS = {
    ROTATOR_MARKER_ID: (0.75, 0.8)
}
CAM_CENTER = (905, 553)

CAMERA_ID = 0
CONTROL_UPDATE_FREQUENCY_HZ = 120

PEDAL_DELAY_MEAN_SECONDS = 0.5
PEDAL_DELAY_STANDARD_DEVIATION_SECONDS = 0.08

SLIDESHOW_MARK_OPACITY = 0.7
SLIDESHOW_STARTING_ZOOM_FACTOR = 1.25

MAX_ZOOM_FACTOR = 5
MIN_ZOOM_FACTOR = 1

MARK_COLOR = (0, 0, 240)
MARK_RADIUS_TO_VIEWPORT = 0.5
MARK_THICKNESS_TO_RADIUS = 0.1

FULLSCREEN_WINDOW_WIDTH = 1920
FULLSCREEN_WINDOW_HEIGHT = 1080
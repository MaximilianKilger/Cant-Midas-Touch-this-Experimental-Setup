import time
from controls.state_selector import StateSelector
from image_analysis.marker_tracker import MarkerTracker
from util.constants import MARKER_MAX_TIME_MISSING

# Tracks several markers and outputs a state based on the current visible marker.
# Assumes that markers are installed so that only one is visible at a time,
# such as on different pages of the same book or two sides of the same card.
class MarkerVisibility(StateSelector):
    def __init__(self, marker_tracker:MarkerTracker, state_to_marker_map):
        super().__init__(False, state_to_marker_map.keys())
        self.marker_tracker = marker_tracker
        # dict mapping marker ids (key) to the state associated with a marker (value)
        self.state_marker_map:dict = state_to_marker_map
        self.active_marker = None
        # cooldown time after state change to prevent "bouncing" between two different stage when two markers are briefly visible at once
        self.debounce_time = 1.0
        self.last_change_time = time.time()
        self.state = None
        self.deactivate()

    # update internal state based on markers detected by the marker tracker
    def update(self):
        if not self.isActive():
            return
        visible_marker_ids = [
            marker_id for marker_id in self.marker_tracker.get_marker_ids()
            
        ]

        if not visible_marker_ids:
            return

        for current_marker in visible_marker_ids:
            # check if marker has not been missing
            if self.marker_tracker.get_marker_missing_time(current_marker) >= MARKER_MAX_TIME_MISSING:
                continue
            # check conditions to induce state change
            if current_marker != self.active_marker and current_marker in self.state_marker_map.keys() and time.time() - self.last_change_time > self.debounce_time:
                self.last_change_time = time.time()
                
                self.activate_marker = current_marker
                # change internal state based on current marker
                self.state = self.state_marker_map[current_marker]
                break

    def getState(self):
        self.update()
        return self.state
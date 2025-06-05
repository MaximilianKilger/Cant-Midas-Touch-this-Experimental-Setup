import os
import time
import win32gui
import win32con
from .opportunistic_control import OpportunisticControl
from controls.state_selector import StateSelector
from util.constants import MARKER_MAX_TIME_MISSING
#from .window_manager import WindowManager

class MarkerVisibility(StateSelector):
    def __init__(self, marker_tracker, state_to_marker_map):
        super().__init__(False, state_to_marker_map.keys())
        self.marker_tracker = marker_tracker
        self.state_marker_map:dict = state_to_marker_map
        #self.window_manager = WindowManager()
        self.active_marker = None
        self.debounce_time = 1.0
        self.last_change_time = time.time()
        self.state = None
        self.deactivate()

    def update(self):
        if not self.isActive():
            return
        visible_marker_ids = [
            marker_id for marker_id in self.marker_tracker.get_marker_ids()
            
        ]

        if not visible_marker_ids:
            return

        #current_marker = visible_marker_ids[0]
        #print(self.active_marker)
        for current_marker in visible_marker_ids:
            if self.marker_tracker.get_marker_missing_time(current_marker) >= MARKER_MAX_TIME_MISSING:
                continue
            if current_marker != self.active_marker and current_marker in self.state_marker_map.keys() and time.time() - self.last_change_time > self.debounce_time:
                self.last_change_time = time.time()
                #self.handle_marker(current_marker)
                self.activate_marker = current_marker
                #self.switch_to_marker(marker_id)
                self.state = self.state_marker_map[current_marker]
                break

    #def handle_marker(self, marker_id):
    #    if marker_id in self.state_marker_map.keys():
            

    #def switch_to_marker(self, marker_id):
    #    if self.active_marker and self.active_marker != marker_id:
    #        self.window_manager.minimize(self.active_marker)

    #    app_path = self.marker_app_map.get(marker_id)
    #    if marker_id in self.window_manager.window_handlers:
    #        self.window_manager.maximize(marker_id)
    #    else:
    #        self.window_manager.start_application(marker_id, app_path)

    #    self.active_marker = marker_id

    def getState(self):
        self.update()
        return self.state
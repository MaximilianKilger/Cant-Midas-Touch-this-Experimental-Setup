import pyautogui
import time
# Zur Aktivierung/Deaktivierung und Sperre evtl. noch einbauen
from .opportunistic_control import OpportunisticControl

class manualControls(OpportunisticControl):

    def __init__(self, function):
        super().__init__(False)
        self.function = function
    
    def trigger(self):
        if self.isActive():
            self.function()

import pyautogui
import time
# Zur Aktivierung/Deaktivierung und Sperre evtl. noch einbauen
from .opportunistic_control import OpportunisticControl

# Very simple control. Receives a function. 
# Can trigger the function, but only if the control is active.
# Ensures that functions that don't require tracking to be executed still follow the rules of other opportunistic controls with regards to clutching.
class manualControls(OpportunisticControl):

    def __init__(self, function):
        super().__init__(False)
        self.function = function
    
    def trigger(self):
        if self.isActive():
            self.function()


# Base Class for all controls used in the study.
# Only functionality at this point is that it can be activated or deactivated.
class OpportunisticControl:

    def __init__(self, active = True):
        self.active = active
    
    def activate(self):
        self.active = True
        return self.active
    
    def deactivate(self):
        self.active = False
        return self.active
    
    def isActive(self):
            return self.active


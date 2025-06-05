
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


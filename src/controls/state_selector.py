from controls.opportunistic_control import OpportunisticControl

# Base class for State selector-type controls.
# State selectors output one of several possible states depending on the tangible.
class StateSelector(OpportunisticControl):

    def __init__(self, active, states):
        super().__init__(active)
        self.states = states
    
    def getState(self):
        return
    
    def getPossibleStates(self):
        return self.states
        
from controls.opportunistic_control import OpportunisticControl


class StateSelector(OpportunisticControl):

    def __init__(self, active, states):
        super().__init__(active)
        self.states = states
    
    def getState(self):
        return
    
    def getPossibleStates(self):
        return self.states
        
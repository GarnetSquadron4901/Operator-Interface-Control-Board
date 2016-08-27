from ControlBoardApp.hal import ControlBoardBase

class Simulator(ControlBoardBase):
    NAME = 'Control Board Simulator'
    def __init__(self, debug):
        super(Simulator).__init__(debug)


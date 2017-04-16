import logging
import sys
logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.SimulatorBase import SimulatorBase, SimulatorFrame
else:
    # Test Mode
    from cbhal.SimulatorBase import SimulatorBase, SimulatorFrame

CB_SNAME = 'ControlBoard_1v1_Simulator'
CB_LNAME = 'Control Board v1.1 Simulator'


class HardwareAbstractionLayer(SimulatorBase):
    """
    Control Board 1v1 Simulator
    """

    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

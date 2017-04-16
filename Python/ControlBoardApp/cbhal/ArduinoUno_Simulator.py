import logging
import sys
logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.SimulatorBase import SimulatorBase, SimulatorFrame
else:
    # Test Mode
    from cbhal.SimulatorBase import SimulatorBase, SimulatorFrame

CB_SNAME = 'ArduinoUno_Simulator'
CB_LNAME = 'Arduino Uno Simulator'


class HardwareAbstractionLayer(SimulatorBase):
    """ Arduino Uno Simulator """

    LED_OUTPUTS = 4
    PWM_OUTPUTS = 1
    ANALOG_INPUTS = 6
    SWITCH_INPUTS = 6

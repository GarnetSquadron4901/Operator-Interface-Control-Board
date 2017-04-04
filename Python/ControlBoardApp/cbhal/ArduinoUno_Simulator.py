import logging
logger = logging.getLogger(__name__)

from ControlBoardApp.cbhal.SimulatorBase import SimulatorBase, SimulatorFrame


CB_SNAME = 'ArduinoUno_Simulator'
CB_LNAME = 'Arduino Uno Simulator'

class HardwareAbstractionLayer(SimulatorBase):

    LED_OUTPUTS = 4
    PWM_OUTPUTS = 1
    ANALOG_INPUTS = 6
    SWITCH_INPUTS = 6


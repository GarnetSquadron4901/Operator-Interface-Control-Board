import sys

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0
else:
    # Test Mode
    from cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0

CB_SNAME = 'ArduinoUno'
CB_LNAME = 'Arduino Uno'


class HardwareAbstractionLayer(ControlBoardSerialBaseFw1v0):
    """
    Arduino Uno HAL - Uses ControlBoardSerialBaseFw1v0
    """
    CB_LNAME = CB_LNAME
    CB_SNAME = CB_SNAME
    LED_OUTPUTS = 4
    PWM_OUTPUTS = 1
    ANALOG_INPUTS = 6
    SWITCH_INPUTS = 6

    # USB Identifiers
    PID = 67
    VID = 9025

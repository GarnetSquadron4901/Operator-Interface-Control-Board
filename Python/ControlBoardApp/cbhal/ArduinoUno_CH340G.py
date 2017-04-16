import sys

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0
else:
    # Test Mode
    from cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0

CB_SNAME = 'ArduinoUnoCH340G'
CB_LNAME = 'Arduino Uno Clone (w/ CH340G USB to Serial)'


class HardwareAbstractionLayer(ControlBoardSerialBaseFw1v0):
    """
    Arduino Uno Clone w/ CH340G USB to Serial HAL - Uses ControlBoardSerialBaseFw1v0
    """
    CB_LNAME = CB_LNAME
    CB_SNAME = CB_SNAME
    LED_OUTPUTS = 4
    PWM_OUTPUTS = 1
    ANALOG_INPUTS = 6
    SWITCH_INPUTS = 6

    PID = 29987
    VID = 6790

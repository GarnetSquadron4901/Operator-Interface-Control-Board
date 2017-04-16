import sys
if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0
else:
    # Test Mode
    from cbhal.ControlBoardSerialBaseFw1v0 import ControlBoardSerialBaseFw1v0

CB_SNAME = 'ControlBoard_1v1'
CB_LNAME = 'Control Board v1.1'


class HardwareAbstractionLayer(ControlBoardSerialBaseFw1v0):
    """
    ControlBoard_1v1 HAL - Uses ControlBoardSerialBase
    """
    CB_LNAME = CB_LNAME
    CB_SNAME = CB_SNAME
    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

    # USB Identifiers
    PID = 24577
    VID = 1027

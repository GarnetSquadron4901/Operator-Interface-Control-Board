import serial
import serial.tools.list_ports as lp
from crccheck.crc import Crc8Maxim
import wx
import threading
import numpy


class HAL:
    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

    def __init__(self, port_name='auto', speed=115200, timeout=1, PID=24577, VID=1027):


        self.timeout = timeout

        # If the port name is auto, find the control board by searching throughthe PID and VID
        if port_name == 'auto':
            port_names = [port.device for port in lp.comports() if port.pid == PID and port.vid == VID]
            if not any(port_names):
                raise serial.SerialException('No valid COM ports found for the control board. Is it connected?')
            elif len(port_names) > 1:
                # TODO: Handle multiple port_names
                port_name = port_names[0]
            else:
                port_name = port_names[0]

        self.port = serial.Serial(port=port_name, baudrate=speed, timeout=self.timeout)



        # Set up default variable
        self.led_out = None
        self.pwm_out = None
        self.analog_in = None
        self.switch_in = None
        self.reset_values()

    def reset_values(self):
        self.led_out = [False] * self.LED_OUTPUTS
        self.pwm_out = [0] * self.PWM_OUTPUTS
        self.analog_in = [0.0] * self.ANALOG_INPUTS
        self.switch_in = [False] * self.SWITCH_INPUTS


    def run(self):
        while self.port.is_open():
            pass

    def pack_data(self, led_array, pwm_array):

        # Make sure the data is the right length
        assert(len(pwm_array) == self.PWM_OUTPUTS, 'Length of PWM array is invalid')
        assert(len(led_array) == self.LED_OUTPUTS, 'Length of LED array is invalid')

        ###########################################
        # Convert the LED Boolean array to a string
        # 1. Convert LED boolean array to number
        led_u16 = 0x0000
        for led in led_array:
            led_u16 <<= 1
            led_u16 |= led
        # 2. Convert number to string
        led_string = str(led_u16)
        ###########################################

        ###########################################
        # Convert PWM Number array to a string
        pwm_string = str(pwm_array).strip('[]').replace(' ', '')
        ###########################################

        # Combine the data together for CRC processing
        data_out = 'LED:' + led_string + ';PWM:' + pwm_string + ';'

        # Calculate the CRC and add it to the string
        data_crc_out = data_out + 'CRC:' + str(Crc8Maxim.calc(data_out.encode(), 0))

        return data_crc_out


    @staticmethod
    def unpack_data(self, data_string):
        analog_array = [0.0] * self.ANALOG_INPUTS


        return (analog_array, switch_array)









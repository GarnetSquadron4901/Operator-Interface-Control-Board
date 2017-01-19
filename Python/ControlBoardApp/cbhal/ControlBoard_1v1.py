from crccheck.crc import Crc8Maxim
import numpy

from cbhal.ControlBoardSerialBase import ControlBoardSerialBase
from cbhal.ControlBoardBase import DataIntegrityError
import logging

logger = logging.getLogger(__name__)
CB_SNAME = 'ControlBoard_1v1'
CB_LNAME = 'FRC Control Board - Version 1.1'

class HardwareAbstractionLayer(ControlBoardSerialBase):

    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

    PID = 24577
    VID = 1027

    BAUD_RATE = 115200  # bps
    TIMEOUT = 1  # second(s)

    def __init__(self):

        # Setup parent class
        super(HardwareAbstractionLayer, self).__init__(port_name='auto',
                                                       baud_rate=self.BAUD_RATE,
                                                       timeout=self.TIMEOUT,
                                                       pid=self.PID,
                                                       vid=self.VID)

    def reset_board(self):
        # Flush input. There may be data already waiting at the port.
        self.flush_input()

        # Reset
        self.pulse_dtr()

        # Read welcome message
        welcome_msg = self.read_line()

        if welcome_msg != 'FRC Control Board\r\n':
            raise ConnectionError('FRC control board did not send welcome message after reset.')

    def update(self):

        led_out = self.getLedValues()
        pwm_out = self.getPwmValues()
        self.data_out = self.pack_data(led_out, pwm_out)

        # Serial Write & Read
        self.write_line(self.data_out)
        self.data_in = self.read_line()

        switch_in, analog_in = self.unpack_data(self.data_in)
        self.putSwitchvalues(switch_in)
        self.putAnalogvalues(analog_in)

    def pack_data(self, led_array, pwm_array):

        # Make sure the data is the right length
        assert len(pwm_array) == self.PWM_OUTPUTS, 'Length of PWM array is invalid'
        assert len(led_array) == self.LED_OUTPUTS, 'Length of LED array is invalid'

        ###########################################
        # Convert the LED Boolean array to a string
        # 1. Convert LED boolean array to number
        led_u16 = 0x0000
        for led in led_array:
            led_u16 |= led << 16
            led_u16 >>= 1

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

    def unpack_data(self, data_string):

        switch_array = []
        analog_array = []

        assert any(data_string), 'No data in.'

        # 'SW:0;ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6;CRC:162;\r\n'
        data_array = (data_string.replace('\r\n', '')).split(';')[:-1]
        # ['SW:0', 'ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6', 'CRC:162']

        # 'SW:0;ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6;'
        crc_val = Crc8Maxim.calc(data_string.split('CRC:')[0].encode(), 0)


        data_in_dict = {}
        for data in data_array:
            data = data.split(':')
            data_in_dict.update({data[0]: data[1]})

        if int(data_in_dict['CRC']) == int(crc_val):

            switches = numpy.uint16(int(data_in_dict['SW'], 16))
            for switch_num in range(self.SWITCH_INPUTS):
                switch_array.append(bool(switches & 0x0001))
                switches >>= 1

            analogs = data_in_dict['ANA'].split(',')
            if len(analogs) is self.ANALOG_INPUTS:
                analog_array = list(map(int, analogs))
        else:
            raise DataIntegrityError('CRC failed')

        assert len(analog_array) is self.ANALOG_INPUTS, 'Number of analog inputs is incorrect. Saw %d, Expected %d' % (len(analog_array), self.ANALOG_INPUTS)
        assert len(switch_array) is self.SWITCH_INPUTS, 'Number of switch inputs is incorrect. Saw %d, Expected %d' % (len(switch_array), self.SWITCH_INPUTS)

        return switch_array, analog_array




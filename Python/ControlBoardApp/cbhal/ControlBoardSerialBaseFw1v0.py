import logging
import sys
from crccheck.crc import Crc8Maxim
import numpy

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardSerialBase import ControlBoardSerialBase
    from ControlBoardApp.cbhal.ControlBoardBase import DataIntegrityError
else:
    # Test Mode
    from cbhal.ControlBoardSerialBase import ControlBoardSerialBase
    from cbhal.ControlBoardBase import DataIntegrityError


class ControlBoardSerialBaseFw1v0(ControlBoardSerialBase):
    """ Represents Arduino based firmware v1.0 for the Control Board"""
    BAUD_RATE = 115200  # bps
    TIMEOUT = 2  # second(s)

    def __init__(self):

        # Setup parent class
        super(ControlBoardSerialBaseFw1v0, self).__init__(port_name='auto',
                                                          baud_rate=self.BAUD_RATE,
                                                          timeout=self.TIMEOUT,
                                                          pid=self.PID,
                                                          vid=self.VID)

    def reset_board(self):
        """
        Resets the microcontroller using the DTR signal.
        :return: 
        """
        logger.debug('Resetting the control board')
        # Flush input. There may be data already waiting at the port.
        self.flush_input()

        # Reset
        self.pulse_dtr()

        # Read welcome message
        welcome_msg = self.read_line()

        if welcome_msg != 'FRC Control Board\r\n':
            raise ConnectionError('FRC control board did not send welcome message after reset.')

    def update(self):
        """
        Updates the microcontroller with output data. Receives a response packet with input data.
        :return: 
        """

        # Get Output Data
        led_out = self.getLedValues()
        pwm_out = self.getPwmValues()
        data_out = self.pack_data(led_out, pwm_out)

        # Serial Write & Read
        self.write_line(data_out)
        data_in = self.read_line()

        # Push Input Data
        switch_in, analog_in = self.unpack_data(data_in)
        self.putSwitchvalues(switch_in)
        self.putAnalogvalues(analog_in)

    def pack_data(self, led_array, pwm_array):
        """
        Packages input data into the format the microcontroller expects
        :param led_array: list - List of LED values, must be the same length as expected
        :param pwm_array: list - List of PWM values, must be the same length as expected
        :return: 
        """

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
        """
        Unpacks data from the microcontroller
        :param data_string: str - Raw data from the microcontroller
        :return: tuple - First element is the switch array (list), Second element is the analog array (list)
        """
        switch_array = []
        analog_array = []

        # Check if there is any data
        if not any(data_string):
            raise DataIntegrityError('No data')

        # Check for missing data tags
        missing = []
        for tag in ['ANA', 'CRC', 'SW']:
            if not tag in data_string:
                missing.append(tag)
        if any(missing):
            raise DataIntegrityError(
                'Missing attributes in data: %s Original data: \'%s\'' % (str(missing), data_string))

        # Separate the data packet into a list.
        # 'SW:0;ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6;CRC:162;\r\n'
        data_array = (data_string.replace('\r\n', '')).split(';')[:-1]
        # ['SW:0', 'ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6', 'CRC:162']

        ###########################################
        # CRC Check
        # Calculate the CRC value from the data before 'CRC:'
        # 'SW:0;ANA:4,4,6,4,4,4,5,4,4,4,4,5,5,4,4,6;'
        crc_val = Crc8Maxim.calc(data_string.split('CRC:')[0].encode(), 0)
        #
        # Create a dictionary from the data array (placed here to get the CRC value
        data_in_dict = {}
        for data in data_array:
            data = data.split(':')
            data_in_dict.update({data[0]: data[1]})
        #
        # Check that the PC side CRC matches the microcontroller side CRC
        if int(data_in_dict['CRC']) != int(crc_val):
            raise DataIntegrityError('CRC failed. Calculated %s for data \'%s\'' % (str(int(crc_val)), data_string))
        # End CRC Check
        ###########################################

        # At this point, we know the data is valid

        # Unpack the switch values from the Unsigned 16-bit Integer
        switches = numpy.uint16(int(data_in_dict['SW'], 16))
        for switch_num in range(self.SWITCH_INPUTS):
            switch_array.append(bool(switches & 0x0001))
            switches >>= 1

        # Unpack the analog values from the string of analog values
        analogs = data_in_dict['ANA'].split(',')
        if len(analogs) is self.ANALOG_INPUTS:
            analog_array = list(map(int, analogs))

        # Check that the data lengths are valid
        if len(analog_array) is not self.ANALOG_INPUTS:
            raise IndexError(
                'Number of analog inputs is incorrect. Saw %d, Expected %d' % (len(analog_array), self.ANALOG_INPUTS))
        if len(switch_array) is not self.SWITCH_INPUTS:
            raise IndexError(
                'Number of switch inputs is incorrect. Saw %d, Expected %d' % (len(switch_array), self.SWITCH_INPUTS))

        # Return the switch and analog data
        return switch_array, analog_array

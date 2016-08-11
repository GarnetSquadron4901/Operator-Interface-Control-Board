import serial
import serial.tools.list_ports as lp
from crccheck.crc import Crc8Maxim

import time
#import wx
import threading
import numpy


class HAL:
    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

    def __init__(self, port_name='auto', speed=115200, timeout=1, PID=24577, VID=1027, debug=False):

        self.port_name = port_name
        self.speed = speed
        self.timeout = timeout
        self.PID = PID
        self.VID = VID

        # Set up default variable
        self.led_out = None
        self.pwm_out = None
        self.analog_in = None
        self.switch_in = None
        self.data_in = ''
        self.data_out = ''
        self.reset_values()

        self.port = None

        self.debug = debug

        self.run_thread = False

        self.event_handler = None

    def usb_connect(self):
        port_name = self.find_com_port()
        self.port = serial.Serial(port=port_name, baudrate=self.speed, timeout=self.timeout)

    def find_com_port(self):
        # If the port name is auto, find the control board by searching through the PID and VID
        port_names = [port.device for port in lp.comports() if port.pid == self.PID and port.vid == self.VID]

        if self.port_name == 'auto':
            if not any(port_names):
                raise serial.SerialException('No valid COM ports found for the control board. Is it connected?')
                time.sleep(1)
            elif len(port_names) > 1:
                # TODO: Handle multiple port_names
                port_name = port_names[0]
            else:
                port_name = port_names[0]
        else:
            if self.port_name in port_names:
                port_name = self.port_name
            else:
                raise serial.SerialException('Invalid COM port selected.')

        return port_name


    def usb_disconnect(self):
        if self.usb_connected():
            self.port.close()

    def usb_reconnect(self):
        self.usb_disconnect()
        time.sleep(1)
        self.usb_connect()

    def reset_values(self):
        self.led_out = [False] * self.LED_OUTPUTS
        self.pwm_out = [0] * self.PWM_OUTPUTS
        self.analog_in = [0] * self.ANALOG_INPUTS
        self.switch_in = [False] * self.SWITCH_INPUTS
        self.data_in = ''
        self.data_out = ''

    def reset_board(self):
        # Flush input. There may be data already waiting at the port.
        self.port.flushInput()

        # Reset
        self.port.dtr = 1;
        time.sleep(50e-3)
        self.port.dtr = 0;

        # Read welcome message
        welcome_msg = self.port.readline().decode('utf-8')

        if welcome_msg != 'FRC Control Board\r\n':
            raise ConnectionError('FRC control board did not send welcome message after reset.')

    def usb_connected(self):
        if self.port is None:
            return False
        else:
            return self.port.isOpen()

    def start(self):
        self.run_thread = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.run_thread is True:
            self.run_thread = False
            self.thread.join()

    def set_event_handler(self, function):
        self.event_handler = function


    def run(self):
        run_state_machine = True
        STATE_INIT = 'Init'
        STATE_CHECK_CONNECTION = 'Check Connection'
        STATE_RESET = 'Reset'
        STATE_RUN = 'Run'
        STATE_RECONNECT = 'Reconnect'
        STATE_STOP = 'Stop'

        last_state = STATE_INIT
        state = STATE_INIT


        while run_state_machine:
            # Stop case
            if self.run_thread is False:
                state = STATE_STOP

            # Debug
            if self.debug is True and state is not last_state:
                print('HAL mode switch: %s -> %s' % (last_state, state))
                last_state = state

            # State machine
            try:
                if state is STATE_INIT:
                    self.usb_connect()
                    if self.debug:
                        print('HAL Started.')
                    state = STATE_CHECK_CONNECTION

                elif state is STATE_CHECK_CONNECTION:
                    if self.usb_connected():
                        state = STATE_RESET
                    else:
                        state = STATE_RECONNECT
                elif state is STATE_RESET:
                    self.reset_values()
                    self.reset_board()
                    state = STATE_RUN
                elif state is STATE_RUN:
                    self.update()
                    state = STATE_RUN
                elif state is STATE_RECONNECT:
                    self.usb_reconnect()
                    state = STATE_CHECK_CONNECTION
                elif state is STATE_STOP:
                    self.usb_disconnect()
                    run_state_machine = False
                    if self.debug:
                        print('HAL Stopped.')
                    state = STATE_STOP
            except serial.SerialException:
                state = STATE_RECONNECT
            except serial.SerialTimeoutException:
                state = STATE_RESET
            except KeyboardInterrupt:
                state = STATE_STOP
            except Exception as e:
                if self.debug:
                    print('Unhandled exception:', e)

    def update(self):
        self.data_out = self.pack_data(self.led_out, self.pwm_out)
        # print ('OUT:', data_out)
        self.port.write(str.encode(self.data_out+'\r\n'))
        self.port.flushOutput()

        self.data_in = self.port.readline().decode('utf-8')
        # print ('IN:', data_in)
        self.switch_in, self.analog_in = self.unpack_data(self.data_in)

        if self.event_handler is not None:
            self.event_handler()


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

    def unpack_data(self, data_string):

        switch_array = []
        analog_array = []

        assert(any(data_string), 'No data in.')

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
            raise IOError('Cyclic redundancy check failed.')

        assert(len(analog_array) is self.ANALOG_INPUTS, 'Number of analog inputs is incorrect. Saw %d, Expected %d' % (len(analog_array), self.ANALOG_INPUTS))
        assert(len(switch_array) is self.SWITCH_INPUTS, 'Number of switch inputs is incorrect. Saw %d, Expected %d' % (len(switch_array), self.SWITCH_INPUTS))

        return switch_array, analog_array

def _event_handler():
    print('SW:', hal.switch_in)
    print('AN:', hal.analog_in)

if __name__ == '__main__':
    hal = HAL(debug=True)
    hal.set_event_handler(_event_handler)
    hal.start()

    try:
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    hal.stop()









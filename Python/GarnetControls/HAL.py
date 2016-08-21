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

    UPDATE_DELTA_TIME_AVERAGE_LEN = 10

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
        self.update_deltas = []
        self.last_update_time = None
        self.hal_state = 'None'
        self.data_in = ''
        self.data_out = ''

        self.control_board_running = False

        self.port = None

        self.debug = debug

        self.run_thread = False

        self.event_handler = None

        self.data_lock = threading.Lock()

        self.reset_values()

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

    def is_control_board_running(self):
        self.data_lock.acquire()
        control_board_running = self.control_board_running
        self.data_lock.release()
        return control_board_running

    def get_hal_state(self):
        self.data_lock.acquire()
        state = str(self.hal_state)
        self.data_lock.release()
        return state

    def usb_disconnect(self):
        if self.usb_connected():
            self.port.close()

    def usb_reconnect(self):
        self.usb_disconnect()
        time.sleep(1)
        self.usb_connect()

    def reset_values(self):
        self.data_lock.acquire()
        self.led_out = [False] * self.LED_OUTPUTS
        self.pwm_out = [int(0)] * self.PWM_OUTPUTS
        self.analog_in = [int(0)] * self.ANALOG_INPUTS
        self.switch_in = [False] * self.SWITCH_INPUTS
        self.update_deltas = []
        self.last_update_time = None
        self.data_in = ''
        self.data_out = ''
        self.data_lock.release()

        self.trigger_event()

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

    def getSwitchValue(self, ch):
        return self.getSwitchValues()[ch]

    def getSwitchValues(self):
        self.data_lock.acquire()
        data = self.switch_in
        self.data_lock.release()
        return data

    def getAnalogValue(self, ch):
        return self.getAnalogValues()[ch]

    def getAnalogValues(self):
        self.data_lock.acquire()
        data = self.analog_in
        self.data_lock.release()
        return data

    def getPwmValue(self, ch):
        return self.getPwmValues()[ch]

    def getPwmValues(self):
        self.data_lock.acquire()
        data = self.pwm_out
        self.data_lock.release()
        return data

    def getLedValue(self, ch):
        return self.getLedValues()[ch]

    def getLedValues(self):
        self.data_lock.acquire()
        data = self.led_out
        self.data_lock.release()
        return data

    def putLedValues(self, led_out):
        assert len(led_out) == self.LED_OUTPUTS, \
            'Number of LED outs does not match. Expected %d, Got %d' % \
            (self.LED_OUTPUTS, len(led_out))
        self.data_lock.acquire()
        self.led_out = [bool(led) for led in led_out]
        self.data_lock.release()

    def putPwmValues(self, pwm_out):
        assert len(pwm_out) == self.PWM_OUTPUTS, \
            'Number of PWM outs does not match. Expected %d, Got %d' % \
            (self.PWM_OUTPUTS, len(pwm_out))
        self.data_lock.acquire()
        self.pwm_out = [int(pwm) for pwm in pwm_out]
        self.data_lock.release()

    def putAnalogvalues(self, analog_in):
        assert len(analog_in) == self.ANALOG_INPUTS, \
            'Number of Analog ins does not match. Expected %d, Got %d' % \
            (self.ANALOG_INPUTS, len(analog_in))
        self.data_lock.acquire()
        self.analog_in = [int(analog) for analog in analog_in]
        self.data_lock.release()

    def putSwitchvalues(self, switch_in):
        assert len(switch_in) == self.SWITCH_INPUTS, \
            'Number of Switch ins does not match. Expected %d, Got %d' % \
            (self.SWITCH_INPUTS, len(switch_in))
        self.data_lock.acquire()
        self.switch_in = [bool(switch) for switch in switch_in]
        self.data_lock.release()

    def getUpdateRate(self):
        self.data_lock.acquire()
        update_deltas = self.update_deltas
        self.data_lock.release()
        if len(update_deltas) is self.UPDATE_DELTA_TIME_AVERAGE_LEN:
            avg_delta = sum(update_deltas) / len(update_deltas)
        else:
            avg_delta = None

        if avg_delta is not None and avg_delta > 0:
            return 1.0 / avg_delta
        else:
            return None

    def trigger_event(self):
        if self.event_handler is not None:
            self.event_handler()

    def run(self):
        run_state_machine = True
        STATE_INIT = 'Initializing'
        STATE_CHECK_CONNECTION = 'Checking USB connection'
        STATE_RESET = 'Resetting control board'
        STATE_RUN = 'Running'
        STATE_RECONNECT = 'Control board unplugged.'
        STATE_STOP = 'Stopped'

        last_state = STATE_INIT
        state = STATE_INIT

        while run_state_machine:
            # Stop case
            if self.run_thread is False:
                state = STATE_STOP

            # Debug
            if state is not last_state:
                self.trigger_event()
                if self.debug:
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

            self.data_lock.acquire()
            self.control_board_running = state is STATE_RUN
            self.hal_state = state
            self.data_lock.release()

    def update(self):

        led_out = self.getLedValues()
        pwm_out = self.getPwmValues()
        self.data_out = self.pack_data(led_out, pwm_out)
        self.port.write(str.encode(self.data_out+'\r\n'))
        self.port.flushOutput()

        self.data_in = self.port.readline().decode('utf-8')

        switch_in, analog_in = self.unpack_data(self.data_in)
        self.putSwitchvalues(switch_in)
        self.putAnalogvalues(analog_in)

        cur_time = time.time()
        self.data_lock.acquire()
        if self.last_update_time is not None:
            self.update_deltas.append(cur_time - self.last_update_time)
        self.last_update_time = cur_time
        if len(self.update_deltas) > self.UPDATE_DELTA_TIME_AVERAGE_LEN:
            self.update_deltas.pop(0)
        self.data_lock.release()

        self.trigger_event()


    def pack_data(self, led_array, pwm_array):

        # Make sure the data is the right length
        assert len(pwm_array) == self.PWM_OUTPUTS, 'Length of PWM array is invalid'
        assert len(led_array) == self.LED_OUTPUTS, 'Length of LED array is invalid'

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
            raise IOError('Cyclic redundancy check failed.')

        assert len(analog_array) is self.ANALOG_INPUTS, 'Number of analog inputs is incorrect. Saw %d, Expected %d' % (len(analog_array), self.ANALOG_INPUTS)
        assert len(switch_array) is self.SWITCH_INPUTS, 'Number of switch inputs is incorrect. Saw %d, Expected %d' % (len(switch_array), self.SWITCH_INPUTS)

        return switch_array, analog_array

def _event_handler():
    print('SW:', hal.getSwitchValues())
    print('AN:', hal.getAnalogValues())

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









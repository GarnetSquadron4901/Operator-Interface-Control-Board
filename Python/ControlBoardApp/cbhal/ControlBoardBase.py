import threading
import time
import wx
import logging

logger = logging.getLogger(__name__)
class ConnectionFailed(Exception):
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Connection Exception: ' + str(self.v)


class ConnectionTimeout(TimeoutError):
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Connection Timeout: ' + str(self.v)


class DataIntegrityError(IOError):
    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Data integrity check failed: ' + str(self.v)


class ControlBoardBase:
    NAME = 'Control Board Base'

    LED_OUTPUTS = 0
    PWM_OUTPUTS = 0
    ANALOG_INPUTS = 0
    SWITCH_INPUTS = 0

    UPDATE_DELTA_TIME_AVERAGE_LEN = 10

    def __init__(self):
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
        self.run_thread = False
        self.event_handler = None
        self.thread = None
        self.data_lock = threading.Lock()
        self.reset_values()

    def get_type(self):
        return self.NAME

    def reset_board(self):
        raise NotImplementedError('This function needs to be implemented!')

    def is_connected(self):
        raise NotImplementedError('This function needs to be implemented!')

    def update(self):
        raise NotImplementedError('This function needs to be implemented!')

    def reconnect(self):
        raise NotImplementedError('This function needs to be implemented!')

    def disconnect(self):
        raise NotImplementedError('This function needs to be implemented!')

    def is_simulator(self):
        return False

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
        try:
            self.led_out = [bool(led) for led in led_out]
        except Exception as e:
            wx.LogError('Failed to pack LED values: ' + e)
        self.data_lock.release()

    def putPwmValues(self, pwm_out):
        assert len(pwm_out) == self.PWM_OUTPUTS, \
            'Number of PWM outs does not match. Expected %d, Got %d' % \
            (self.PWM_OUTPUTS, len(pwm_out))
        self.data_lock.acquire()
        try:
            self.pwm_out = [int(pwm) for pwm in pwm_out]
        except Exception as e:
            wx.LogError('Failed to pack PWM values: ' + e)
        self.data_lock.release()

    def putAnalogvalues(self, analog_in):
        assert len(analog_in) == self.ANALOG_INPUTS, \
            'Number of Analog ins does not match. Expected %d, Got %d' % \
            (self.ANALOG_INPUTS, len(analog_in))
        self.data_lock.acquire()
        try:
            self.analog_in = [int(analog) for analog in analog_in]
        except Exception as e:
            wx.LogError('Failed to pack analog values: ' + e)
        self.data_lock.release()

    def putSwitchvalues(self, switch_in):
        assert len(switch_in) == self.SWITCH_INPUTS, \
            'Number of Switch ins does not match. Expected %d, Got %d' % \
            (self.SWITCH_INPUTS, len(switch_in))
        self.data_lock.acquire()
        try:
            self.switch_in = [bool(switch) for switch in switch_in]
        except Exception as e:
            wx.LogError('Failed to pack switch values: ' + e)
        self.data_lock.release()

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

    def get_status(self):
        return {'LEDs': self.getLedValues(),
                'PWMs': self.getPwmValues(),
                'ANAs': self.getAnalogValues(),
                'SWs': self.getSwitchValues(),
                'State': self.get_hal_state(),
                'IsRunning': self.control_board_running,
                'UpdateRate': self.getUpdateRate()}

    def trigger_event(self):
        if self.event_handler is not None:
            self.event_handler()

    def calc_time_since_last_update(self):
        cur_time = time.time()
        self.data_lock.acquire()
        try:
            if self.last_update_time is not None:
                self.update_deltas.append(cur_time - self.last_update_time)
            self.last_update_time = cur_time
            if len(self.update_deltas) > self.UPDATE_DELTA_TIME_AVERAGE_LEN:
                self.update_deltas.pop(0)
        except:
            pass
        self.data_lock.release()

    def run(self):
        run_state_machine = True
        STATE_INIT = 'Initializing'
        STATE_CHECK_CONNECTION = 'Checking connection'
        STATE_RESET = 'Resetting control board'
        STATE_RUN = 'Running'
        STATE_RECONNECT = 'Control board unplugged'
        STATE_STOP = 'Stopped'

        last_state = STATE_INIT
        state = STATE_INIT

        wx.LogVerbose('HAL state machine has started.')

        while run_state_machine:
            # Stop case
            if self.run_thread is False:
                state = STATE_STOP

            # Debug
            if state is not last_state:
                self.trigger_event()
                wx.LogVerbose('HAL mode switch: %s -> %s' % (last_state, state))
                last_state = state

            # State machine
            try:
                if state is STATE_INIT:
                    self.is_connected()
                    state = STATE_CHECK_CONNECTION

                elif state is STATE_CHECK_CONNECTION:
                    if self.is_connected():
                        state = STATE_RESET
                    else:
                        state = STATE_RECONNECT

                elif state is STATE_RESET:
                    self.reset_values()
                    self.reset_board()
                    state = STATE_RUN

                elif state is STATE_RUN:
                    self.update()
                    self.calc_time_since_last_update()
                    self.trigger_event()
                    state = STATE_RUN

                elif state is STATE_RECONNECT:
                    self.reconnect()
                    state = STATE_CHECK_CONNECTION

                elif state is STATE_STOP:
                    self.disconnect()
                    run_state_machine = False
                    state = STATE_STOP

            except ConnectionFailed:
                state = STATE_RECONNECT
            except ConnectionTimeout:
                state = STATE_RESET
            except DataIntegrityError:
                wx.LogError(e)
            except KeyboardInterrupt:
                state = STATE_STOP
            except Exception as e:
                wx.LogError('Unhandled exception: %s' % e)

            self.data_lock.acquire()
            self.control_board_running = state is STATE_RUN
            self.hal_state = state
            self.data_lock.release()
        wx.LogVerbose('HAL state machine has stopped.')



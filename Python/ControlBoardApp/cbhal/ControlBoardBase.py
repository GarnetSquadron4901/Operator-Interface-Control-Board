import logging

logger = logging.getLogger(__name__)

import threading
import time
import wx
import traceback


######################################################
# ControlBoardBase exception classes
class ConnectionFailed(Exception):
    """ Exception thrown if the connection fails, such as being unplugged. """

    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Connection Exception: ' + str(self.v)


class ConnectionTimeout(TimeoutError):
    """ Exception thrown if the connection times out, such as the microprocessor resetting or freezing. """

    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Connection Timeout: ' + str(self.v)


class DataIntegrityError(IOError):
    """ Exception thrown if the data being received is not validated properly. Usually a CRC check failure. """

    def __init__(self, v):
        self.v = v

    def __str__(self):
        return 'Data integrity check failed: ' + str(self.v)


######################################################

class ControlBoardBase:
    """ The base control board class. """
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
        self.control_board_running = False
        self.run_thread = False
        self.event_handler = None
        self.thread = None
        self.data_lock = threading.Lock()
        self.data_in = ''
        self.data_out = ''
        self.reset_values()

    # def get_type(self):
    #     """
    #     Returns the type of control board
    #     :return: str -
    #     """
    #     return self.NAME

    def reset_board(self):
        """
        This function is called when the board needs to be reset.
 
        :return: 
        """
        raise NotImplementedError('This function needs to be implemented!')

    def is_connected(self):
        """
        This function is called to check if the control board is connected 

        :return: 
        """
        raise NotImplementedError('This function needs to be implemented!')

    def update(self):
        """
        This function is called to send new control data to the control board. 
        
        :return: 
        """
        raise NotImplementedError('This function needs to be implemented!')

    def reconnect(self):
        """
        This function will attempt to reconnect to the control board.
        
        :return: 
        """
        raise NotImplementedError('This function needs to be implemented!')

    def disconnect(self):
        """
        This function disconnects / shuts down the control board interface.
         
        :return: 
        """

        raise NotImplementedError('This function needs to be implemented!')

    def is_simulator(self):
        """
        Tells whether or not the current board is a simulator.
        
        :return: bool - True if Simulator, False if Real
        """
        return False

    def is_cbhal_running(self):
        """ Tells if the CHBAL thread is running. 
        
        :return: bool - True if running, False if not running
        """
        return self.run_thread

    def start(self):
        """
        Starts the CBHAL thread. 
        
        :return: 
        """
        self.run_thread = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stops the CBHAL thread.
        
        :return: 
        """
        if self.run_thread is True:
            self.run_thread = False
            self.thread.join()

    def set_event_handler(self, event_function):
        """
        Sets the event handler to process new data.
        
        :param event_function: The function to call when new data arrives.
        :return: 
        """
        self.event_handler = event_function

    def getSwitchValue(self, ch):
        """
        Returns a specific switch's value. 
        
        :param ch: Switch channel
        :return: bool - Switch value
        """
        return self.getSwitchValues()[ch]

    def getSwitchValues(self):
        """
        Returns a list of switch values.
        
        :return: list(bool) - Switch values
        """
        self.data_lock.acquire()
        data = self.switch_in
        self.data_lock.release()
        return data

    def getAnalogValue(self, ch):
        """
        Returns a specific analog's value.
        
        :param ch: Analog channel
        :return: uint8 - Analog value
        """
        return self.getAnalogValues()[ch]

    def getAnalogValues(self):
        """
        Returns a list of analog values.
        
        :return: list(uint8) - Analog values
        """
        self.data_lock.acquire()
        data = self.analog_in
        self.data_lock.release()
        return data

    def getPwmValue(self, ch):
        """
        Returns a specific PWM value.
        
        :param ch: PWM channel 
        :return: uint8 - PWM value
        """
        return self.getPwmValues()[ch]

    def getPwmValues(self):
        """
        Returns a list of PWM values.
        
        :return: list(uint8) - PWM values
        """
        self.data_lock.acquire()
        data = self.pwm_out
        self.data_lock.release()
        return data

    def getLedValue(self, ch):
        """
        Returns a specific LED value.
        
        :param ch: LED channel 
        :return: bool - LED state
        """
        return self.getLedValues()[ch]

    def getLedValues(self):
        """ Returns a list of LED values. 
        
        :return: list(bool) - LED values
        """
        self.data_lock.acquire()
        data = self.led_out
        self.data_lock.release()
        return data

    @staticmethod
    def check_list_length(input_list, expected_length, list_type):
        """
        Assertion like test to make sure the data length is correct
        
        :param input_list: The list to check.
        :param expected_length: The expected length.
        :param list_type: String to describe the list type.
        :return: 
        """
        if len(input_list) != expected_length:
            raise IndexError('Number of %s does not match. Expected %d, Got %d' %
                             (list_type, expected_length, len(input_list)))

    def putLedValues(self, led_out):
        """
        Programs the list of LED outputs.
        
        :param led_out: list - LED outputs
        :return: 
        """
        self.check_list_length(led_out, self.LED_OUTPUTS, 'LED outs')
        self.data_lock.acquire()
        try:
            self.led_out = [bool(led) for led in led_out]
        except Exception:
            logger.error('Failed to pack LED values: \n %s' % traceback.format_exc())

        self.data_lock.release()

    def putPwmValues(self, pwm_out):
        """
        Programs the list of PWM outputs.
        
        :param pwm_out: list - PWM outputs 
        :return: 
        """
        self.check_list_length(pwm_out, self.PWM_OUTPUTS, 'PWM outs')
        self.data_lock.acquire()
        try:
            self.pwm_out = [int(pwm) for pwm in pwm_out]
        except Exception:
            logger.error('Failed to pack PWM values: \n %s' % traceback.format_exc())
        self.data_lock.release()

    def putAnalogvalues(self, analog_in):
        """
        Programs the list of Analog inputs.

        :param analog_in: list - Analog inputs 
        :return: 
        """
        self.check_list_length(analog_in, self.ANALOG_INPUTS, 'Analog ins')
        self.data_lock.acquire()
        try:
            self.analog_in = [int(analog) for analog in analog_in]
        except Exception:
            logger.error('Failed to pack analog values: \n %s' % traceback.format_exc())
        self.data_lock.release()

    def putSwitchvalues(self, switch_in):
        """
        Programs the list of Switch inputs.

        :param switch_in: list - Switch inputs 
        :return: 
        """
        self.check_list_length(switch_in, self.SWITCH_INPUTS, 'Switch ins')
        self.data_lock.acquire()
        try:
            self.switch_in = [bool(switch) for switch in switch_in]
        except Exception:
            logger.error('Failed to pack switch values: \n %s' % traceback.format_exc())
        self.data_lock.release()

    def reset_values(self):
        """
        Resets all control board variables. 
        
        :return: 
        """
        logger.debug('Resetting the control board variables')
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
        """
        Returns the rate of update. None if not ready.
        :return: float - update rate; None if not ready.
        """
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
        """
        Returns if the control board is actively running
        :return: bool - running state
        """
        self.data_lock.acquire()
        control_board_running = self.control_board_running
        self.data_lock.release()
        return control_board_running

    def get_hal_state(self):
        """
        Returns the HAL state
        :return: str - HAL state
        """
        self.data_lock.acquire()
        state = str(self.hal_state)
        self.data_lock.release()
        return state

    def get_status(self):
        """
        Returns a dictionary of status information
        :return: dict - status
        """
        return {'LEDs': self.getLedValues(),
                'PWMs': self.getPwmValues(),
                'ANAs': self.getAnalogValues(),
                'SWs': self.getSwitchValues(),
                'State': self.get_hal_state(),
                'IsRunning': self.is_control_board_running(),
                'UpdateRate': self.getUpdateRate()}

    def trigger_event(self):
        """
        Invokes the event handler.
        :return: 
        """
        if self.event_handler is not None:
            self.event_handler()

    def calc_time_since_last_update(self):
        """
        Calculates the time since the last update. Used to calculate the update rate. 
        
        :return: 
        """
        cur_time = time.time()
        self.data_lock.acquire()
        if self.last_update_time is not None:
            self.update_deltas.append(cur_time - self.last_update_time)
        self.last_update_time = cur_time
        if len(self.update_deltas) > self.UPDATE_DELTA_TIME_AVERAGE_LEN:
            self.update_deltas.pop(0)
        self.data_lock.release()

    def run(self):
        """ Main CBHAL run thread.
        
        :return: 
        """
        last_error = None
        run_state_machine = True

        # States:
        STATE_INIT = 'Initializing'
        STATE_CHECK_CONNECTION = 'Checking connection'
        STATE_RESET = 'Resetting control board'
        STATE_RUN = 'Running'
        STATE_DISCONNECTED = 'Control board disconnected'
        STATE_RECONNECTED = 'Control board connected'
        STATE_STOP = 'Stopped'

        last_state = STATE_INIT
        state = STATE_INIT

        logger.debug('HAL state machine has started.')

        while run_state_machine:
            # Stop case
            if self.run_thread is False:
                state = STATE_STOP

            # Debug
            if state is not last_state:
                self.trigger_event()
                logger.debug('HAL mode switch: %s -> %s' % (last_state, state))
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
                        state = STATE_DISCONNECTED

                elif state is STATE_RESET:
                    self.reset_board()
                    self.reset_values()
                    state = STATE_RUN

                elif state is STATE_RUN:
                    self.update()
                    self.calc_time_since_last_update()
                    self.trigger_event()
                    state = STATE_RUN

                elif state is STATE_DISCONNECTED:
                    self.reconnect()
                    state = STATE_RECONNECTED

                elif state is STATE_RECONNECTED:
                    logger.info('Control board connected.')
                    state = STATE_CHECK_CONNECTION

                elif state is STATE_STOP:
                    self.disconnect()
                    run_state_machine = False
                    state = STATE_STOP

                last_error = None

            except ConnectionFailed as e:
                if str(e) != str(last_error):
                    logger.warning(traceback.format_exc())
                    last_error = e
                state = STATE_DISCONNECTED
            except ConnectionTimeout as e:
                logger.warning(e)
                state = STATE_RESET
            except DataIntegrityError as e:
                if str(e) != str(last_error):
                    logger.warning(traceback.format_exc())
                    last_error = e
            except KeyboardInterrupt:
                if str(e) != str(last_error):
                    logger.debug('Keyboard Interrupt')
                    last_error = e
                state = STATE_STOP
            except Exception as e:
                if str(e) != str(last_error):
                    logger.error(traceback.format_exc())
                    last_error = e

            self.data_lock.acquire()
            self.control_board_running = state is STATE_RUN
            self.hal_state = state
            self.data_lock.release()
        logger.debug('HAL state machine has stopped.')

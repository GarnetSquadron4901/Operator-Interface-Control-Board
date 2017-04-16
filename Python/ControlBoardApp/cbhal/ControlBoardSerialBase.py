import logging
import serial
import serial.tools.list_ports as lp
import time
import sys

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardBase import ControlBoardBase, ConnectionFailed, ConnectionTimeout, \
        DataIntegrityError
else:
    # Test Mode
    from cbhal.ControlBoardBase import ControlBoardBase, ConnectionFailed, ConnectionTimeout, DataIntegrityError


class ControlBoardSerialBase(ControlBoardBase):
    """ Control Board Serial Based - for control boards that use a serial connection. """
    NAME = 'Control Board Serial Base'
    BAUD_RATE = 0

    def __init__(self, port_name, baud_rate, timeout, pid=None, vid=None):
        """

        :param port_name: str - such as COM1. None for Auto
        :param baud_rate: int - the baud rate of the serial connection
        :param timeout: int - timeout in seconds
        :param pid: - USB PID
        :param vid: - USB VID
        """
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.pid = pid
        self.vid = vid
        self.port = None
        super(ControlBoardSerialBase, self).__init__()

        # Log the USB PIDs and VIDs at startup. Only used for debugging purposes.
        self.log_com_pids_vids()

    def reset_board(self):
        """
        Used to reset the board. 
        
        :return: 
        """
        raise NotImplementedError('This function needs to be implemented in the child class!')

    def update(self):
        """
        Used to update the board. 
        
        :return: 
        """
        raise NotImplementedError('This function needs to be implemented in the child class!')

    def flush_input(self):
        """
        Flushes the serial input. 
        
        :return: 
        """
        try:
            self.port.flushInput()
        except serial.SerialException as e:
            raise ConnectionFailed(e)

    def read_line(self):
        """
        Reads a line of data from the serial input.
        
        :return: utf-8 data
        """
        try:
            data = self.port.readline().decode('utf-8')
            if not any(data):
                raise ConnectionTimeout('No data was read in time.')
            return data
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)
        except serial.SerialException as e:
            raise ConnectionFailed(e)
        except UnicodeDecodeError as e:
            raise DataIntegrityError(e)

    def write_line(self, data_out):
        """
        Writes a line of data to the serial output. Flushes the output before continuing. 
        
        :param data_out: 
        :return: 
        """
        try:
            self.port.write(str.encode(data_out + '\r\n'))
            self.port.flushOutput()
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)
        except serial.SerialException as e:
            raise ConnectionFailed(e)

    def connect(self):
        """
        Attempts to attach/connect to a serial port. 
        :return: 
        """
        try:
            port_name = self.find_com_port()
            self.port = serial.Serial(port=port_name, baudrate=self.BAUD_RATE, timeout=self.timeout)
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)
        except serial.SerialException as e:
            time.sleep(1)
            raise ConnectionFailed(e)

    @staticmethod
    def log_com_pids_vids():
        """
        Logs all of the available COM ports with PID and VID information to the log file. 
        NOTE: Logger must be at a debug level.
         
        :return: 
        """
        logger.debug('Listing available COM ports:')
        for port in lp.comports():
            logger.debug('  %s: PID: %s, VID: %s' % (port.device, port.pid, port.vid))

    def find_com_port(self):
        """
        Finds all of the appropriate COM port based on the set PID and VID. Will automatically select the first match.
        
        TODO: Need to handle multiple connections. It might not be uncommon to have multiple Arduinos or FTDI USB to 
        Serial devices connected to a computer at once. 
        
        :return: str - port name
        """

        # Filter on just the PIDs and VIDs that match, if provided
        if self.pid is not None and self.vid is not None:
            # If the port name is auto, find the control board by searching through the PID and VID
            port_names = [port.device for port in lp.comports() if port.pid == self.pid and port.vid == self.vid]
        else:
            # If PID or VID is not supplied, list all the com ports
            port_names = [port.device for port in lp.comports()]

        # If Auto, select the first port in the port_names list
        if self.port_name.lower() == 'auto' and self.pid is not None and self.vid is not None:
            if not any(port_names):
                raise ConnectionFailed('No valid COM ports found for the control board. Is it connected?')
            elif len(port_names) > 1:
                # TODO: Handle multiple port_names
                port_name = port_names[0]
            else:
                port_name = port_names[0]
        else:
            # This is the hard-set COM port setting.
            if self.port_name in port_names:
                port_name = self.port_name
            else:
                raise ConnectionFailed('Invalid COM port selected.')

        return port_name

    def disconnect(self):
        """
        Closes the COM port
        :return: 
        """
        if self.is_connected():
            try:
                self.port.close()
            except serial.SerialException as e:
                raise ConnectionFailed(e)

    def reconnect(self):
        """ Disconnected and reconnects to the COM port. """
        self.disconnect()
        time.sleep(1)
        self.connect()

    def pulse_dtr(self, assert_time=50e-3):
        """
        Pulses the DTR pin for a given assertion time in seconds.
        :param assert_time: float - seconds to hold the assertion. (Default = 50ms)
        :return: 
        """
        try:
            self.port.dtr = 1
            time.sleep(assert_time)
            self.port.dtr = 0
        except serial.SerialException as e:
            raise ConnectionFailed(e)

    def is_connected(self):
        """
        Returns True is the serial port is valid and open.
        :return: bool - Serial port connected
        """
        try:
            if self.port is None:
                return False
            else:
                return self.port.isOpen()
        except serial.SerialException as e:
            raise ConnectionFailed(e)

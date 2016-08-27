import serial
import serial.tools.list_ports as lp
import time

from ControlBoardApp.hal.ControlBoardBase import ControlBoardBase, ConnectionFailed, ConnectionTimeout


class ControlBoardSerialBase(ControlBoardBase):
    NAME = 'Control Board Serial Base'

    def __init__(self, port_name, baud_rate, timeout, debug, pid=None, vid=None):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.pid = pid
        self.vid = vid
        self.port = None

        super(ControlBoardSerialBase, self).__init__(debug=debug)

    def flush_input(self):
        try:
            self.port.flushInput()
        except serial.SerialException as e:
            raise ConnectionFailed(e)

    def read_line(self):
        try:
            return self.port.readline().decode('utf-8')
        except serial.SerialException as e:
            raise ConnectionFailed(e)
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)

    def write_line(self, data_out):
        try:
            self.port.write(str.encode(data_out + '\r\n'))
            self.port.flushOutput()
        except serial.SerialException as e:
            raise ConnectionFailed(e)
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)

    def usb_connect(self):
        try:
            port_name = self.find_com_port()
            self.port = serial.Serial(port=port_name, baudrate=self.BAUD_RATE, timeout=self.timeout)
        except serial.SerialException as e:
            time.sleep(1)
            raise ConnectionFailed(e)
        except serial.SerialTimeoutException as e:
            raise ConnectionTimeout(e)


    def find_com_port(self, pid, vid):
        if self.pid is not None and self.vid is not None:
            # If the port name is auto, find the control board by searching through the PID and VID
            port_names = [port.device for port in lp.comports() if port.pid == pid and port.vid == vid]
        else:
            # If PID or VID is not supplied, list all the com ports
            port_names = [port.device for port in lp.comports()]

        if self.port_name.lower() == 'auto' and self.pid is not None and self.vid is not None:
            if not any(port_names):
                raise ConnectionFailed('No valid COM ports found for the control board. Is it connected?')
            elif len(port_names) > 1:
                # TODO: Handle multiple port_names
                port_name = port_names[0]
            else:
                port_name = port_names[0]
        else:
            if self.port_name in port_names:
                port_name = self.port_name
            else:
                raise ConnectionFailed('Invalid COM port selected.')

        return port_name

    def usb_disconnect(self):
        if self.usb_connected():
            try:
                self.port.close()
            except serial.SerialException as e:
                raise ConnectionFailed(e)

    def usb_reconnect(self):
        self.usb_disconnect()
        time.sleep(1)
        self.usb_connect()

    def pulse_dtr(self, assert_time=50e-3):
        try:
            self.port.dtr = 1
            time.sleep(assert_time)
            self.port.dtr = 0
        except serial.SerialException as e:
            raise ConnectionFailed(e)

    def usb_connected(self):
        try:
            if self.port is None:
                return False
            else:
                return self.port.isOpen()
        except serial.SerialException as e:
            raise ConnectionFailed(e)
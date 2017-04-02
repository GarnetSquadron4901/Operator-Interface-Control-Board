import logging



import wx

from networktables import NetworkTable

class NetworkTableAbstractionLayer():

    SWITCH_OUT = 'Switch'
    ANALOG_OUT = 'Analog'
    PWM_IN = 'PWM'
    LED_IN = 'LED'

    STATUS_INIT = 'Initializing...'
    STATUS_CLIENT_STOPPING = 'Disabling...'
    STATUS_CLIENT_STOPPED = 'Disabled'
    STATUS_CLIENT_STARTING = 'Enabling...'
    STATUS_CLIENT_STARTED_CONNECTING = 'Enabled. Connecting...'
    STATUS_CLIENT_CONNECTED = 'Connected'
    STATUS_ERROR = 'Error'
    
    def __init__(self, address, cbhal_handler, flush_period=50e-3):
        '''

        :param address: str
        :param cbhal_handler: HAL
        :param flush_period: int
        '''
        self.logger = logging.getLogger(__name__)
        
        self.last_ntal_log_status = self.STATUS_INIT
        self._set_status(self.STATUS_INIT)
        self.last_address = address
        self.address = address
        self.flush_period = flush_period
        self.nt = None
        self.cbhal_handler = cbhal_handler

        self.sw_vals_out = []
        self.led_vals_in = []
        self.ana_vals_out = []
        self.pwm_vals_in = []

        self.startNtClient()
        self.reset_table()
        self.logger.debug('NTAL initialized.')

    def getNtServerAddress(self):
        return self.address

    def setNtServerAddress(self, new_address):
        self.logger.info('Changing NT server address from \"%s\" to \"%s\"' % (self.address, new_address))
        self.address = new_address

        if self.ntal_status in [self.STATUS_CLIENT_CONNECTED, self.STATUS_CLIENT_STARTED_CONNECTING, self.STATUS_CLIENT_STARTING]:
            self.shutdownNtClient()
            self.startNtClient()
            
    def _set_status(self, status):
        self.ntal_status = status

    def shutdownNtClient(self):
        try:
            self._set_status(self.STATUS_CLIENT_STOPPING)
            NetworkTable.shutdown()
            self._set_status(self.STATUS_CLIENT_STOPPED)
        except Exception as e:
            self._set_status(self.STATUS_ERROR)
            self.logger.error(str(e))

    def startNtClient(self):

        if self.ntal_status is not self.STATUS_CLIENT_STARTED_CONNECTING and not NetworkTable.isConnected():
            self._set_status(self.STATUS_CLIENT_STARTING)
            try:
                NetworkTable.setIPAddress(self.address)
                NetworkTable.setClientMode()
                NetworkTable.setUpdateRate(interval=self.flush_period)
                NetworkTable.initialize()
                self.nt = NetworkTable.getTable('DriverStationControlBoard')
                self._set_status(self.STATUS_CLIENT_STARTED_CONNECTING)
            except Exception as e:
                self._set_status(self.STATUS_ERROR)
                self.logger.error(str(e))

    def log_status_changes(self):
        status = self._get_status()
        if status != self.last_ntal_log_status or self.address != self.last_address:
            if status == self.STATUS_CLIENT_CONNECTED:
                self.logger.info('Connected to %s' % self.nt.getRemoteAddress())
            if status == self.STATUS_CLIENT_STARTED_CONNECTING and self.last_ntal_log_status == self.STATUS_CLIENT_CONNECTED:
                self.logger.info('Disconnected')
            if status == self.STATUS_CLIENT_STARTED_CONNECTING:
                self.logger.info('Trying to connect to %s' % self.address)
            if status == self.STATUS_CLIENT_STOPPED:
                self.logger.info('Disabled')

            self.last_address = self.address
            self.last_ntal_log_status = status

    def reset_table(self):
        self.logger.debug('Resetting the NT variables')
        self.sw_vals_out.clear()
        self.led_vals_in.clear()
        self.ana_vals_out.clear()
        self.pwm_vals_in.clear()
        self.cbhal_handler.get_cbhal().reset_values()

        self.sw_vals_out.extend(self.cbhal_handler.get_cbhal().getSwitchValues())
        self.led_vals_in.extend(self.cbhal_handler.get_cbhal().getLedValues())
        self.ana_vals_out.extend(self.cbhal_handler.get_cbhal().getAnalogValues())
        self.pwm_vals_in.extend(self.cbhal_handler.get_cbhal().getPwmValues())

        self.nt.putBooleanArray(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putBooleanArray(self.LED_IN, self.led_vals_in)
        self.nt.putNumberArray(self.ANALOG_OUT, self.ana_vals_out)
        self.nt.putNumberArray(self.PWM_IN, self.pwm_vals_in)

    def get_status(self):
        self.log_status_changes()
        return self._get_status()

    def _get_status(self):
        if self.ntal_status == self.STATUS_CLIENT_STARTED_CONNECTING and self.nt.isConnected():
            return self.STATUS_CLIENT_CONNECTED
        else:
            return self.ntal_status

    def getNtData(self):
        # Data In
        self.nt.getBooleanArray(self.LED_IN, self.led_vals_in)
        self.nt.getNumberArray(self.PWM_IN, self.pwm_vals_in)
        self.cbhal_handler.get_cbhal().putLedValues(self.led_vals_in)
        self.cbhal_handler.get_cbhal().putPwmValues(self.pwm_vals_in)

    def putNtData(self):
        # Data Out
        self.sw_vals_out.clear()
        self.ana_vals_out.clear()
        self.sw_vals_out.extend(self.cbhal_handler.get_cbhal().getSwitchValues())
        self.ana_vals_out.extend(self.cbhal_handler.get_cbhal().getAnalogValues())
        self.nt.putBooleanArray(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putNumberArray(self.ANALOG_OUT, self.ana_vals_out)

    def update(self):
        self.putNtData()
        self.getNtData()




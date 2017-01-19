import logging
logger = logging.getLogger(__name__)

import wx

from networktables import NetworkTable

class NetworkTableAbstractionLayer():

    SWITCH_OUT = 'Switch'
    ANALOG_OUT = 'Analog'
    PWM_IN = 'PWM'
    LED_IN = 'LED'

    def __init__(self, address, hal, flush_period=50e-3):
        '''

        :param address: str
        :param hal: HAL
        :param flush_period: int
        '''

        self.address = None
        self.flush_period = flush_period

        self.setNtServerAddress(address)

        self.nt = NetworkTable.getTable('DriverStationControlBoard')

        self.hal = hal

        self.sw_vals_out = []
        self.led_vals_in = []
        self.ana_vals_out = []
        self.pwm_vals_in = []
        self.reset_table()

    def getNtServerAddress(self):
        return self.address

    def setNtServerAddress(self, new_address):
        wx.LogVerbose('Changing NT server address from \"%s\" to \"%s\"' % (self.address, new_address))
        self.address = new_address
        NetworkTable.shutdown()
        NetworkTable.setIPAddress(self.address)
        NetworkTable.setClientMode()
        NetworkTable.setUpdateRate(interval=self.flush_period)
        NetworkTable.initialize()

    def reset_table(self,):

        self.sw_vals_out.clear()
        self.led_vals_in.clear()
        self.ana_vals_out.clear()
        self.pwm_vals_in.clear()

        self.hal.reset_values()

        self.sw_vals_out.extend(self.hal.getSwitchValues())
        self.led_vals_in.extend(self.hal.getLedValues())
        self.ana_vals_out.extend(self.hal.getAnalogValues())
        self.pwm_vals_in.extend(self.hal.getPwmValues())

        self.nt.putBooleanArray(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putBooleanArray(self.LED_IN, self.led_vals_in)
        self.nt.putNumberArray(self.ANALOG_OUT, self.ana_vals_out)
        self.nt.putNumberArray(self.PWM_IN, self.pwm_vals_in)
        wx.LogVerbose('The Control Board values in the Network Table have been reset.')

    def isConnected(self):
        return self.nt.isConnected()

    def getNtData(self):
        # Data In
        self.nt.getBooleanArray(self.LED_IN, self.led_vals_in)
        self.nt.getNumberArray(self.PWM_IN, self.pwm_vals_in)
        self.hal.putLedValues(self.led_vals_in)
        self.hal.putPwmValues(self.pwm_vals_in)

    def putNtData(self):
        # Data Out
        self.sw_vals_out.clear()
        self.ana_vals_out.clear()
        self.sw_vals_out.extend(self.hal.getSwitchValues())
        self.ana_vals_out.extend(self.hal.getAnalogValues())
        self.nt.putBooleanArray(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putNumberArray(self.ANALOG_OUT, self.ana_vals_out)

    def update(self):
        self.putNtData()
        self.getNtData()




from networktables import NetworkTable
# from networktables2.type import BooleanArray, NumberArray

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

        self.flush_period = flush_period

        NetworkTable.setIPAddress(address)
        NetworkTable.setClientMode()
        NetworkTable.setUpdateRate(interval=self.flush_period)
        # NetworkTable.setWriteFlushPeriod(flushPeriod=flush_period)
        NetworkTable.initialize()

        self.nt = NetworkTable.getTable('DriverStationControlBoard')

        self.hal = hal

        self.sw_vals_out = []
        self.led_vals_in = []
        self.ana_vals_out = []
        self.pwm_vals_in = []
        self.reset_table()

    def getNtServerAddress(self):
        return NetworkTable.getRemoteAddress()


    def setNtServerAddress(self, address):
        NetworkTable.shutdown()
        NetworkTable.setIPAddress(address)
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

    def isConnected(self):
        return self.nt.isConnected()

    def getNtServerAddress(self):
        return self.nt.getRemoteAddress()

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




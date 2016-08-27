from networktables import NetworkTable
from networktables2.type import BooleanArray, NumberArray

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
        NetworkTable.setIPAddress(address)
        NetworkTable.setClientMode()
        NetworkTable.setWriteFlushPeriod(flushPeriod=flush_period)
        NetworkTable.initialize()

        self.nt = NetworkTable.getTable('DriverStationControlBoard')

        self.hal = hal

        self.sw_vals_out = BooleanArray()
        self.led_vals_in = BooleanArray()
        self.ana_vals_out = NumberArray()
        self.pwm_vals_in = NumberArray()
        self.reset_table()


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

        self.nt.putValue(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putValue(self.LED_IN, self.led_vals_in)
        self.nt.putValue(self.ANALOG_OUT, self.ana_vals_out)
        self.nt.putValue(self.PWM_IN, self.pwm_vals_in)

    def isConnected(self):
        return self.nt.isConnected()

    def update(self):

        # Data Out
        self.sw_vals_out.clear()
        self.ana_vals_out.clear()
        self.sw_vals_out.extend(self.hal.getSwitchValues())
        self.ana_vals_out.extend(self.hal.getAnalogValues())
        self.nt.putValue(self.SWITCH_OUT, self.sw_vals_out)
        self.nt.putValue(self.ANALOG_OUT, self.ana_vals_out)

        # Data In
        self.nt.getValue(self.LED_IN, self.led_vals_in)
        self.nt.getValue(self.PWM_IN, self.pwm_vals_in)
        self.hal.putLedValues(self.led_vals_in)
        self.hal.putPwmValues(self.pwm_vals_in)


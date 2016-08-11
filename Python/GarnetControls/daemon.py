import GUI
import HAL
from networktables import NetworkTable
import logging
import time

debug = True

# address = 'roborio-4901-frc.local'

address = '192.168.56.1'

logging.basicConfig(level=logging.DEBUG)

class GarnetControlsDaemon:

    def __init__(self, address):
        self.hal = HAL.HAL(debug=debug)
        NetworkTable.setIPAddress(address)
        NetworkTable.setClientMode()
        NetworkTable.initialize()
        self.nt = NetworkTable.getTable('GarnetControls')
        self.run = True
        self.hal.set_event_handler(self.update)

    def main(self):
        self.hal.start()

        while self.run:
            try:
                print('Connected?', self.nt.isConnected())
                time.sleep(1)

            except KeyboardInterrupt:
                self.run = False
            except Exception as e:
                print('Error:', e)

        self.hal.stop()


    def update(self):
        for array_index in range(self.hal.SWITCH_INPUTS):
            self.nt.putBoolean('Switch_'+str(array_index), self.hal.switch_in[array_index])

        for array_index in range(self.hal.ANALOG_INPUTS):
            self.nt.putNumber('Analog_'+str(array_index), self.hal.analog_in[array_index])

        for array_index in range(self.hal.LED_OUTPUTS):
            self.hal.switch_in[array_index] = self.nt.getBoolean('LED_'+str(array_index), defaultValue=False)

        for array_index in range(self.hal.PWM_OUTPUTS):
            self.hal.switch_in[array_index] = int(self.nt.getNumber('PWM_' + str(array_index), defaultValue=0))

if __name__ == '__main__':
    gcd = GarnetControlsDaemon(address=address)
    gcd.main()
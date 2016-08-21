import GUI
import HAL
import GarnetControlsNT
import time

debug = True

# address = 'roborio-4901-frc.local'

# address = '10.242.64.36'
address = 'localhost'
class GarnetControlsDaemon:

    def __init__(self, address):
        self.hal = HAL.HAL(debug=debug)
        self.nt = GarnetControlsNT.GarnetControlsNT(address=address, hal=self.hal)
        self.run = True
        self.hal.set_event_handler(self.nt.update)

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




if __name__ == '__main__':
    gcd = GarnetControlsDaemon(address=address)
    gcd.main()

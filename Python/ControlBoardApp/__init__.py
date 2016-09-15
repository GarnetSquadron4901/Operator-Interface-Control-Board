from ControlBoardApp import main_window
from ControlBoardApp import ntal
import wx
import sys

ADDRESS = 'robiorio-4901-frc.local'

if len(sys.argv) >= 2:
    sim = (sys.argv[1].lower() == 'simulator')
else:
    sim = False

if sim:
    print ('Starting in simulator mode.')
    from ControlBoardApp.hal.Simulator import *
else:
    print ('Staring in real device mode.')
    from ControlBoardApp.hal.ControlBoard_1v1 import *

def main():

    app = wx.App()
    cb_hal = HardwareAbstractionLayer(debug=True)
    print('Control Board:', cb_hal.get_type())
    nt = ntal.NetworkTableAbstractionLayer(address=ADDRESS, hal=cb_hal)
    frame = main_window.MainWindow(hal=cb_hal, nt=nt)
    cb_hal.set_event_handler(frame.event_responder)

    cb_hal.start()
    if cb_hal.is_simulator():
        sim = SimulatorFrame(frame, cb_hal)
        cb_hal.set_sim_connection(sim)
        sim.Show()
    frame.Show()

    app.MainLoop()

    cb_hal.stop()
    if cb_hal.is_simulator():
        sim.Hide()
        sim.Destroy()

if __name__ == "__main__":
    main()
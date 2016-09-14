from ControlBoardApp import main_window
from ControlBoardApp.hal.Simulator import HardwareAbstractionLayer, SimulatorFrame
# from ControlBoardApp.hal.ControlBoard_1v1 import HardwareAbstractionLayer
from ControlBoardApp import ntal
import wx

ADDRESS = 'robiorio-4901-frc.local'
# CB_TYPE = 'ControlBoard_1v1'
CB_TYPE = 'Simulator'

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
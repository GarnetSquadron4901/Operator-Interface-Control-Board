from ControlBoardApp import main_window
from ControlBoardApp.hal.ControlBoard_1v1 import HardwareAbstractionLayer
from ControlBoardApp import ntal
import wx

ADDRESS = 'robiorio-4901-frc.local'
# CB_TYPE = 'ControlBoard_1v1'
CB_TYPE = 'Simulator'

def main():
    cb_hal = HardwareAbstractionLayer()
    print('Control Board:', cb_hal.get_type())
    nt = ntal.NetworkTableAbstractionLayer(address=ADDRESS, hal=cb_hal)
    app = wx.App()
    frame = main_window.MainWindow(hal=cb_hal, nt=nt)
    cb_hal.set_event_handler(frame.event_responder)
    cb_hal.start()
    frame.Show()
    app.MainLoop()
    cb_hal.stop()
    main_window.main()

if __name__ == "__main__":
    main()
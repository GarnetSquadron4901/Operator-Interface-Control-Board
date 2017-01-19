import logging
logger = logging.getLogger(__name__)

import main_window
import ntal
import sys
from config import ConfigFile
import wx
import cbhal


if len(sys.argv) >= 2:
    sim = (sys.argv[1].lower() == 'simulator')
else:
    sim = False

print('CBHAL Plugins:', cbhal.types.keys())

if sim:
    logger.log(logging.INFO, 'Starting in simulator mode.')
    sel_cb_hal = cbhal.types['Simulator']
    # from cbhal.Simulator import *
else:
    logger.log(logging.INFO, 'Starting in real device mode.')
    sel_cb_hal = cbhal.types['ControlBoard_1v1']
    # from cbhal.ControlBoard_1v1 import *


def main():
    logger.log(logging.DEBUG, 'Main started.')
    app = wx.App(False)
    app_config = ConfigFile(None)
    cb_hal_inst = sel_cb_hal.HardwareAbstractionLayer()
    logger.log(logging.INFO, 'Control Board: %s' % cb_hal_inst.get_type())
    nt = ntal.NetworkTableAbstractionLayer(address=app_config.get_nt_server_address(), hal=cb_hal_inst)
    frame = main_window.MainWindow(hal=cb_hal_inst, nt=nt, config=app_config)
    cb_hal_inst.set_event_handler(frame.event_responder)

    cb_hal_inst.start()
    if cb_hal_inst.is_simulator():
        sim = sel_cb_hal.SimulatorFrame(frame, cb_hal_inst)
        cb_hal_inst.set_sim_connection(sim)
        sim.Show()

    app.MainLoop()

    cb_hal_inst.stop()

if __name__ == "__main__":
    main()

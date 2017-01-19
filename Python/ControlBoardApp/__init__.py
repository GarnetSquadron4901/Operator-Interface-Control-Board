import logging
logger = logging.getLogger(__name__)

import wx

from ControlBoardApp.main_window import MainWindow
from ControlBoardApp.ntal import NetworkTableAbstractionLayer
from ControlBoardApp.config import ConfigFile
from ControlBoardApp.cbhal import cbtypes

def main():
    logger.log(logging.DEBUG, 'Main started.')
    app = wx.App(False)
    app_config = ConfigFile(None)
    cb_hal_inst = cbtypes[app_config.get_cb_type()]['module'].HardwareAbstractionLayer()
    logger.log(logging.INFO, 'Control Board: %s' % cb_hal_inst.get_type())
    nt = NetworkTableAbstractionLayer(address=app_config.get_nt_server_address(), hal=cb_hal_inst)
    frame = MainWindow(hal=cb_hal_inst, nt=nt, config=app_config)
    cb_hal_inst.set_event_handler(frame.event_responder)

    cb_hal_inst.start()
    if cb_hal_inst.is_simulator():
        sim = cbtypes[app_config.get_cb_type()]['module'].SimulatorFrame(frame, cb_hal_inst)
        cb_hal_inst.set_sim_connection(sim)
        sim.Show()

    app.MainLoop()

    cb_hal_inst.stop()

if __name__ == "__main__":
    main()

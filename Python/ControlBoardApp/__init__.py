import logging
import logging.config

dictLogConfig = {
        "version": 1,
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": "test.log"
            },
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "formatter": "myFormatter"
            }
        },
        "loggers": {
            '': {
                "handlers": ["fileHandler", "consoleHandler"],
                "level": "DEBUG",
            }
        },

        "formatters": {
            "myFormatter": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }

logging.config.dictConfig(dictLogConfig)


import wx
import sys
import networktables.version as ntver

from ControlBoardApp import _version as ntcbaver
from ControlBoardApp.main_window import MainWindow
from ControlBoardApp.ntal import NetworkTableAbstractionLayer
from ControlBoardApp.config import ConfigFile
from ControlBoardApp.cbhal import cbtypes, scan_for_hal_interfaces

logger = logging.getLogger(__name__)

def main():
    # Log version information
    logger.info('Main started')
    logger.info('Control Board Application Version: %s' % str(ntcbaver.__version__))
    logger.info('Python Version: %s' % str(sys.version.split()[0]))
    logger.info('wxPython Version: %s' % str(wx.VERSION_STRING))
    logger.info('pynetworktable Version: %s' % str(ntver.__version__))

    # Create the wx App
    app = wx.App(False)



    # Scan for HALs
    scan_for_hal_interfaces()

    # Get the config
    app_config = ConfigFile()

    # Load the selected HAL
    #TODO: Figure out a way to load the cb_hal_inst dynamically to change it during runtime
    cb_hal_inst = cbtypes[app_config.get_cb_type()]['module'].HardwareAbstractionLayer()

    # Load NTAL
    nt = NetworkTableAbstractionLayer(address=app_config.get_nt_server_address(), hal=cb_hal_inst)

    # Load the main window
    frame = MainWindow(hal=cb_hal_inst, nt=nt, config=app_config)

    # Pass the main window's event_responder to HAL
    cb_hal_inst.set_event_handler(frame.event_responder)

    # Start HAL
    cb_hal_inst.start()

    # If HAL is simulated, show the simulator window
    if cb_hal_inst.is_simulator():
        sim = cbtypes[app_config.get_cb_type()]['module'].SimulatorFrame(frame, cb_hal_inst)
        cb_hal_inst.set_sim_connection(sim)
        sim.Show()

    # Start the GUI
    app.MainLoop()

    # GUI closed, stop HAL
    cb_hal_inst.stop()

if __name__ == "__main__":
    main()

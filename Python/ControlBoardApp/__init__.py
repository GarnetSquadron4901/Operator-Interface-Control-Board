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
from ControlBoardApp.cbhal import ControlBoardHalInterfaceHandler

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

    # Get the config
    app_config = ConfigFile()

    # Load the selected HAL
    #TODO: Figure out a way to load the cb_hal_inst dynamically to change it during runtime
    # Scan for HALs
    cbhal_handler = ControlBoardHalInterfaceHandler()

    if app_config in cbhal_handler.get_types():
        cbhal_handler.init_cbtype_inst(app_config.get_cb_type())
    else:
        logger.error('The saved config type does not exist. Picking another config.')
        default_cb_type = list(cbhal_handler.get_types().keys())[0]
        cbhal_handler.init_cbtype_inst(default_cb_type)
        app_config.set_cb_type(default_cb_type)

    # Load NTAL
    nt = NetworkTableAbstractionLayer(address=app_config.get_nt_server_address(), cbhal_handler=cbhal_handler)

    # Load the main window
    main_window_inst = MainWindow(cbhal_handler=cbhal_handler, nt=nt, config=app_config)

    # Pass the main window's event_responder to HAL
    cbhal_handler.set_main_window(main_window_inst)
    cbhal_handler.set_event_handler(main_window_inst.event_responder)

    # Start HAL
    cbhal_handler.start_cbhal()

    # Start the GUI
    app.MainLoop()

    # GUI closed, stop HAL
    cbhal_handler.shutdown_cbhal()

if __name__ == "__main__":
    main()

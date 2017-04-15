import logging
import logging.config
import os

APP_NAME = 'ControlBoardApp'

LOG_PATH = os.path.join(os.path.expanduser('~'), APP_NAME+'.log')
CONFIG_PATH = os.path.join(os.path.expanduser('~'), APP_NAME+'.xml')

import wx
import sys
import networktables.version as ntver

from ControlBoardApp import _version as cbaver
from ControlBoardApp.main_window import MainWindow
from ControlBoardApp.ntal import NetworkTableAbstractionLayer
from ControlBoardApp.config import ConfigFile
from ControlBoardApp.cbhal import ControlBoardHalInterfaceHandler



dictLogConfig = {
        "version": 1,
        "handlers": {
            "fileHandler": {
                "class": "logging.FileHandler",
                "formatter": "myFormatter",
                "filename": LOG_PATH
            },
            "consoleHandler": {
                "class": "logging.StreamHandler",
                "formatter": "myFormatter"
            }

        },
        "loggers": {
            '': {
                "handlers": ["fileHandler", "consoleHandler"],
                "level": ConfigFile().get_logging_level(),
            }
        },

        "formatters": {
            "myFormatter": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    }

logging.config.dictConfig(dictLogConfig)

logger = logging.getLogger(__name__)

def main():
    # Log version information
    logger.info('Main started')
    logger.info('Control Board Application Version: %s' % str(cbaver.__version__))
    logger.info('Python Version: %s' % str(sys.version.split()[0]))
    logger.info('wxPython Version: %s' % str(wx.VERSION_STRING))
    logger.info('pynetworktable Version: %s' % str(ntver.__version__))

    # Create the wx App
    app = wx.App(False)

    # Get the config
    app_config = ConfigFile(CONFIG_PATH)

    # Scan for HALs
    cbhal_handler = ControlBoardHalInterfaceHandler()

    # Load the selected HAL
    if app_config.get_cb_type() in cbhal_handler.get_keys():
        cbhal_handler.init_cbtype_inst(app_config.get_cb_type())
    else:
        logger.error('The saved config type (%s) does not exist in %s. Picking \"%s\".' % (app_config.get_cb_type(), str(cbhal_handler.get_keys()), cbhal_handler.get_keys()[0]))
        default_cb_type = cbhal_handler.get_keys()[0]
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

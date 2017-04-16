import logging
import logging.config
import os
import sys

APP_NAME = 'Operator Interface Control Board'
EXE_NAME = APP_NAME.replace(' ', '')

LOG_PATH = os.path.abspath(os.path.join(os.path.expanduser('~'), EXE_NAME + '.log'))
CONFIG_PATH = os.path.abspath(os.path.join(os.path.expanduser('~'), EXE_NAME + '.xml'))


import wx
import sys
import networktables.version as ntver

if getattr(sys, 'frozen', False):
    # Normal Mode
    HELP_PATH = os.path.abspath(os.path.join(os.path.dirname(sys.executable), 'help.pdf'))
    from ControlBoardApp import version as cbaver
    from ControlBoardApp.main_window import MainWindow
    from ControlBoardApp.ntal import NetworkTableAbstractionLayer
    from ControlBoardApp.config import ConfigFile
    from ControlBoardApp.cbhal import ControlBoardHalInterfaceHandler

else:
    # Test Mode
    HELP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\', 'help.pdf'))
    import version as cbaver
    from main_window import MainWindow
    from ntal import NetworkTableAbstractionLayer
    from config import ConfigFile
    from cbhal import ControlBoardHalInterfaceHandler

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

# Configure logging
logging.config.dictConfig(dictLogConfig)
# Create a logger for main
logger = logging.getLogger(__name__)


def main():
    """
    Main function. It all starts here.
    
    :return: 
    """
    # Log version information
    logger.info('Main started')
    logger.info('%s Version: %s' % (APP_NAME, str(cbaver.__version__)))
    logger.info('Python Version: %s' % str(sys.version.split()[0]))
    logger.info('wxPython Version: %s' % str(wx.VERSION_STRING))
    logger.info('pynetworktable Version: %s' % str(ntver.__version__))

    # Log file locations
    logger.info('Config File: %s' % CONFIG_PATH)
    logger.info('Log File: %s' % LOG_PATH)
    logger.info('Help File: %s' % HELP_PATH)

    # Create the wx App
    app = wx.App(False)

    # Get the config
    app_config = ConfigFile()

    # Scan for HALs
    cbhal_handler = ControlBoardHalInterfaceHandler()

    # Load the selected HAL
    if app_config.get_cb_type() in cbhal_handler.get_keys():
        cbhal_handler.init_cbtype_inst(app_config.get_cb_type())
    else:
        logger.error('The saved config type (%s) does not exist in %s. Picking \"%s\".' % (
        app_config.get_cb_type(), str(cbhal_handler.get_keys()), cbhal_handler.get_keys()[0]))
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
    if cbhal_handler.is_valid():
        cbhal_handler.shutdown_cbhal()


if __name__ == "__main__":
    main()

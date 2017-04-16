import logging
import os
import importlib


class ControlBoardHalInterfaceHandler:
    """
    This class parses the cbhal folder to look for different control board interfaces. It handles setting up the class
    instance as well as starting and stopping the Control Board Hardware Abstraction Layer (CBHAL)
    """

    def __init__(self):
        self.logger = logging.getLogger('ControlBoardHalInterfaceHandler')
        self.main_window = None
        self.cbtypes = {}
        self.cbhal_inst = None
        self.scan_for_hal_interfaces()
        self.event_handler = None
        self.cb_sname = None
        self.cbhal = None
        self.sim = None

    def scan_for_hal_interfaces(self):
        """
        Scans through the cbhal folder to find the all the HAL interfaces.
        :return: 
        """
        # Scan for HAL interfaces
        self.logger.info('Scanning %s for HAL interfaces' % os.path.dirname(__file__))
        pluginfiles = [pyfile for pyfile in os.listdir(os.path.dirname(__file__)) if
                       not pyfile.startswith('__') and (pyfile.endswith('.pyc') or pyfile.endswith('.py'))]
        from_module = lambda fp: '.' + os.path.splitext(fp)[0]
        plugins = map(from_module, pluginfiles)

        # import parent module / namespace
        importlib.import_module(__package__)
        for plugin in plugins:
            cb = importlib.import_module(plugin, package=__package__)
            if hasattr(cb, 'CB_SNAME') and hasattr(cb, 'CB_LNAME'):
                self.logger.info('  Found: %s' % cb.CB_LNAME)
                self.cbtypes.update({cb.CB_SNAME: {'name': cb.CB_LNAME, 'module': cb}})
        self.logger.info('Done scanning for HAL interfaces.')

    def get_types(self):
        """
        Returns the different control board types
        :return: dict - A dictionary of control board short names with a dictionary with their long name [name] and the class module [module] 
        """
        return self.cbtypes

    def get_keys(self):
        """
        Returns a list of different control board types using their short name (CB_SNAME)
        :return: list - List of different control board type short names
        """
        if any(self.cbtypes.keys()):
            return sorted(list(self.cbtypes.keys()))
        else:
            raise (IndexError('No control board plugin instances found.'))

    def set_event_handler(self, event_handler):
        """
        Sets the event handler to process new data.
        :param event_handler: The function to call when new data arrives.
        :return: 
        """
        self.event_handler = event_handler

    def start_cbhal(self):
        """
        Starts the CBHAL
        :return: 
        """
        if self.cbhal_inst is None:
            raise ReferenceError('The init_cbtype_inst method must be called prior to start_cbhal')

        if self.event_handler is None:
            raise ReferenceError('The event responder must be set before instantiating a new CB HAL')

        self.cbhal.set_event_handler(self.event_handler)
        self.cbhal.start()

        # If HAL is simulated, show the simulator window
        if self.cbhal.is_simulator():
            self.sim = self.get_module().SimulatorFrame(self.main_window, self.cbhal, self.get_cbhal_inst_name())
            self.cbhal.set_sim_connection(self.sim)
            self.sim.Show()

    def shutdown_cbhal(self):
        """
        Shuts down the CBHAL
        :return: 
        """
        if self.cbhal_inst is not None:
            self.logger.info('Shutting down HAL interface: %s')

        else:
            self.logger.warning('Shutdown called when no CB Instance was found')
            return

        if self.cbhal.is_simulator():
            self.sim.Hide()

        self.cbhal.stop()
        del self.cbhal
        self.cbhal = None
        self.cbhal_inst = None

    def init_cbtype_inst(self, cb_sname):
        """
        Initializes the CBHAL
        :param cb_sname: 
        :return: 
        """
        if cb_sname not in self.cbtypes:
            raise KeyError('Invalid CB type \"%s\"' % cb_sname)

        self.cb_sname = cb_sname

        if self.cbhal_inst is not None:
            self.shutdown_cbhal()

        self.cbhal_inst = self.cbtypes[self.cb_sname]
        self.cbhal = self.get_module().HardwareAbstractionLayer()

    def set_main_window(self, frame):
        """
        Sets the main window for the simulator frame.
        :param frame: 
        :return: 
        """
        self.main_window = frame

    def get_module(self):
        """
        Returns the current CBHAL module. Used to start the SimulatorFrame.
        :return: module
        """
        if self.cbhal_inst is not None:
            return self.cbhal_inst['module']
        else:
            raise UnboundLocalError('The cbhal is still null. Please call init_cbhal(\'CB_SNAME\') first.')

    def get_cbhal(self):
        """
        Returns the current CBHAL instance
        :return: ControlBoardBase
        """
        if self.cbhal_inst is not None:
            return self.cbhal
        else:
            raise UnboundLocalError('The cbhal is still null. Please call init_cbhal(\'CB_SNAME\') first.')

    def get_cbhal_inst_name(self):
        """
        Returns the CBHAL Long Name
        :return: str
        """
        if self.cbhal_inst is not None:
            return self.cbhal_inst['name']
        else:
            raise UnboundLocalError('The cbhal_inst is still null. Please call start_cbhal(\'CB_SNAME\') first.')

    def get_cbhal_inst_sname(self):
        """
        Returns the CBHAL Short Name
        :return: str
        """
        if self.cbhal_inst is not None:
            return self.cb_sname
        else:
            raise UnboundLocalError('The cbhal_inst is still null. Please call start_cbhal(\'CB_SNAME\') first.')

    def is_valid(self):
        """
        Returns if the CBHAL is valid. 
        :return: bool
        """
        return self.cbhal is not None

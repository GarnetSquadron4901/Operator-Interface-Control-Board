import logging

logger = logging.getLogger(__name__)
import os
import importlib

class ControlBoardHalInterfaceHandler:
    def __init__(self):
        self.cbtypes = {}
        self.cbhal_inst = None
        self.scan_for_hal_interfaces()
        self.event_handler = None
        self.cb_sname = None
        self.sim = None

    def scan_for_hal_interfaces(self):
        global cbtypes
        logger.info('Scanning %s for HAL devices' % os.path.dirname(__file__))
        pluginfiles = pyfiles = [pyfile for pyfile in os.listdir(os.path.dirname(__file__)) if not pyfile.startswith('__') and pyfile.endswith('.pyc')]
        from_module = lambda fp: '.' + os.path.splitext(fp)[0]
        plugins = map(from_module, pluginfiles)
        # import parent module / namespace
        importlib.import_module(__package__)
        for plugin in plugins:
            cb = importlib.import_module(plugin, package=__package__)
            if hasattr(cb, 'CB_SNAME') and hasattr(cb, 'CB_LNAME'):
                logger.info('Found: %s' % cb.CB_LNAME)
                self.cbtypes.update({cb.CB_SNAME: {'name': cb.CB_LNAME, 'module': cb}})
        logger.info('Done scanning for HAL devices.')

    def get_types(self):
        return self.cbtypes

    def get_keys(self):
        return sorted(list(self.cbtypes.keys()))

    def set_event_handler(self, event_handler):
        self.event_handler = event_handler

    def start_cbhal(self):

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
        if self.cbhal_inst is not None:
            logger.info('Shutting down HAL interface: %s')

        else:
            logger.warning('Shutdown called when no CB Instance was found')
            return

        if self.cbhal.is_simulator():
            self.sim.Hide()

        self.cbhal.stop()
        del self.cbhal
        self.cbhal = None
        self.cbhal_inst = None

    def init_cbtype_inst(self, cb_sname):
        if cb_sname not in self.cbtypes:
            raise KeyError('Invalid CB type \"%s\"' % cb_sname)

        self.cb_sname = cb_sname


        if self.cbhal_inst is not None:
           self.shutdown_cbhal()

        self.cbhal_inst = self.cbtypes[self.cb_sname]
        self.cbhal = self.get_module().HardwareAbstractionLayer()


    def set_main_window(self, frame):
        self.main_window = frame

    def get_module(self):
        if self.cbhal_inst is not None:
            return self.cbhal_inst['module']
        else:
            raise UnboundLocalError('The cbhal is still null. Please call init_cbhal(\'CB_SNAME\') first.')

    def get_cbhal(self):
        if self.cbhal_inst is not None:
            return self.cbhal
        else:
            raise UnboundLocalError('The cbhal is still null. Please call init_cbhal(\'CB_SNAME\') first.')

    def get_cbhal_inst_name(self):
        if self.cbhal_inst is not None:
            return self.cbhal_inst['name']
        else:
            raise UnboundLocalError('The cbhal_inst is still null. Please call start_cbhal(\'CB_SNAME\') first.')

    def get_cbhal_inst_sname(self):
        if self.cbhal_inst is not None:
            return self.cb_sname
        else:
            raise UnboundLocalError('The cbhal_inst is still null. Please call start_cbhal(\'CB_SNAME\') first.')

    def is_valid(self):
        return self.cbhal is not None



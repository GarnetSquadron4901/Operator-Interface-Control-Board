import logging

logger = logging.getLogger(__name__)
import os
import importlib

cbtypes = {}

def scan_for_hal_interfaces():
    global cbtypes
    logger.info('Scanning %s for HAL devices' % os.path.dirname(__file__))
    pluginfiles = pyfiles = [pyfile for pyfile in os.listdir(os.path.dirname(__file__)) if not pyfile.startswith('__') and pyfile.endswith('.py')]
    from_module = lambda fp: '.' + os.path.splitext(fp)[0]
    plugins = map(from_module, pluginfiles)
    # import parent module / namespace
    importlib.import_module(__package__)
    for plugin in plugins:
        cb = importlib.import_module(plugin, package=__package__)
        if hasattr(cb, 'CB_SNAME') and hasattr(cb, 'CB_LNAME'):
            logger.info('Found: %s' % cb.CB_LNAME)
            cbtypes.update({cb.CB_SNAME: {'name': cb.CB_LNAME, 'module': cb}})
    logger.info('Done scanning for HAL devices.')











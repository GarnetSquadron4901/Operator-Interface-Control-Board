import os
import importlib

pluginfiles = pyfiles = [pyfile for pyfile in os.listdir(os.path.dirname(__file__)) if not pyfile.startswith('__') and pyfile.endswith('.py')]
from_module = lambda fp: '.' + os.path.splitext(fp)[0]
plugins = map(from_module, pluginfiles)
# import parent module / namespace
importlib.import_module(__package__)
cbtypes = {}
for plugin in plugins:
    cb = importlib.import_module(plugin, package=__package__)
    if hasattr(cb, 'CB_SNAME') and hasattr(cb, 'CB_LNAME'):
        cbtypes.update({cb.CB_SNAME: {'name': cb.CB_LNAME, 'module': cb}})












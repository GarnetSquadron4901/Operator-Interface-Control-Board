import os
import importlib

pluginfiles = pyfiles = [pyfile for pyfile in os.listdir(os.path.dirname(__file__)) if not pyfile.startswith('__') and pyfile.endswith('.py')]
from_module = lambda fp: '.' + os.path.splitext(fp)[0]
plugins = map(from_module, pluginfiles)
# import parent module / namespace
importlib.import_module(__package__)
types = {}
for plugin in plugins:
    print('Checking:', plugin)
    cb = importlib.import_module(plugin, package=__package__)
    if hasattr(cb, 'CB_TYPE'):
        types.update({cb.CB_TYPE:cb})
    else:
        print(plugin, 'is not a CB type. Probably a parent class?')

print("types:", types)












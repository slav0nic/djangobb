# Module taken from Turbion blog engine

import os
import imp

class NoModuleError(Exception):
    """
    Custom exception class indicates that given module does not exit at all
    """
    pass

def get_module(base, module_name):
    try:
        base_path = __import__(base, {}, {}, [base.split('.')[-1]]).__path__
    except AttributeError:
        raise NoModuleError("Cannot load base `%s`" % base)

    try:
        imp.find_module(module_name, base_path)
    except ImportError:
        raise NoModuleError("Cannot find module `%s` in base `%s`" % (module_name, base))

    return getattr(__import__(base, {}, {}, [module_name]), module_name)

def get_module_attrs(base, module_name, filter=lambda attr: True):
    mod = get_module(base, module_name)

    try:
        attrs = mod.__all__
    except AttributeError:
        attrs = dir(mod)

    return dict([(name, getattr(mod, name)) for name in attrs if filter(getattr(mod, name))])

def list_sub_modules(base, module_name):
    mod = get_module(base, module_name)

    directory = os.path.dirname(os.path.abspath(mod.__file__))
    names = [name for name in os.listdir(directory) if name.endswith('.py') and name != '__init__.py']
    return [os.path.splitext(name)[0] for name in names]

def get_sub_modules(base, module_name):
    return [get_module("%s.%s" % (base, module_name), sub_mod_name)\
                    for sub_mod_name in list_sub_modules(base, module_name)]

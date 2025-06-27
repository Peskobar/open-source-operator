import importlib
import os
import pkgutil


def load_plugins():
    plugins = []
    pkg_dir = os.path.dirname(__file__)
    for mod in pkgutil.iter_modules([pkg_dir]):
        if mod.name.startswith('_'):
            continue
        module = importlib.import_module(f"plugins.{mod.name}")
        if hasattr(module, 'register'):
            plugins.append(module.register())
    return plugins

class Plugin:
    """Base plugin interface."""
    def register_actions(self):
        """Return a dict of custom actions."""
        return {}

    def memory_hook(self, memory):
        """Optional hook called with memory backend."""
        pass

import importlib
import pkgutil
import pathlib
from typing import List


def load_plugins(directory: str = None) -> List[Plugin]:
    """Auto discover plugins in the plugins folder."""
    plugins: List[Plugin] = []
    base = pathlib.Path(directory or pathlib.Path(__file__).resolve().parents[1] / "plugins")
    if not base.exists():
        return plugins
    for mod in pkgutil.iter_modules([str(base)]):
        if mod.name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"plugins.{mod.name}")
            if hasattr(module, "register"):
                plugin = module.register()
                if isinstance(plugin, Plugin):
                    plugins.append(plugin)
        except Exception as e:  # pragma: no cover - plugin errors shouldn't crash
            print(f"Failed to load plugin {mod.name}: {e}")
    return plugins

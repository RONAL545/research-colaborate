from importlib import import_module
from importlib.util import find_spec


def load_models():
    for module in ("auth", "projects", "events"):
        path = f"app.modules.{module}.models"
        if find_spec(path) is not None:
            import_module(path)

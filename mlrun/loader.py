"""Dynamic module loading for MLRun components.

These functions are essential to the operation of MLRun.
"""
from typing import Callable, Dict
import importlib.util
from pathlib import Path
import os
import pyclbr
from enum import Enum

from mlrun import strings


class ComponentType(Enum):
    """Component types for generic loader."""
    CAMERA = 0
    ENGINE = 1
    LOGGER = 2
    PUBLISHER = 3


def get_package(package_name: str, must_implement: str) -> Dict[str, str]:
    """
    Get the files within a directory which happen in have a class that implements a given class.
    (Whew, that is a mouthful...)
    Args:
        package_name: String name of the subpackage to enumerate over.
        must_implement: The name of the class that the returned classes must implement.
    Returns:
        A dictionary of the classes that happen to occur in the specified name.
    """
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return {}
    else:
        assert isinstance(spec.origin, str)
        pathname = Path(spec.origin).parent
        ret = {}
        with os.scandir(pathname) as entries:
            for entry in entries:
                if entry.name.startswith("__"):
                    continue
                current = ".".join((package_name, entry.name.partition(".")[0]))
                if entry.is_file():
                    if entry.name.endswith(".py"):
                        if "base" not in entry.name:
                            module_info = pyclbr.readmodule(current)
                            for value in module_info.values():
                                if value.super[0] == must_implement:  # type: ignore
                                    ret[current.split(".")[2]] = value.name
        return ret


def load_component(ctype: ComponentType, name: str) -> Callable:
    """
    Load a component from it's file.
    Args:
        ctype: Type of component.
        name: File name of component under a given category.

    Returns:
        The Callable init method of the class.
    """

    # Determine the needed parameters.
    if ctype == ComponentType.CAMERA:
        singular = "camera"
        package = "mlrun.cameras"
        base = "BaseCamera"
    elif ctype == ComponentType.ENGINE:
        singular = "engine"
        package = "mlrun.engines"
        base = "BaseEngine"
    elif ctype == ComponentType.LOGGER:
        singular = "logger"
        package = "mlrun.loggers"
        base = "BaseLogger"
    elif ctype == ComponentType.PUBLISHER:
        singular = "publisher"
        package = "mlrun.publishers"
        base = "BasePublisher"

    # Prevent importing the base class.
    if name == "base":
        raise ImportError(strings.error_base_import.format(component=singular))

    # Search for the correct package.
    components = get_package(package, base)

    # Enumerate over returned packages.
    for key, value in components.items():
        # If the name of the component we are searching for is matched,
        # import it and return its main module.
        if key == name:
            module = __import__(f"{package}.{key}", fromlist=[value])
            return getattr(module, value)
    raise ImportError(strings.error_component_not_found.format(component=singular, name=name))

"""Dynamic module loading for MLRun components.

These functions are essential to the operation of MLRun.
"""
from typing import Callable, Dict
import importlib.util
from pathlib import Path
import os
import pyclbr


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
                            if value.super[0] == must_implement:
                                ret[current.split(".")[2]] = value.name
    return ret


def load_logger(name: str) -> Callable:
    """
    Load a logging class by name from it's file.
    Args:
        name: Logger *file* name, not class name.

    Returns:
        Instance of BaseLogger that the logger inherits from; it is a Callable function because of __init__.
    """
    if name == "base":
        raise ImportError("You cannot import the base logger!")
    loggers = get_package("mlrun.loggers", "BaseLogger")
    for key, value in loggers.items():
        if key == name:
            logger_module = __import__(f"mlrun.loggers.{key}", fromlist=[value])
            return getattr(logger_module, value)
    raise ImportError(f"The requested logger, {name}, could not be found.")


def load_camera(name: str) -> Callable:
    """
    Load a camera class by name from it's file.
    Args:
        name: Camera *file* name, not class name.

    Returns:
        Instance of BaseCamera that the camera class inherits from; it is a callable function.
    """
    if name == "base":
        raise ImportError("You cannot import the base camera!")
    cameras = get_package("mlrun.cameras", "BaseCamera")
    for key, value in cameras.items():
        if key == name:
            camera_module = __import__(f"mlrun.cameras.{key}", fromlist=[value])
            return getattr(camera_module, value)
    raise ImportError(f"The requested camera, {name}, could not be found.")


def load_engine(name: str) -> Callable:
    """
    Load an engine by name from it's file.
    Args:
        name: Engine *file* name, not class name.

    Returns:
        Instance of BaseEngine that the engine inherits from; it is a callable function.
    """
    if name == "base":
        raise ImportError("You cannot import the base engine!")
    engines = get_package("mlrun.engines", "BaseEngine")
    for key, value in engines.items():
        if key == name:
            engine_module = __import__(f"mlrun.engines.{key}", fromlist=[value])
            return getattr(engine_module, value)
    raise ImportError(f"The requested engine, {name}, could not be found.")


def load_publisher(name: str) -> Callable:
    """
    Load a publisher by name from its file.
    Args:
        name: Publisher *file* name, not class name.

    Returns:
        Instance of BasePublisher that the publisher inherits from; it is a callable function.
    """
    if name == "base":
        raise ImportError("You cannot import the base publisher!")
    publishers = get_package("mlrun.publishers", "BasePublisher")
    for key, value in publishers.items():
        if key == name:
            publisher_module = __import__(f"mlrun.publishers.{key}", fromlist=[value])
            return getattr(publisher_module, value)
    raise ImportError(f"The requested publisher, {name}, could not be found.")
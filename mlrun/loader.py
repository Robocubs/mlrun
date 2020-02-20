"""Dynamic module loading for MLRun components.

These functions are essential to the operation of MLRun.
"""
from typing import Callable

from mlrun.loggers.base import BaseLogger


def load_logger(name: str) -> Callable:
    """
    Load a logging class by name from it's file.
    Args:
        name: Logger *file* name, not class name.

    Returns:
        Instance of BaseLogger that the logger inherits from;
        it is a Callable function because of __init__.
    """
    if name == "colored":
        file_name = "colored"
        class_name = "ColoredLogger"
    elif name == "standard":
        file_name = "standard"
        class_name = "StandardLogger"
    elif name == "base":
        raise ImportError("You cannot import the base logger!")
    logger_module = __import__(f"mlrun.loggers.{file_name}", fromlist=[class_name])
    return getattr(logger_module, class_name)

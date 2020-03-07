"""
This file defines the base logger class for MLRun.
All logging handlers should implement this logger.
"""
from abc import ABC, abstractmethod


class BaseLogger(ABC):
    """
    Base logging handler for MLRun.
    All logging handlers should implement this logger.
    """

    def __init__(self, *args, **kwargs):
        """
        Set up the logger.
        Args:
            logger: Logger to set up.
        """
        pass

    @abstractmethod
    def debug(self, msg: str, *args, **kwargs):
        """
        Generate a debug message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        pass

    @abstractmethod
    def info(self, msg: str, *args, **kwargs):
        """
        Generate an info message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        pass

    @abstractmethod
    def warning(self, msg: str, *args, **kwargs):
        """
        Generate a warning message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        pass

    @abstractmethod
    def error(self, msg: str, *args, **kwargs):
        """
        Generate an error message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        pass

    @abstractmethod
    def setLevel(self, level: str):
        """
        Set the minimum level on the logger.
        Args:
            level: One of DEBUG, INFO, WARNING, ERROR, or FATAL

        Returns:
            Nothing
        """
        pass

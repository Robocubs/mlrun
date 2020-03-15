"""
This file defines the most simple logger class for MLRun.
This is used by default.
"""
from .base import BaseLogger
import logging


class StandardLogger(BaseLogger):
    """
    The standard logger class for MLRun.
    """
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__), max_level: str = "DEBUG", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.max_level = max_level

    def debug(self, msg: str, *args: str):
        """
        Generate a debug message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        if self.max_level == "DEBUG":
            self.logger.debug(msg, *args)

    def info(self, msg: str, *args: str):
        """
        Generate an info message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.info(msg, *args)

    def warning(self, msg: str, *args: str):
        """
        Generate a warning message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.warning(msg, *args)

    def error(self, msg: str, *args: str):
        """
        Generate an error message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.error(msg, *args)

    def setLevel(self, level: str):
        """
        Set the minimum level on the logger.
        Args:
            level: One of DEBUG, INFO, WARNING, ERROR, or FATAL

        Returns:
            Nothing
        """
        self.logger.setLevel(level)


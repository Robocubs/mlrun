"""
This file defines the most simple logger class for MLRun.
This is used by default.
"""
from .base import BaseLogger
from logging import Logger


class StandardLogger(BaseLogger):
    """
    The standard logger class for MLRun.
    """
    def __init__(self, logger: Logger, max_level: str = "DEBUG", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.max_level = max_level

    def debug(self, msg: str, *args: str, **kwargs: int):
        """
        Generate a debug message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        if self.max_level == "DEBUG":
            self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: str, **kwargs: int):
        """
        Generate an info message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: str, **kwargs: int):
        """
        Generate a warning message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: str, **kwargs: int):
        """
        Generate an error message in the logger.

        Args:
            msg: Message to handle.

        Returns:
            Nothing, at least not in this case.
        """
        self.logger.error(msg, *args, **kwargs)
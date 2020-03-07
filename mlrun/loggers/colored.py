"""
This file defines the colored logger class for MLRun.
"""
from .base import BaseLogger
from mlrun import strings
import logging


class ColoredLogger(BaseLogger):
    """
    The colored logger class for MLRun.
    """
    def __init__(self, logger: logging.Logger = logging.getLogger(__name__), max_level: str = "DEBUG"):
        super().__init__(logger)
        self.max_level = max_level
        self.logger = logger
        # Install coloredlogs hook, if it exists.
        try:
            import coloredlogs
            coloredlogs.install(
                level="DEBUG",
                logger=self.logger,
                fmt="%(name)s %(levelname)s %(message)s"
            )
        except ImportError:
            self.warning(strings.warning_coloredlogs)

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

    def setLevel(self, level: str):
        """
        Set the minimum level on the logger.
        Args:
            level: One of DEBUG, INFO, WARNING, ERROR, or FATAL

        Returns:
            Nothing
        """
        self.logger.setLevel(level)

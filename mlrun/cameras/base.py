"""Basic capture device operator.

By default, this class does nothing. It implements an Iterator for the best possible performance.
"""
from abc import ABC, abstractmethod


class BaseCamera(ABC):
    """
    Basic capture device.

    Intentionally does nothing.
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Initialize the capture.
        Should only be used for variables.
        Args:
            Generified for your sanity.
        """
        pass

    @abstractmethod
    def enable(self, *args, **kwargs):
        """
        Enable the capture device.
        Usually gets a hook for the device and prepares
        it for reading.
        Args:
            Generic for your sanity.
        Returns:
            Usually nothing.
        """
        pass

    @abstractmethod
    def disable(self, *args, **kwargs):
        """
        Disable the capture device.
        Usually closes the hook for the device gracefully.
        Args:
            Generic for your sanity.
        Returns:
            Usually nothing.
        """
        pass

    @abstractmethod
    def read(self) -> bytes:
        """
        Read from camera stream.
        Returns:
            Bytes of camera stream.
        """
        pass

"""Base inferrer class for MLRun.

Nothing happens here.
"""
from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """
    Base inferrer class.

    Does nothing by design.
    """
    def __init__(self, *args, **kwargs):
        """Initialize whatever inference engine we use."""
        pass

    @abstractmethod
    def enable(self):
        """Enable the inference engine."""
        pass

    @abstractmethod
    def disable(self):
        """Disable the inference engine."""
        pass

    @abstractmethod
    def infer(self, *args, **kwargs):
        """Run inference on an object of some kind."""
        pass

"""Base publisher class for MLRun."""
from abc import ABC, abstractmethod
from typing import Callable, Union

from _pynetworktables import NetworkTable


class BasePublisher(ABC):
    """Base publisher class."""
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Initialize your publisher here."""
        pass

    @abstractmethod
    def enable(self, *args, **kwargs) -> Union[Callable, NetworkTable]:
        """Enable your publisher here."""
        pass

    @abstractmethod
    def disable(self, *args, **kwargs):
        """Disable your publisher here."""
        pass

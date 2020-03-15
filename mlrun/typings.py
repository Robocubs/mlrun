"""Miscellaneous support statements for Mypy in MLRun."""
from typing import Dict

from typing_extensions import TypedDict

# For whatever reason, PyCharm doesn't seem to understand these statements.
# So I told PyCharm to shove it.
# noinspection PyTypeChecker
LoggerConfiguration = TypedDict("LoggerConfiguration", {"name": str, "max_level": str})
# noinspection PyTypeChecker
CameraConfiguration = TypedDict("CameraConfiguration",
                                {"name": str, "id": int, "width": int, "height": int, "fps": int, "file": str})
# noinspection PyTypeChecker
EngineConfiguration = TypedDict("EngineConfiguration",
                                {"name": str, "path": str, "min_score": float, "width": int, "height": int})
# noinspection PyTypeChecker
PublisherConfiguration = TypedDict("PublisherConfiguration", {"name": str, "team": int, "table": str, "prefix": str})
# noinspection PyTypeChecker
Configuration = TypedDict("Configuration",
                          {"logger": LoggerConfiguration, "camera": CameraConfiguration, "engine": EngineConfiguration,
                           "publisher": PublisherConfiguration, "show": bool})
# noinspection PyTypeChecker
ConfigurationDictionary = Dict[str, Configuration]

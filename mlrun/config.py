"""Configurations for MLRun.

This file defines your configuration for MLRun. When running MLRun, pass a configuration name as the first argument.
"""
from typing import Dict, Union
from mlrun.loggers.base import BaseLogger

# Define type aliases to make reading the types less complicated.
# This is somewhat stupid, because it allows for non-specific typings of configuration objects.
# Unfortunately, both the Jetson and the Ubuntu 18.04 LTS developer workstation used by our team use Python 3.6.
# This means that I can't use TypedDict, and there isn't a backport available for it. *sigh*
Configuration = Dict[str, Dict[str, Union[BaseLogger, bool, int, str, float]]]
ConfigurationDictionary = Dict[str, Configuration]

# Define your configuration below in a new top-level dictionary entry.
configurations: ConfigurationDictionary = {
    "desktop": {
        "logger": {
            "name": "colored",
            "max_level": "DEBUG"
        },
        "camera": {
            "name": "opencv",
            "id": 0,
            "width": 320,
            "height": 240,
            "fps": 30,
            "file": "/home/nvidia/Videos/output/output.mp4"
        },
        "engine": {
            "name": "tensorflow",
            "path": "/home/nvidia/Documents/Programming/Python/MLRun/v2",
            "min_score": 0.7
        },
        "publisher": {
            "name": "networktables",
            "team": 1701,
            "table": "SmartDashboard",
            "prefix": "jetson"
        }
    },
    "jetson": {
        "logger": {
            "name": "colored",
            "max_level": "DEBUG"
        },
        "camera": {
            "name": "opencv",
            "id": 0,
            "width": 320,
            "height": 240,
            "fps": 30
        },
        "encoder": {
            "name": "opencv"
        },
        "engine": {
            "name": "tensorflow",
            "min_score": 0.7,
            "max_score": 1.0
        },
        "publisher": {
            "name": "networktables",
            "team": 1701,
            "table": "SmartDashboard",
            "prefix": "jetson"
        }
    }
}

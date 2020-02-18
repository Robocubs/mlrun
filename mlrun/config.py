"""Configuration for MLRun.

This file defines your configuration for MLRun.
"""
from typing import Dict, Union

configurations: Dict[str, Dict[str, Dict[str, Union[bool, int, str]]]] = {
    "desktop": {
        "tensorflow": {
            "print_deprecation_messages": False,
            "minimum_logging_level": 3,
            "compat": True,
            "model_path": "/home/nvidia/Documents/Programming/Python/MLRun/v2"
        },
        "camera": {
            "id": 0,
            "width": 320,
            "height": 240,
            "fps": 30
        },
        "networktables": {
            "enabled": False,
            "team": 1701,
            "table": "SmartDashboard",
            "keyPrefix": "jetson"
        },
        "debugging": {
            "logs": True,
            "show": False
        }
    },
    "jetson": {
        "tensorflow": {
            "print_deprecation_messages": False,
            "minimum_logging_level": 3,
            "compat": True,
            "model_path": "/home/nvidia/mlrun/mlrun/v2",
        },
        "camera": {
            "id": 2,
            "width": 320,
            "height": 240,
            "fps": 30
        },
        "networktables": {
            "enabled": True,
            "team": 1701,
            "table": "SmartDashboard",
            "keyPrefix": "jetson"
        },
        "debugging": {
            "logs": True,
            "show": False
        }
    }
}
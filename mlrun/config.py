"""Configurations for MLRun.

This file defines your configuration for MLRun. When running MLRun, pass a configuration name as the first argument.
"""
from mlrun.typings import ConfigurationDictionary
from typedconfig import Config, key, section, group_key


@section("logger")
class LoggerConfig(Config):
    name = key(cast=str)
    max_level = key(cast=str)


@section("camera")
class CameraConfig(Config):
    name = key(cast=str)
    id = key(cast=int)
    width = key(cast=int)
    height = key(cast=int)
    fps = key(cast=int)
    file = key(cast=str)


@section("engine")
class EngineConfig(Config):
    name = key(cast=str)
    path = key(cast=str)
    min_score = key(cast=float)
    width = key(cast=int)
    height = key(cast=int)


@section("publisher")
class PublisherConfig(Config):
    name = key(cast=str)
    team = key(cast=int)
    table = key(cast=str)
    prefix = key(cast=str)

class ConfigObject(Config):
    logger = group_key(LoggerConfig)
    camera = group_key(CameraConfig)
    engine = group_key(EngineConfig)
    publisher = group_key(PublisherConfig)
    show = key(cast=bool, section_name="debug")

# Define your configuration below in a new top-level dictionary entry.
configurations: ConfigurationDictionary = {
    "desktop": {
        "logger": {
            "name": "colored",
            "max_level": "INFO"
        },
        "camera": {
            "name": "file",
            "id": 0,
            "width": 1280,
            "height": 720,
            "fps": 30,
            "file": "/home/nvidia/demo_videos/720p.mp4"
        },
        "engine": {
            "name": "tensorflow",
            "path": "/home/nvidia/Documents/Programming/Python/MLRun/models/v1",
            "min_score": 0.3,
            "width": 1280,
            "height": 720
        },
        "publisher": {
            "name": "networktables",
            "team": 1701,
            "table": "SmartDashboard",
            "prefix": "jetson"
        },
        "show": True
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
            "fps": 30,
            "file": "/home/nvidia/demo_videos/720p.mp4"
        },
        "engine": {
            "name": "tflite",
            "path": "/home/nvidia/mlrun/models/v2tpu",
            "min_score": 0.7,
            "width": 192,
            "height": 192
        },
        "publisher": {
            "name": "networktables",
            "team": 1701,
            "table": "SmartDashboard",
            "prefix": "jetson"
        },
        "show": False
    }
}

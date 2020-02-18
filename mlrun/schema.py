# -*- coding: utf-8 -*-
"""MLRun configuration schema.

Provides for configuration validation to ensure no
errors occur, and simplifies actual config validation.
"""
schema: dict = {
    "$id": "http://example.com/root.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "definitions": {},
    "required": ["tensorflow", "logging", "camera", "networktables", "debugging"],
    "title": "The MLRun configuration schema.",
    "type": "object",
    "properties": {
        "camera": {
            "$id": "#/properties/camera",
            "required": ["id", "width", "height", "fps"],
            "title": "The camera configuration object.",
            "type": "object",
            "properties": {
                "id": {
                    "$id": "#/properties/camera/properties/id",
                    "default": 0,
                    "examples": range(0, 4),
                    "title": "The camera ID that OpenCV should be searching for.",
                    "type": "integer"
                },
                "width": {
                    "$id": "#/properties/camera/properties/width",
                    "default": 0,
                    "examples": [320, 864, 1280, 1920],
                    "title": "The expected width of the frame the camera provides.",
                    "type": "integer"
                },
                "height": {
                    "$id": "#/properties/camera/properties/height",
                    "default": 0,
                    "examples": [240, 480, 1280, 1920],
                    "title": "The expected height of the frame the camera provides.",
                    "type": "integer"
                },
                "fps": {
                    "$id": "#/properties/camera/properties/fps",
                    "default": 0,
                    "examples": range(5, 30, 5),
                    "title": "Expected FPS of video capture from camera input.",
                    "type": "integer"
                }
            }
        },
        "debugging": {
            "$id": "#/properties/debugging",
            "required": ["logs", "show"],
            "title": "The debugging configuration object.",
            "type": "object",
            "properties": {
                "logs": {
                    "$id": "#/properties/debugging/properties/logs",
                    "default": False,
                    "examples": [True],
                    "title": "Whether or not to enable debug logging.",
                    "type": "boolean"
                },
                "show": {
                    "$id": "#/properties/debugging/properties/show",
                    "default": False,
                    "examples": [True],
                    "title": "Whether or not to enable visualization of bounding boxes.",
                    "type": "boolean"
                }
            }
        },
        "logging": {
            "$id": "#/properties/logging",
            "required": ["log_level", "format"],
            "title": "The logging configuration object.",
            "type": "object",
            "properties": {
                "format": {
                    "$id": "#/properties/logging/properties/format",
                    "default": "",
                    "examples": ["%(name)s %(levelname)s %(message)s"],
                    "pattern": "^(.*)$",
                    "title": "The formatting string to be used when writing the logs to the console.",
                    "type": "string"
                },
                "log_level": {
                    "$id": "#/properties/logging/properties/log_level",
                    "default": "DEBUG",
                    "examples": ["DEBUG", "INFO", "WARNING", "ERROR"],
                    "pattern": "^(.*)$",
                    "title": "The maximum logging level to use. Should remain as DEBUG.",
                    "type": "string"
                }
            }
        },
        "networktables": {
            "$id": "#/properties/networktables",
            "required": ["enabled", "team", "table", "keyPrefix"],
            "title": "The NetworkTables config object.",
            "type": "object",
            "properties": {
                "enabled": {
                    "$id": "#/properties/networktables/properties/enabled",
                    "default": False,
                    "examples": [False, True],
                    "title": "Whether or not to enable NetworkTables support.",
                    "type": "boolean"
                },
                "keyPrefix": {
                    "$id": "#/properties/networktables/properties/keyPrefix",
                    "default": "jetson",
                    "examples": ["jetson"],
                    "pattern": "^(.*)$",
                    "title": "The prefix that all NetworkTables will have attached to them.",
                    "type": "string"
                },
                "table": {
                    "$id": "#/properties/networktables/properties/table",
                    "default": "SmartDashboard",
                    "examples": ["SmartDashboard"],
                    "pattern": "^(.*)$",
                    "title": "The table that NetworkTables values are written to. Should be SmartDashboard for "
                             "Shuffleboard visualizations.",
                    "type": "string"
                },
                "team": {
                    "$id": "#/properties/networktables/properties/team",
                    "default": 1701,
                    "examples": [33, 254, 1701],
                    "title": "Your team number for connecting to the RoboRIO NetworkTables server.",
                    "type": "integer"
                }
            }
        },
        "tensorflow": {
            "$id": "#/properties/tensorflow",
            "required": ["print_deprecation_messages", "minimum_logging_level", "compat", "model_path"],
            "title": "The TensorFlow configuration object.",
            "type": "object",
            "properties": {
                "compat": {
                    "$id": "#/properties/tensorflow/properties/compat",
                    "default": False,
                    "examples": [True, False],
                    "title": "Whether to enable compatibility mode. Enable if you are running on TF 1.15 or 2.x.",
                    "type": "boolean"
                },
                "minimum_logging_level": {
                    "$id": "#/properties/tensorflow/properties/minimum_logging_level",
                    "default": 0,
                    "examples": [1, 2, 3, 4],
                    "title": "The minimum logging level for tensorflow. Suggested value is 4 for performance reasons.",
                    "type": "integer"
                },
                "model_path": {
                    "$id": "#/properties/tensorflow/properties/model_path",
                    "default": "/home/nvidia/Documents/Programming/Python/MLRun/v2",
                    "examples": ["/home/nvidia/Documents/Programming/Python/MLRun/v2"],
                    "pattern": "^(.*)$",
                    "title": "The absolute path to the folder holding your model.",
                    "type": "string"
                },
                "print_deprecation_messages": {
                    "$id": "#/properties/tensorflow/properties/print_deprecation_messages",
                    "default": False,
                    "examples": [False],
                    "title": "Whether or not to print function deprecation warnings. Disabled by default.",
                    "type": "boolean"
                }
            }
        }
    }
}

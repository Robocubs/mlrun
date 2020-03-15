# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""

# Global modules
import pyximport  # type: ignore

from mlrun.typings import LoggerConfiguration, CameraConfiguration, EngineConfiguration, PublisherConfiguration

pyximport.install(language_level=3)

import logging
import sys

# Non-guarded imports
from cv2 import getTickFrequency, getTickCount, namedWindow, destroyAllWindows  # type: ignore

# Local imports
from mlrun import strings, config, loader, util, simple_util  # type: ignore
from mlrun.loader import ComponentType

# Determine the number of arguments.
if len(sys.argv) == 2:
    # Load the configuration.
    if config.configurations[sys.argv[1]]:
        loaded_config = config.configurations[sys.argv[1]]  # type: ignore
    else:
        print(strings.warning_config_name)
        loaded_config = config.configurations["desktop"]  # type: ignore
else:
    print(strings.warning_config_name)
    loaded_config = config.configurations["desktop"]

# Make some aliases for readability's sake.
logger_config: LoggerConfiguration = loaded_config["logger"]
camera_config: CameraConfiguration = loaded_config["camera"]
engine_config: EngineConfiguration = loaded_config["engine"]
publisher_config: PublisherConfiguration = loaded_config["publisher"]
# noinspection PyTypeChecker
show: bool = loaded_config["show"]
debug: bool = True if logger_config["max_level"] == "DEBUG" else False

#######################################################################################################
# All things requiring configuration go below here. The configuration isn't loaded before this point. #
#######################################################################################################
logger = loader.load_component(ComponentType.LOGGER, logger_config["name"])(
    logger=logging.getLogger("mlrun"),
    max_level=logger_config["max_level"]
)

# Disable TensorFlow mixed logging. This is important because TensorFlow will start logging random Python-based
# messages without these lines.
loader.load_component(ComponentType.LOGGER, logger_config["name"])(
    logger=logging.getLogger("tensorflow"),
    max_level=logger_config["max_level"]
).setLevel(logging.FATAL)

###########################################################################
# Start logging below, because the logger isn't loaded before this point. #
###########################################################################

logger.info(strings.mlrun_started)
if show:
    logger.warning(strings.warning_show_debug)

# Load the configured camera instance for reading.
if camera_config["name"] == "opencv":
    cam = loader.load_component(ComponentType.CAMERA, camera_config["name"])(
        camera=camera_config["id"],
        width=camera_config["width"],
        height=camera_config["height"],
        fps=camera_config["fps"]
    )
elif camera_config["name"] == "file":
    cam = loader.load_component(ComponentType.CAMERA, camera_config["name"])(
        file=camera_config["file"]
    )

# Enable the camera.
cam.enable()

# Load the configured engine.
engine = loader.load_component(ComponentType.ENGINE, engine_config["name"])(
    path=engine_config["path"]
)
# Enable the inference engine.
engine.enable()

# Load the configured publisher.
publisher = loader.load_component(ComponentType.PUBLISHER, publisher_config["name"])(
    team=publisher_config["team"],
    table=publisher_config["table"],
    prefix=publisher_config["prefix"]
)
# Enable the publisher.
sd = publisher.enable()
prefix: str = publisher_config["prefix"]
if publisher.is_connected():
    sd.putBoolean(f"{prefix}/enabled", True)

# Create a new image window if visual debugging is enabled.
if show:
    namedWindow("debug")

# Average FPS counter
avg_fps = []

try:
    while True:
        connected = publisher.is_connected()
        if connected and not sd.getBoolean(f"{prefix}/enabled", False):
            continue
        t1 = getTickCount()
        frame = cam.read()
        inferred = engine.infer(frame)
        filtered = util.filter_confidence(inferred, engine_config["min_score"])
        normalized = util.normalize(filtered, camera_config["width"], camera_config["height"],
                                    engine_config["width"], engine_config["height"])
        humanized = util.humanize(normalized, t1, getTickCount(), getTickFrequency())
        avg_fps.append(humanized["fps"])
        simple_util.publish(humanized, connected, f"{prefix}/detections", sd.putString, debug,
                            logger.debug, show, frame, (sum(avg_fps) / len(avg_fps)))

    logger.info(strings.stopped_nt)
    if publisher.is_connected():
        sd.putBoolean(f"{prefix}/enabled", False)
except KeyboardInterrupt:
    logger.warning(strings.stopped_keyboard)
except EOFError:
    logger.info("End of file reached.")
finally:
    if publisher.is_connected():
        sd.putBoolean(f"{prefix}/enabled", False)
    if show:
        destroyAllWindows()
    cam.disable()
    engine.disable()
    publisher.disable()
    sys.exit(0)

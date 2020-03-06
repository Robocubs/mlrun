# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""

# Global modules
import cv2
import pyximport
pyximport.install(language_level=3)

import logging
import sys

# Non-guarded imports
from cv2 import getTickFrequency, getTickCount  # type: ignore

# Local imports
from mlrun import strings, config, loader, util, simple_util


def main():
    """
    Main function that starts MLRun.
    """
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
    logger_config: dict = loaded_config["logger"]
    camera_config: dict = loaded_config["camera"]
    engine_config: dict = loaded_config["engine"]
    publisher_config: dict = loaded_config["publisher"]
    show: bool = loaded_config["show"]
    debug: bool = True if logger_config["max_level"] == "DEBUG" else False

    #######################################################################################################
    # All things requiring configuration go below here. The configuration isn't loaded before this point. #
    #######################################################################################################

    logger = loader.load_logger(logger_config["name"])(
        logging.getLogger("mlrun"),
        max_level=logger_config["max_level"]
    )

    # Disable TensorFlow mixed logging. This is important because TensorFlow will start logging random Python-based
    # messages without this line.
    logging.getLogger("tensorflow").setLevel(logging.FATAL)

    ###########################################################################
    # Start logging below, because the logger isn't loaded before this point. #
    ###########################################################################

    logger.info(strings.mlrun_started)
    if show:
        logger.warning(strings.warning_show_debug)

    # Load the configured camera instance for reading.
    if camera_config["name"] == "opencv":
        cam = loader.load_camera(camera_config["name"])(
            camera=camera_config["id"],
            width=camera_config["width"],
            height=camera_config["height"],
            fps=camera_config["fps"]
        )
    elif camera_config["name"] == "file":
        cam = loader.load_camera(camera_config["name"])(
            file=camera_config["file"]
        )

    # Enable the camera.
    cam.enable()

    # Load the configured engine.
    engine = loader.load_engine(engine_config["name"])(
        engine_config["path"]
    )
    # Enable the inference engine.
    engine.enable()

    # Load the configured publisher.
    publisher = loader.load_publisher(publisher_config["name"])(
        team=publisher_config["team"],
        table=publisher_config["table"],
        prefix=publisher_config["prefix"]
    )
    # Enable the publisher.
    sd = publisher.enable()

    # Notify of frame rate tick frequency.
    prefix: str = publisher_config["prefix"]
    if publisher.is_connected():
        sd.putBoolean(f"{prefix}/enabled", True)
    if show:
        cv2.namedWindow("debug")

    try:
        while True:
            connected = publisher.is_connected()
            if connected and sd.getBoolean(f"{prefix}/enabled", False):
                continue
            # Inference!
            t1 = getTickCount()
            try: # This inner try is required to catch errors if the file ends.
                frame = cam.read()
                inferred = engine.infer(frame)
                filtered = util.filter_confidence(inferred, engine_config["min_score"])
                normalized = util.normalize(filtered, camera_config["width"], camera_config["height"],
                                            engine_config["width"], engine_config["height"])
                humanized = util.humanize(normalized, t1, getTickCount(), getTickFrequency())
                simple_util.publish(humanized, connected, f"{prefix}/detections", sd.putString, debug,
                                    logger.debug, show, frame)
            except TypeError:
                raise EOFError()

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
            cv2.destroyAllWindows()
        cam.disable()
        engine.disable()
        publisher.disable()
        sys.exit(0)


if __name__ == "__main__":
    main()

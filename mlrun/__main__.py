# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""

# Global modules

import logging
import sys

# Non-guarded imports
from cv2 import getTickFrequency, getTickCount, namedWindow, destroyAllWindows  # type: ignore
from typedconfig.source import IniFileConfigSource
import click

# Local imports
from mlrun import strings, config, loader, util  # type: ignore
from mlrun.loader import ComponentType


@click.command(name="mlrun")
@click.argument("config_file", type=click.Path(exists=True))
def main(config_file: str):
    """
    Launch MLRun.

    CONFIG_FILE is the path to the INI config file to be used.
    """
    # Load configuration.
    loaded_config = config.ConfigObject()
    loaded_config.add_source(IniFileConfigSource(config_file, encoding="utf-8"))
    loaded_config.read()

    # Make some aliases for readability's sake.
    logger_config = loaded_config.logger
    camera_config = loaded_config.camera
    engine_config = loaded_config.engine
    publisher_config = loaded_config.publisher
    show = loaded_config.show
    debug = True if logger_config["max_level"] == "DEBUG" else False

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

    ##################################################################################################
    # All things requiring logging go below here, because the logger isn't loaded before this point. #
    ##################################################################################################

    # Show the starting banner.
    logger.info(strings.mlrun_started)

    # Warn about debugging reducing performance.
    if show:
        logger.warning(strings.warning_show_debug)

    # Load the configured camera instance.
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

    # Create a new image window if debugging is enabled.
    if show:
        namedWindow("debug")

    # Average FPS counter
    avg_fps = []

    try:
        while True:
            connected = publisher.is_connected()
            if connected and sd.getBoolean(f"{prefix}/enabled", False):
                continue
            t1 = getTickCount()
            frame = cam.read()
            inferred = engine.infer(frame)
            filtered = util.filter_confidence(inferred, engine_config["min_score"])
            normalized = util.normalize(filtered, camera_config["width"], camera_config["height"],
                                        engine_config["width"], engine_config["height"])
            humanized = util.humanize(normalized, t1, getTickCount(), getTickFrequency())
            avg_fps.append(humanized["fps"])
            util.publish(humanized, connected, f"{prefix}/detections", sd.putString, debug,
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


if __name__ == "__main__":
    main()

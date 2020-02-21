# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""

# Global modules
import json
import logging
import sys

# Non-guarded imports
import rx
from cv2 import getTickFrequency, getTickCount
from rx import operators as op

# Local imports
from mlrun import strings, config, loader

# Determine the number of arguments.
if len(sys.argv) == 2:
    # Load the configuration.
    if config.configurations[sys.argv[1]]:
        config = config.configurations[sys.argv[1]]
    else:
        print(strings.warning_config_name)
        config = config.configurations["desktop"]
    # Make some aliases for readability's sake.
    logger_config: dict = config["logger"]
    camera_config: dict = config["camera"]
    engine_config: dict = config["engine"]
    publisher_config: dict = config["publisher"]
else:
    print(strings.warning_config_name)
    config = config.configurations["desktop"]

#######################################################################################################
# All things requiring configuration go below here. The configuration isn't loaded before this point. #
#######################################################################################################

l = loader.load_logger(logger_config["name"])(
    logging.getLogger("mlrun"),
    max_level=logger_config["max_level"]
)

# Disable TensorFlow mixed logging. This is important because TensorFlow will start logging random Python-based
# messages without this line.
logging.getLogger("tensorflow").setLevel(logging.FATAL)

###########################################################################
# Start logging below, because the logger isn't loaded before this point. #
###########################################################################

l.info(strings.mlrun_started)

# Load the configured camera instance for reading.
cam = loader.load_camera(camera_config["name"])(
    id=camera_config["id"],
    width=camera_config["width"],
    height=camera_config["height"],
    fps=camera_config["fps"],
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
fps: float = 0.0
avg_fps = []
freq: float = getTickFrequency()
prefix: str = publisher_config["prefix"]
nt: bool = publisher.is_connected()

try:
    if nt:
        sd.putBoolean(f"{prefix}/enabled", True)
    while True:
        # This is already set above, but we need to refresh it constantly.
        nt: bool = publisher.is_connected()
        # Begin process of inference.
        if nt and sd.getBoolean(f"{prefix}/enabled", True):
            continue
        t1 = getTickCount()
        rx.start(lambda: cam.read()).pipe(
            # Input the image into the neural network.
            op.map(lambda byte_encoded: engine.infer(byte_encoded)),
            # Reshape the data into a usable construct.
            op.map(lambda raw_infer: [i.tolist()[0] for i in raw_infer]),
            # Zip the newly decoded contents.
            op.map(lambda unzipped: list(zip(*unzipped))),
            # Filter the items that don't match our required quality.
            # This filter is so freaking annoying... it's really hard to explain and difficult to optimize!
            op.map(lambda unfiltered: [
                unfiltered[i] for i in range(len(unfiltered))
                if unfiltered[i][0] > engine_config["min_score"]
            ]),
            # Convert the floating coordinates to a pixel size.
            # This is also really complicated and hard to explain.
            op.map(lambda raw_values: [
                (
                    [
                        int(max(1, (a[1][0] * camera_config["height"]))),
                        int(max(1, (a[1][1] * camera_config["width"]))),
                        int(min(camera_config["height"], (a[1][2] * camera_config["height"]))),
                        int(min(camera_config["width"], (a[1][3] * camera_config["width"]))),
                        round(100 * a[0], 1)
                    ] if not (len(a) == 0) else None
                ) for a in raw_values
            ]),
            # Rewrite data into JSON output
            op.map(lambda processed: json.dumps({
                "fps": round(1 / ((getTickCount() - t1) / freq), 1),
                "numDetections": len(processed),
                "detections": processed
            })),
            # Add to average FPS
            op.map(lambda output: (avg_fps.append(json.loads(output)["fps"]), output)[-1]),
            # Write to NetworkTables
            op.map(lambda output: (sd.putString(f"{prefix}/detections", output) if nt else None, print(output))[0])
        ).run()

    l.info(strings.stopped_nt)
    if nt:
        sd.putBoolean(f"{prefix}/enabled", False)
except KeyboardInterrupt:
    l.warning(strings.stopped_keyboard)
    if len(avg_fps) > 1:
        l.info(f"Average FPS: {round(sum(avg_fps)/len(avg_fps), 1)}")
    sd.putBoolean(f"{prefix}/enabled", False)
    cam.disable()
    engine.disable()
    publisher.disable()
    sys.exit(0)

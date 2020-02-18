# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""
# Global modules
import json
import logging
import os
import sys
import pkg_resources

# Non-guarded installed modules
import coloredlogs
import jsonschema
from jsonschema import ValidationError

# Type hinting only
from logging import Logger
from typing import Dict, List

# Local imports
from mlrun import strings, schema

# Create individual loggers for each segment of the program.
l: Dict[str, Logger] = {
    "root": logging.getLogger("mlrun"),
    "tensorflow": logging.getLogger("tf"),
    "opencv": logging.getLogger("opencv"),
    "networktables": logging.getLogger("networktables")
}
# Install colored logging hook onto each of our loggers.
[coloredlogs.install(
    level="DEBUG",
    logger=l[i],
    fmt="%(name)s %(levelname)s %(message)s"
) for i in l.keys()]
# Disable TensorFlow mixed logging.
logging.getLogger("tensorflow").setLevel(logging.FATAL)
# Whether the pipeline should be enabled.
pipelineEnabled = True

# Load configuration file
if len(sys.argv) != 2:
    l["root"].error("Incorrect number of arguments.")
    l["root"].error("MLRun should be invoked as:")
    l["root"].error("\tpython3 -m mlrun {config_path}")
    sys.exit(1)
with open(sys.argv[1]) as fp:
    config = json.load(fp)

###########################################################################
# Start logging below, because the logger isn't loaded before this point. #
###########################################################################
l["root"].debug(strings.mlrun_started)

# Verify configuration file
try:
    l["root"].info(strings.validation_started)
    jsonschema.validate(config, schema=schema.schema)
except ValidationError as e:
    l["root"].error(strings.validation_error)
    l["root"].error(str(e))

l["root"].info(strings.validation_successful)

# If configured to do so, enable debugging.
if (not config["debugging"]["logs"]) and (not config["debugging"]["show"]):
    l["root"].info(strings.debugging_disabled)
elif config["debugging"]["logs"] and (not config["debugging"]["show"]):
    l["root"].info(strings.debugging_logs_only)
elif (not config["debugging"]["logs"]) and config["debugging"]["show"]:
    l["root"].info(strings.debugging_show_only)
elif config["debugging"]["logs"] and config["debugging"]["show"]:
    l["root"].info(strings.debugging_full_enabled)

# If configured to do so, hide TensorFlow deprecation messages.
# Note that this is a private API, and may disappear at any time.
if not config["tensorflow"]["print_deprecation_messages"]:
    l["tensorflow"].warning(strings.tensorflow_deprecation_disabled)
    from tensorflow.python.util import deprecation

    deprecation._PRINT_DEPRECATION_WARNINGS = False
elif pkg_resources.get_distribution("tensorflow").version.split(".")[0] > 1:
    l["tensorflow"].info(strings.tensorflow_deprecation_irrelevant)
else:
    l["tensorflow"].info(strings.tensorflow_deprecation_enabled)

# If configured to do so, hide TensorFlow's normal output messages.
if config["tensorflow"]["minimum_logging_level"] is 0:
    l["tensorflow"].warning(strings.tensorflow_log_level_full)
elif config["tensorflow"]["minimum_logging_level"] is 1:
    l["tensorflow"].warning(strings.tensorflow_log_level_warnings)
elif config["tensorflow"]["minimum_logging_level"] is 2:
    l["tensorflow"].warning(strings.tensorflow_log_level_errors)
elif config["tensorflow"]["minimum_logging_level"] is 3:
    l["tensorflow"].warning(strings.tensorflow_log_level_fatal)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = str(config["tensorflow"]["minimum_logging_level"])

# Open the camera for reading.
# Then check whether the capture was successfully opened.
l["opencv"].info(strings.opencv_loading)
try:
    # Note: PyCharm freaks out about OpenCV, b/c supposedly the references we make don't exist.
    # Spoiler alert: they do.
    # noinspection PyUnresolvedReferences
    import cv2
    # inspection PyUnresolvedReferences
except ImportError:
    l["opencv"].error(strings.opencv_unsuccessful)
    sys.exit(1)

l["opencv"].info(strings.opencv_successful)
cap = cv2.VideoCapture(int(config["camera"]["id"]))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["camera"]["width"])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["camera"]["height"])
cap.set(cv2.CAP_PROP_FPS, config["camera"]["fps"])
if not cap.isOpened():
    l["opencv"].error(strings.opencv_camera_error.format(cam=config["camera"]["id"]))
    sys.exit(1)

# Prepare for publishing via NetworkTables, if enabled in the settings file.
if config["networktables"]["enabled"]:
    l["networktables"].info(strings.networktables_loading)
    try:
        from _pynetworktables import NetworkTable
        from networktables import NetworkTables
    except ImportError:
        l["networktables"].error(strings.networktables_unexpected_disable)
        sys.exit(1)

    l["networktables"].info(strings.networktables_successful)


    def connection_listener(status, connection):
        """
        Connection listener for NetworkTables.
        Args:
            status: Bool, whether status is positive or not
            connection: ConnectionInfo NamedTuple from NetworkTables
        """
        if status:
            l["networktables"].info(strings.networktables_connection_established.format(
                ip=connection.remote_ip,
                port=connection.remote_port,
                ver=connection.protocol_version
            ))
        else:
            l["networktables"].warning(strings.networktables_connection_lost)


    NetworkTables.addConnectionListener(connection_listener, True)
    NetworkTables.initialize(server="roborio-{team}-frc.local".format(team=config["networktables"]["team"]))
    sd: NetworkTable = NetworkTables.getTable(config["networktables"]["table"])
else:
    l["networktables"].warning(strings.networktables_expected_disable)

# Load TensorFlow from disk.
if config["tensorflow"]["compat"]:
    l["tensorflow"].warning(strings.tensorflow_legacy_mode)
    l["tensorflow"].info(strings.tensorflow_legacy_loading)
    try:
        import tensorflow.compat.v1 as tf
    except ImportError:
        l["tensorflow"].error(strings.tensorflow_legacy_error)
        sys.exit(1)

    l["tensorflow"].info(strings.tensorflow_legacy_loaded)
else:
    l["tensorflow"].info(strings.tensorflow_modern_mode)
    l["tensorflow"].info(strings.tensorflow_modern_loading)
    try:
        import tensorflow as tf
    except ImportError:
        l["tensorflow"].error(strings.tensorflow_modern_error)
        sys.exit(1)

    l["tensorflow"].info(strings.tensorflow_modern_loaded)

# Check if a model exists at the specified path.
if os.path.exists(config["tensorflow"]["model_path"] + "/saved_model.pb"):
    l["tensorflow"].info(strings.tensorflow_model_present)
else:
    l["tensorflow"].error(strings.tensorflow_model_missing)
    sys.exit(1)

# Notify of frame rate tick frequency.
fps: float = 0.0
freq: float = cv2.getTickFrequency()
l["opencv"].info(strings.opencv_tick_frequency.format(freq=freq))
average_fps: List[float] = []

try:
    l["tensorflow"].info(strings.tensorflow_loading_model)
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ["serve"], config["tensorflow"]["model_path"])
        l["root"].info(strings.tensorflow_loaded_model)
        # Begin process of inference.
        if config["networktables"]["enabled"]:
            sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", pipelineEnabled)
        while True:
            if config["networktables"]["enabled"]:
                if sd.getBoolean(f"{config['networktables']['keyPrefix']}/enabled", False):
                    continue
            t1 = cv2.getTickCount()
            frame = cap.read()[1]
            inferred = sess.run(["detection_scores:0", "detection_boxes:0"], feed_dict={
                "encoded_image_string_tensor:0": [cv2.imencode(".jpg", frame)[1].tobytes()]
            })
            scores = inferred[0].tolist()[0]
            boxes = inferred[1].tolist()[0]
            detections = []
            for i in range(len(scores)):
                if (scores[i] > 0.8) and (scores[i] <= 1.0):
                    ymin = int(max(1, (boxes[i][0] * frame.shape[0])))
                    xmin = int(max(1, (boxes[i][1] * frame.shape[1])))
                    ymax = int(min(frame.shape[0], (boxes[i][2] * frame.shape[0])))
                    xmax = int(min(frame.shape[1], (boxes[i][3] * frame.shape[1])))
                    t2 = cv2.getTickCount()
                    pre_calc = (t2 - t1) / freq
                    fps = 1 / pre_calc
                    average_fps.append(fps)
                    detections.append([xmin, ymin, xmax, ymax, round(100 * scores[i], 1)])
            if config["debugging"]["logs"]:
                for i in detections:
                    l["root"].debug(strings.debug_log.format(fps=round(fps, 1), xmin=i[1], ymin=i[2], xmax=i[3],
                                                             ymax=i[4]))
            if config["debugging"]["show"]:
                for i in detections:
                    cv2.rectangle(frame, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 2)
                cv2.imshow("MLRun Debugging View", frame)
                cv2.waitKey(1) & 0xFF
            if config["networktables"]["enabled"]:
                sd.putString("jetson/detections", json.dumps({
                    "fps": round(fps, 1),
                    "numDetections": len(detections),
                    "detections": detections
                }))

        if config["networktables"]["enabled"]:
            l["root"].info(strings.stopped_nt)
            sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", False)
except KeyboardInterrupt:
    l["root"].warning(strings.stopped_keyboard)
    if config["networktables"]["enabled"]:
        sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", False)
    cap.release()
    if config["debugging"]["show"]:
        cv2.destroyAllWindows()
    if len(average_fps) > 0:
        l["root"].info(f"Average FPS: {round(sum(average_fps)/len(average_fps), 1)}")
    sys.exit(0)

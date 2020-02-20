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

# Type hinting only
from logging import Logger
from typing import Dict, List

# Local imports
from mlrun import strings, config, loader

# Determine the number of arguments.
if len(sys.argv) == 2:
    # Load the configuration.
    config = config.configurations[sys.argv[1]]
    # Make some aliases for readability's sake.
    logger_name: str = config["logger"]
    deprecation: bool = config["tf"]["deprecation"]
    level: int = config["tf"]["level"]
    compat: bool = config["tf"]["compat"]
    path: str = config["tf"]["path"]
    min_score: float = config["tf"]["min_score"]
    max_score: float = config["tf"]["max_score"]
    camera: Dict[str, int] = config["cam"]
    nt: bool = config["nt"]["enabled"]
    team: int = config["nt"]["team"]
    table: str = config["nt"]["table"]
    prefix: str = config["nt"]["prefix"]
    dlog: bool = config["debug"]["logs"]
    dshow: bool = config["debug"]["show"]
else:
    print(f"ERROR! {strings.error_wrong_arguments}")
    sys.exit(1)

#######################################################################################################
# All things requiring configuration go below here. The configuration isn't loaded before this point. #
#######################################################################################################

# Create individual loggers for each segment of the program.
l: Dict[str, Logger] = {
    "mlrun": loader.load_logger(logger_name)(logging.getLogger("mlrun")),
    "tf": loader.load_logger(logger_name)(logging.getLogger("tf")),
    "cv2": loader.load_logger(logger_name)(logging.getLogger("cv2")),
    "nt": loader.load_logger(logger_name)(logging.getLogger("nt"))
}

###########################################################################
# Start logging below, because the logger isn't loaded before this point. #
###########################################################################

# Disable TensorFlow mixed logging. This is important because TensorFlow will start logging random Python-based
# messages without this line.
logging.getLogger("tensorflow").setLevel(logging.FATAL)
# The pipeline should immediately be enabled if this is set. Will be moved to a config variable eventually.
pipelineEnabled: bool = True

l["mlrun"].info(strings.mlrun_started)

# If configured to do so, enable debugging.
# Debugging can consist of either logging results per frame, visualization of results, or all of the above.
# If visualization is enabled, performance will be significantly lowered.
if (not dlog) and (not dshow):
    l["mlrun"].info(strings.debugging_disabled)
elif dlog and (not dshow):
    l["mlrun"].warning(strings.debugging_logs_only)
elif (not dlog) and dshow:
    l["mlrun"].warning(strings.debugging_show_only)
elif dlog and dshow:
    l["mlrun"].warning(strings.debugging_full_enabled)

# If configured to do so, hide TensorFlow deprecation messages.
# Note that this is a private undocumented API, and may disappear at any time.
try:
    from tensorflow import __version__ as tf_version
    if int(tf_version.split(".")[0]) > 1:
        l["tf"].info(strings.tensorflow_deprecation_irrelevant)
    else:
        if not deprecation:
            l["tf"].warning(strings.tensorflow_deprecation_disabled)
            try:
                # noinspection PyUnresolvedReferences
                from tensorflow.python.util import deprecation

                deprecation._PRINT_DEPRECATION_WARNINGS = False
            except ImportError:
                l["tf"].error(strings.tensorflow_legacy_error)
                sys.exit(1)
        else:
            l["tf"].info(strings.tensorflow_deprecation_enabled)
except ImportError:
    l["mlrun"].error(strings.tensorflow_legacy_error)
    sys.exit(1)

# If configured to do so, hide TensorFlow's normal output messages.
if level is 0:
    l["tf"].warning(strings.tensorflow_log_level_full)
elif level is 1:
    l["tf"].warning(strings.tensorflow_log_level_warnings)
elif level is 2:
    l["tf"].warning(strings.tensorflow_log_level_errors)
elif level is 3:
    l["tf"].warning(strings.tensorflow_log_level_fatal)
os.system(f"export TF_CPP_MIN_LOG_LEVEL={level}")

# Open the camera for reading.
# Then check whether the capture was successfully opened.
l["cv2"].info(strings.opencv_loading)
try:
    # Note: PyCharm freaks out about OpenCV, b/c supposedly the references we make don't exist.
    # Spoiler alert: they do.
    # noinspection PyUnresolvedReferences
    import cv2
except ImportError:
    # Fail if unsuccessful.
    l["cv2"].error(strings.opencv_unsuccessful)
    sys.exit(1)

l["cv2"].info(strings.opencv_successful)
if os.path.exists(f"/dev/video{camera['id']}"):
    cap = cv2.VideoCapture(camera["id"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera["height"])
    cap.set(cv2.CAP_PROP_FPS, camera["fps"])
    if not cap.isOpened():
        l["cv2"].error(strings.opencv_camera_error.format(cam=camera["id"]))
        sys.exit(1)
else:
    l["mlrun"].error(strings.error_nonexistant_camera.format(id=camera["id"]))
    sys.exit(1)

# Prepare for publishing via NetworkTables, if enabled in the settings file.
if nt:
    l["nt"].info(strings.networktables_loading)
    try:
        from _pynetworktables import NetworkTable
        from networktables import NetworkTables
        from _pynetworktables._impl.structs import ConnectionInfo
    except ImportError:
        l["nt"].error(strings.networktables_unexpected_disable)
        sys.exit(1)

    l["nt"].info(strings.networktables_successful)


    def connection_listener(status: bool, connection: ConnectionInfo):
        """
        Connection listener for NetworkTables.
        Args:
            status: Bool, whether status is positive or not
            connection: ConnectionInfo NamedTuple from NetworkTables
        """
        if status:
            l["nt"].info(strings.networktables_connection_established.format(
                ip=connection.remote_ip,
                port=connection.remote_port,
                ver=connection.protocol_version
            ))
        else:
            l["nt"].warning(strings.networktables_connection_lost)


    NetworkTables.addConnectionListener(connection_listener, True)
    NetworkTables.initialize(server=f"roborio-{team}-frc.local")
    sd: NetworkTable = NetworkTables.getTable(table)
else:
    l["nt"].warning(strings.networktables_expected_disable)

# Load TensorFlow from disk.
if compat:
    l["tf"].warning(strings.tensorflow_legacy_mode)
    l["tf"].info(strings.tensorflow_legacy_loading)
    try:
        import tensorflow.compat.v1 as tf

        tf.disable_v2_behavior()
    except ImportError:
        l["tf"].error(strings.tensorflow_legacy_error)
        sys.exit(1)

    l["tf"].info(strings.tensorflow_legacy_loaded)
else:
    l["tf"].info(strings.tensorflow_modern_mode)
    l["tf"].info(strings.tensorflow_modern_loading)
    try:
        import tensorflow as tf
    except ImportError:
        l["tf"].error(strings.tensorflow_modern_error)
        sys.exit(1)

    l["tf"].info(strings.tensorflow_modern_loaded)

# Check if a model exists at the specified path.
if os.path.exists(path + "/saved_model.pb"):
    l["tf"].info(strings.tensorflow_model_present)
else:
    l["tf"].error(strings.tensorflow_model_missing)
    sys.exit(1)

# Notify of frame rate tick frequency.
fps: float = 0.0
freq: float = cv2.getTickFrequency()
l["cv2"].info(strings.opencv_tick_frequency.format(freq=freq))
average_fps: List[float] = []

try:
    l["tf"].info(strings.tensorflow_loading_model)
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ["serve"], path)
        l["mlrun"].info(strings.tensorflow_loaded_model)
        # Begin process of inference.
        if nt:
            sd.putBoolean(f"{prefix}/enabled", pipelineEnabled)
        while True:
            if nt:
                if sd.getBoolean(f"{prefix}/enabled", pipelineEnabled):
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
                if (scores[i] > min_score) and (scores[i] <= max_score):
                    ymin = int(max(1, (boxes[i][0] * frame.shape[0])))
                    xmin = int(max(1, (boxes[i][1] * frame.shape[1])))
                    ymax = int(min(frame.shape[0], (boxes[i][2] * frame.shape[0])))
                    xmax = int(min(frame.shape[1], (boxes[i][3] * frame.shape[1])))
                    t2 = cv2.getTickCount()
                    pre_calc = (t2 - t1) / freq
                    fps = 1 / pre_calc
                    average_fps.append(fps)
                    detections.append([xmin, ymin, xmax, ymax, round(100 * scores[i], 1)])
            if dlog:
                l["mlrun"].debug(json.dumps({
                    "fps": round(fps, 1),
                    "numDetections": len(detections),
                    "detections": detections
                }))
            if dshow:
                for i in detections:
                    cv2.rectangle(frame, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 2)
                cv2.imshow("MLRun Debugging View", frame)
                cv2.waitKey(1) & 0xFF
            if nt:
                sd.putString(f"{prefix}/detections", json.dumps({
                    "fps": round(fps, 1),
                    "numDetections": len(detections),
                    "detections": detections
                }))

        if nt:
            l["mlrun"].info(strings.stopped_nt)
            sd.putBoolean(f"{prefix}/enabled", False)
except KeyboardInterrupt:
    l["mlrun"].warning(strings.stopped_keyboard)
    if nt:
        sd.putBoolean(f"{prefix}/enabled", False)
    cap.release()
    if dshow:
        cv2.destroyAllWindows()
    if len(average_fps) > 0:
        l["mlrun"].info(strings.average_fps_message.format(fps=round(sum(average_fps) / len(average_fps), 1)))
    sys.exit(0)

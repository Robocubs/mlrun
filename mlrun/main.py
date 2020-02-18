# -*- coding: utf-8 -*-
"""Run an AutoML model with GPU acceleration using TensorFlow.

This module loads a model from a file, imports it into memory,
and executes it with a camera input.
"""
import json
import logging
from logging import Logger
import os
import sys
from typing import Dict

import coloredlogs

# Load configuration file
with open("config.json") as fp:
    config = json.load(fp)

# Create individual loggers for each segment of the program.
l: Dict[str, Logger] = {
    "root": logging.getLogger("mlrun"),
    "tensorflow": logging.getLogger("tf"),
    "opencv": logging.getLogger("opencv"),
    "networktables": logging.getLogger("networktables")
}
# Install colored logging hook onto each of our loggers.
[coloredlogs.install(
    level=config["logging"]["log_level"],
    logger=l[i],
    fmt=config["logging"]["format"]
) for i in l.keys()]
# Disable TensorFlow mixed logging.
logging.getLogger("tensorflow").setLevel(logging.FATAL)
# Whether the pipeline should be enabled.
pipelineEnabled = True

###########################################################################
# Start logging below, because the logger isn't loaded before this point. #
###########################################################################
l["root"].debug("Starting a new instance of MLRun.")
if config["debugging"]:
    l["root"].warning("Debugging is enabled! Performance will be dramatically reduced due to displaying of output.")

# If configured to do so, hide TensorFlow deprecation messages.
# Note that this is a private API, and may disappear at any time.
if not config["tensorflow"]["print_deprecation_messages"]:
    l["tensorflow"].warning("TensorFlow deprecation warnings have been disabled. If you intend on upgrading "
                            "TensorFlow later, please enable these in your configuration file. Otherwise, "
                            "you can ignore this message.")
    from tensorflow.python.util import deprecation

    deprecation._PRINT_DEPRECATION_WARNINGS = False
else:
    l["tensorflow"].warning("TensorFlow deprecation warnings have been enabled. These can safely be ignored, "
                            "or turned off in your configuration file if they don't affect your use case.")

# If configured to do so, hide TensorFlow's normal output messages.
if config["tensorflow"]["minimum_logging_level"] is 0:
    l["tensorflow"].warning("TensorFlow minimum logging level set to allow information, warnings, non-fatal "
                            "errors, and fatal errors.")
elif config["tensorflow"]["minimum_logging_level"] is 1:
    l["tensorflow"].warning("TensorFlow minimum logging level set to allow warnings, non-fatal errors and fatal "
                            "errors.")
elif config["tensorflow"]["minimum_logging_level"] is 2:
    l["tensorflow"].warning("TensorFlow minimum logging level set to allow non-fatal errors and fatal errors.")
elif config["tensorflow"]["minimum_logging_level"] is 3:
    l["tensorflow"].warning("Tensorflow minimum logging level set to allow only fatal errors.")
os.system(f"export TF_CPP_MIN_LOG_LEVEL=\"{config['tensorflow']['minimum_logging_level']}\"")

# Open the camera for reading.
# Then check whether the capture was successfully opened.
l["opencv"].info("Loading OpenCV...")
import cv2

l["opencv"].info("Successfully loaded OpenCV.")
cap = cv2.VideoCapture(int(config["camera"]["id"]))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["camera"]["width"])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["camera"]["height"])
cap.set(cv2.CAP_PROP_FPS, config["camera"]["fps"])
if not cap.isOpened():
    l["opencv"].error("OpenCV was unable to open the camera /dev/video{cam}. Please check your "
                      "configuration.".format(cam=config["camera"]["id"]))
    sys.exit(1)

# Prepare for publishing via NetworkTables, if enabled in the settings file.
if config["networktables"]["enabled"]:
    from _pynetworktables import NetworkTable
    from networktables import NetworkTables

    l["networktables"].info("NetworkTables support is enabled.")


    def connection_listener(status, connection):
        """
        Connection listener for NetworkTables.
        Args:
            status: Bool, whether status is positive or not
            connection: ConnectionInfo NamedTuple from NetworkTables
        """
        if status:
            l["networktables"].info(
                f"Established connection with {connection.remote_ip}:{connection.remote_port} "
                f"over protocol version {connection.protocol_version}.")
        else:
            l["networktables"].warning(
                f"Lost connection with NetworkTables server."
            )

    NetworkTables.addConnectionListener(connection_listener, True)
    NetworkTables.initialize(server="roborio-{team}-frc.local".format(team=config["networktables"]["team"]))
    sd: NetworkTable = NetworkTables.getTable(config["networktables"]["table"])
else:
    l["networktables"].warning("NetworkTables support disabled. Results will not be broadcasted over the network.")

# Load TensorFlow from disk.
if config["tensorflow"]["compat"]:
    l["tensorflow"].warning("TensorFlow is running in V1 (compatibility) mode. This is a kludge for replacing legacy "
                            "TensorFlow code with modern TensorFlow 2.0 code. Please fix your code later on.")
    l["tensorflow"].info("Loading TensorFlow in compatibility mode...")
    import tensorflow.compat.v1 as tf

    l["tensorflow"].info("Successfully loaded TensorFlow in compatibility mode.")
else:
    l["tensorflow"].info("TensorFlow is running in V2 (modern) mode.")
    l["tensorflow"].info("Loading TensorFlow...")
    import tensorflow as tf

    l["tensorflow"].info("Successfully loaded TensorFlow.")

# Check if a model exists at the specified path.
if not os.path.exists(config["tensorflow"]["model_path"] + "/saved_model.pb"):
    l["tensorflow"].error("A model was not found in the specified model path. Please check your configuration and try "
                          "again.")
    sys.exit(1)

# Notify of frame rate tick frequency.
fps: float = 1.0
freq: float = cv2.getTickFrequency()
l["opencv"].info(f"System's stated tick frequency is {freq}.")

try:
    l["tensorflow"].info("Please wait for TensorFlow to load the model into memory. This may take a while...")
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.loader.load(sess, ["serve"], config["tensorflow"]["model_path"])
        l["root"].info("Startup has finished; inference will begin momentarily.")
        # Begin process of inference.
        if config["networktables"]["enabled"]:
            sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", pipelineEnabled)
        while True:
            if config["networktables"]["enabled"]:
                if sd.getBoolean(f"{config['networktables']['keyPrefix']}/enabled"):
                    continue
            t1 = cv2.getTickCount()
            frame = cap.read()[1]
            inferred = sess.run(["detection_scores:0", "detection_boxes:0"], feed_dict={
                "encoded_image_string_tensor:0": [cv2.imencode(".jpg", frame)[1].tobytes()]
            })
            scores = inferred[0].tolist()[0]
            boxes = inferred[1].tolist()[0]
            for i in range(len(scores)):
                if (scores[i] > 0.8) and (scores[i] <= 1.0):
                    ymin = int(max(1, (boxes[i][0] * frame.shape[0])))
                    xmin = int(max(1, (boxes[i][1] * frame.shape[1])))
                    ymax = int(min(frame.shape[0], (boxes[i][2] * frame.shape[0])))
                    xmax = int(min(frame.shape[1], (boxes[i][3] * frame.shape[1])))
                    t2 = cv2.getTickCount()
                    pre_calc = (t2 - t1) / freq
                    fps = 1 / pre_calc
                    if config["networktables"]["enabled"]:
                        [
                            sd.putNumber(f"{config['networktables']['keyPrefix']}{i}/{key}", value)
                            for key, value in {
                                "xmin": xmin,
                                "xmax": xmax,
                                "ymin": ymin,
                                "ymax": ymax,
                                "scores": round(100 * scores[i], 1),
                                "fps": round(fps, 1)
                            }
                        ]
                    if config["debugging"]["logs"]:
                        l["root"].debug(f"FPS: {round(fps, 1)}; top left: ({xmin}, {ymin}); bottom right: "
                                        f"({xmin}, {ymin})")
                    if config["debugging"]["show"]:
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
                        cv2.imshow("DEBUG frame", frame)
                        cv2.waitKey(1) & 0xFF

        l["root"].info("Pipeline stopped without errors.")
        if config["networktables"]["enabled"]:
            sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", False)
except KeyboardInterrupt:
    l["root"].warning("Pipeline stopped manually.")
    if config["networktables"]["enabled"]:
        sd.putBoolean(f"{config['networktables']['keyPrefix']}/enabled", False)
    cap.release()
    if config["debugging"]["show"]:
        cv2.destroyAllWindows()

"""
Simple utilities to reduce verbosity in the starting point.
"""
from typing import Callable
import json
import cv2  # type: ignore
import numpy as np  # type: ignore


def filter_confidence(unfiltered: list, min_score: float) -> list:
    """
    Filter inference results by confidence.
    Args:
        unfiltered: The unfiltered results.
        min_score: The minimum score that is required for an item to pass.

    Returns:
        A list of inference results which have the required confidence.

    Notes:
        Roughly equivalent to the original lambda used, which was:
            lambda unfiltered: [
                unfiltered[i] for i in range(len(unfiltered))
                if unfiltered[i][0] > engine_config["min_score"]
            ]
    """
    output = []
    length: int = len(unfiltered)
    if length >= 1:
        for i in range(length):
            score = unfiltered[i][0]
            if score > min_score:
                output.append(unfiltered[i])
    return output


def normalize(filtered: list, camera_width: int, camera_height: int, inference_width: int,
              inference_height: int) -> list:
    """
    Normalize the floating point coordinates into pixel values, and convert the inference results into
    a human-understandable format.
    Args:
        filtered: Filtered results from earlier in the pipeline.
        camera_width: The width of the input image for normalization.
        camera_height: The height of the input image for normalization.
        inference_width: The width of the output image from the inference process.
        inference_height: The height of the output image from the inference process.

    Returns:
        The normalized values.
    """
    output = []
    for i in filtered:
        # This stuff is complicated. Long story short, the inference process returns values relative to
        # its expected input size, which need to be changed to the values relative to the size of the camera's
        # input.
        one = int(((max(1, i[1][0] * inference_height)) / inference_height) * camera_height)
        two = int(((max(1, i[1][1] * inference_width)) / inference_width) * camera_width)
        three = int((min(inference_height, (i[1][2] * inference_height)) / inference_height) * camera_height)
        four = int((min(inference_width, (i[1][3] * inference_width)) / inference_width) * camera_width)
        confidence = round(100 * i[0], 1)
        output.append([
            four, three, two, one, confidence
        ])
    return output


def humanize(normalized: list, t1: int, t2: int, freq: float) -> dict:
    """
    Convert processed values to readable output.
    Args:
        normalized: Normalized values.
        t1: Tick count at start.
        t2: Tick count at end.
        freq: Tick frequency.

    Returns:
        Readable dictionary.
    """
    length = len(normalized)
    fps = round(1 / ((t2 - t1) / freq), 1)
    return {
        "fps": fps,
        "numDetections": length,
        "detections": normalized
    }


def publish(message: dict, publish_enabled: bool, key: str, publisher: Callable[[str, str], None], debug_enabled: bool,
            logger: Callable[[str], None], show_enabled: bool, image: np.ndarray, avg_fps: float):
    """
    Publish results to NetworkTables, run debug logging and show the results in one fell swoop.
    
    Args:
        message: Dictionary message.
        publish_enabled: Enable publishing.
        key: String key to publish message to.
        publisher: Publisher instance.
        debug_enabled: Enable debug logging.
        logger: Logger instance.
        show_enabled: Whether to show the information.
        image: Image to write rectangles to.
        avg_fps: Average FPS to be written in corner of frame.
    """
    for i in message["detections"]:
        i[4] = round(i[4], 1)
    jsonified: str = json.dumps(message)
    if publish_enabled:
        publisher(key, jsonified)
    if debug_enabled:
        logger(jsonified)
    if show_enabled:
        if len(message["detections"]) > 0:
            for i in message["detections"]:
                cv2.rectangle(image, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 2)
                label = f"{i[4]}%"
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                label_ymin = max(i[3], label_size[1] + 10)
                cv2.putText(image, label, (i[2], label_ymin - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(image, f"FPS: {round(avg_fps, 1)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("debug", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise EOFError()
    return jsonified

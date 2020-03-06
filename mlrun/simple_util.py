"""
Simple utilities that can't be optimized using Cython.
"""
from typing import Callable, Union
import json
import cv2
import numpy as np


def publish(message: dict, publish_enabled: bool, key: str, publisher: Callable[[str, str], None], debug_enabled: bool,
            logger: Callable[[str], None], show_enabled: bool, image: np.ndarray):
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
    """
    jsonified: str = json.dumps(message)
    if publish_enabled:
        publisher(key, jsonified)
    if debug_enabled:
        logger(jsonified)
    if show_enabled:
        if len(message["detections"]) > 0:
            for i in message["detections"]:
                cv2.rectangle(image, (i[0], i[1]), (i[2], i[3]), (255, 0, 0), 2)
        cv2.imshow("debug", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise EOFError()
    return jsonified

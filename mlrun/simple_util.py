"""
Simple utilities that can't be optimized using Cython.
"""
from typing import Callable
import json
import cv2
import numpy as np


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
                cv2.putText(image, label, (i[2], label_ymin - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2,
                            cv2.LINE_AA)
        cv2.putText(image, f"FPS: {round(avg_fps, 1)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)
        cv2.imshow("debug", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise EOFError()
    return jsonified

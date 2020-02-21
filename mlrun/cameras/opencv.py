"""OpenCV based capture device for MLRun.

Loads a frame from a webcam instance created by OpenCV."""
import logging
import os
import sys
from abc import ABC

import numpy as np

from mlrun.loader import load_logger
from mlrun.config import configurations
from mlrun import strings
from mlrun.cameras.base import BaseCamera

cv2 = None


class OpenCVCamera(BaseCamera, ABC):
    """
    OpenCV-based camera system.

    Nothing special here!
    """

    def __init__(self, camera: int = 0, width: int = 320, height: int = 240, fps: int = 30, *args, **kwargs):
        """
        Initialize the capture.
        Args:
            camera: The camera ID to capture. Defaults to zero.
            width: The expected width of the returned frame. Defaults to 320.
            height: The expected height of the returned frame. Defaults to 240.
            fps: The expected amount of frames to be returned each second. Defaults to 30.
        """
        global cv2
        # noinspection PyTypeChecker
        self.logger_name: str = configurations["desktop"]["logger"]["name"]
        self.logger = load_logger(self.logger_name)(logging.getLogger("cv2"))
        if os.path.exists(f"/dev/video{camera}"):
            self.logger.info(strings.opencv_loading)
            try:
                import cv2
            except ImportError:
                self.logger.error(strings.opencv_unsuccessful)
                sys.exit(1)
            self.camera = camera
            self.width = width
            self.height = height
            self.fps = fps
            self.capture = None
        else:
            self.logger.error(strings.error_nonexistant_camera.format(id=camera))

    def enable(self):
        """
        Start capturing video.
        Returns:
            Nothing.
        """
        global cv2
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.capture.isOpened():
            self.logger.error(strings.error_camera_fault.format(id=self.camera))

    def disable(self):
        """
        Stop capturing video.
        Returns:
            Nothing.
        """
        self.capture.release()

    def read(self) -> bytes:
        """Return read frame."""
        ret, frame = self.capture.read()
        if ret:
            encoded = cv2.imencode(".jpg", frame)[1]
            return encoded.tobytes()
        else:
            return np.zeros((self.height, self.width, 3), dtype=np.int8).tobytes()

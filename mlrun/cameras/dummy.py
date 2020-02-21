"""Dummy video input for testing purposes."""
from abc import ABC
import logging
import os
import sys

import numpy as np

from mlrun import strings
from mlrun.config import configurations
from mlrun.loader import load_logger
from mlrun.cameras.base import BaseCamera

cv2 = None


class DummyCamera(BaseCamera, ABC):
    """Initialize the dummy camera."""
    def __init__(self, file: str = "", *args, **kwargs):
        """
        Initialize the capture.
        Args:
            camera: The camera ID to capture. Defaults to zero.
            width: The expected width of the returned frame. Defaults to 320.
            height: The expected height of the returned frame. Defaults to 240.
            fps: The expected amount of frames to be returned each second. Defaults to 30.
        """
        global cv2
        super().__init__(*args, **kwargs)
        # noinspection PyTypeChecker
        self.logger_name: str = configurations["desktop"]["logger"]["name"]
        self.logger = load_logger(self.logger_name)(logging.getLogger("cv2"))
        self.file = file
        if os.path.exists(self.file):
            self.logger.info(strings.opencv_loading)
            try:
                import cv2
            except ImportError:
                self.logger.error(strings.opencv_unsuccessful)
                sys.exit(1)
            self.width = None
            self.height = None
            self.fps = None
            self.capture = None

    def enable(self):
        """
        Start capturing video.
        Returns:
            Nothing.
        """
        global cv2
        self.capture = cv2.VideoCapture(self.file)
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        if not self.capture.isOpened():
            self.logger.error("Unable to open file.")

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
            if len(frame.shape) == 3:
                frame = frame[1:]
                return cv2.imencode(".jpg", cv2.resize(frame, (320, 240)))[1].tobytes()
        else:
            return np.zeros((self.height, self.width, 3), dtype=int).tobytes()

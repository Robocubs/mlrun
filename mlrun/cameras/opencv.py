"""OpenCV based capture device for MLRun.

Loads a frame from a webcam instance created by OpenCV."""
import logging
import os
import sys
from abc import ABC
from typing import Union

import numpy as np

from mlrun import strings, loader
from mlrun.loader import ComponentType
from mlrun.config import configurations
from mlrun.cameras.base import BaseCamera

cv2 = None


class OpenCVCamera(BaseCamera, ABC):
    """
    OpenCV-based camera system.

    Nothing special here!
    """

    def __init__(self, camera: int = 0, width: int = 320, height: int = 240, fps: int = 30):
        """
        Initialize the capture.
        Args:
            camera: The camera ID to capture. Defaults to zero.
            width: The expected width of the returned frame. Defaults to 320.
            height: The expected height of the returned frame. Defaults to 240.
            fps: The expected amount of frames to be returned each second. Defaults to 30.
        """
        global cv2
        super().__init__(self)
        # noinspection PyTypeChecker
        self.logger_name: str = configurations["desktop"]["logger"]["name"]
        self.logger = loader.load_component(
            ComponentType.LOGGER,
            self.logger_name
        )(
            logger=logging.getLogger("cv2"),
            max_level="DEBUG"
        )
        if os.path.exists(f"/dev/video{camera}"):
            self.logger.info(strings.opencv_loading)
            try:
                import cv2
                self.logger.info(strings.opencv_successful)
            except ImportError:
                self.logger.error(strings.opencv_unsuccessful)
                sys.exit(1)
            self.camera = camera
            self.width = width
            self.height = height
            self.fps = fps
            self.capture = None
        else:
            self.logger.error(strings.opencv_camera_error.format(cam=camera))

    def enable(self):
        """
        Start capturing video.
        Returns:
            Nothing.
        """
        global cv2
        self.capture = cv2.VideoCapture(self.camera)
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

    def read(self) -> np.ndarray:
        """Return read frame in compatible way."""
        ret, frame = self.capture.read()
        if ret:
            return frame
        else:
            raise EOFError()

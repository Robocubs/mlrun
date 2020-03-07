"""OpenCV based capture device for MLRun.

Loads a frame from a webcam instance created by OpenCV."""
import logging
import os
import sys
from abc import ABC

from mlrun import strings, loader
from mlrun.loader import ComponentType
from mlrun.config import configurations
from mlrun.cameras.base import BaseCamera

cv2 = None


class FileCamera(BaseCamera, ABC):
    """
    File-based camera system.

    Nothing special here!
    """

    def __init__(self, file: str = "/home/nvidia/demo.mp4"):
        """
        Initialize the capture.
        Args:
            file: The file to capture. Defaults to a random path.
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
        if os.path.exists(file):
            self.logger.info(strings.opencv_loading)
            try:
                import cv2
                self.logger.info(strings.opencv_successful)
            except ImportError:
                self.logger.error(strings.opencv_unsuccessful)
                sys.exit(1)
            self.file = file
            self.capture = None
        else:
            self.logger.error(strings.opencv_camera_error.format(cam=file))

    def enable(self):
        """
        Start capturing video.
        Returns:
            Nothing.
        """
        global cv2
        self.capture = cv2.VideoCapture(self.file)
        if not self.capture.isOpened():
            self.logger.error(strings.error_camera_fault.format(id=self.file))

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
            return frame
        else:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
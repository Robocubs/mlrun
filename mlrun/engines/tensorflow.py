"""TensorFlow inferrer for MLRun.

The default inferrer for MLRun. Also the most complicated.
"""
import os
import sys
from abc import ABC
import logging
from typing import List

import cv2  # type: ignore
import numpy as np  # type: ignore

from mlrun import strings, loader
from mlrun.config import configurations
from mlrun.loader import ComponentType
from mlrun.engines.base import BaseEngine

tf = None  # type: ignore


class TensorFlowEngine(BaseEngine, ABC):
    """
    A TensorFlow inferrer for MLRun.
    """
    def __init__(self, path: str = ""):
        """
        Initialize the inference engine.
        Args:
            path: The fully qualified path to the saved model for inference.
        """
        global tf
        super().__init__(self)
        # noinspection PyTypeChecker
        self.logger_name: str = configurations["desktop"]["logger"]["name"]
        self.logger = loader.load_component(
            ComponentType.LOGGER,
            self.logger_name
        )(
            logger=logging.getLogger("tf"),
            max_level="DEBUG"
        )
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        if os.path.exists(path + "/saved_model.pb"):
            self.logger.info(strings.tensorflow_model_present)
            self.model_path = path
        else:
            self.logger.error(strings.tensorflow_model_missing)
            sys.exit(1)
        # Disable TensorFlow deprecation warnings.
        try:
            # noinspection PyUnresolvedReferences
            from tensorflow.python.util import deprecation  # type: ignore
            deprecation._PRINT_DEPRECATION_WARNINGS = False
        except ImportError:
            pass
        # Attempt to load TensorFlow.
        try:
            # TensorFlow 2.x is a bear to deal with.
            # noinspection PyUnresolvedReferences
            import tensorflow.compat.v1 as tf  # type: ignore
        except ImportError:
            self.logger.error(strings.tensorflow_error)
            sys.exit(1)
        self.graph = tf.Graph()  # type: ignore
        self.session = tf.Session(graph=self.graph)  # type:ignore

    def enable(self):
        """
        Enable the session.
        Returns:
            Nothing.
        """
        global tf
        self.session.__enter__()
        self.logger.info(strings.tensorflow_loading_model)
        tf.saved_model.loader.load(self.session, ["serve"], self.model_path)
        self.logger.info(strings.tensorflow_loaded_model)

    def disable(self):
        """
        Disable the session.
        Returns:
            Nothing.
        """
        self.session.close()

    def infer(self, image: np.ndarray) -> List:
        """
        Infer on a byte-encoded image.
        Args:
            image: A byte-encoded image to infer upon.

        Returns:
            A list containing the raw TensorFlow output.
        """
        return list(zip(*[i.tolist()[0] for i in self.session.run(
            ["detection_scores:0", "detection_boxes:0"],
            feed_dict={
                "encoded_image_string_tensor:0": [cv2.imencode(".jpg", image)[1].tobytes()]
            }
        )]))

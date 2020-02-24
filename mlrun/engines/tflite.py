"""TensorFlow Lite inferrer for MLRun.

The secondary inferrer for MLRun.
"""
import logging
import sys
from abc import ABC
import os
from typing import Callable, Union

import cv2
import numpy as np

from mlrun import strings
from mlrun.config import configurations
from mlrun.engines.base import BaseEngine
from mlrun.loader import load_logger

Interpreter: Union[None, Callable] = None
load_delegate: Union[None, Callable] = None


class TFLiteEngine(BaseEngine, ABC):
    """
    A TensorFlow Lite inferrer for MLRun.
    """

    def __init__(self, saved_model_path: str):
        global Interpreter
        global load_delegate
        super().__init__(self)
        self.logger_name: str = configurations["desktop"]["logger"]["name"]
        self.logger = load_logger(self.logger_name)(logging.getLogger("tflite"))
        self.tpu = False
        self.interpreter = None
        self.model = saved_model_path
        self.full_path = ""
        self.input_details = None
        self.output_details = None
        self.image_size = None
        if os.path.exists(self.model + "/model_edgetpu.tflite"):
            self.logger.info(strings.tflite_coral_model_present)
            self.tpu = True
            self.full_path = self.model + "/model_edgetpu.tflite"
        elif os.path.exists(self.model + "/model.tflite"):
            self.logger.info(strings.tflite_model_present)
            self.full_path = self.model + "/model.tflite"
        else:
            self.logger.error(strings.tflite_model_missing)
            sys.exit(1)
        # Attempt to load TFLite and the appropriate delegate.
        try:
            if self.tpu:
                from tflite_runtime.interpreter import Interpreter, load_delegate
            else:
                from tflite_runtime.interpreter import Interpreter
        except ImportError:
            self.logger.error(strings.tflite_not_found)
            sys.exit(1)

    def enable(self):
        """
        Enable the interpreter.
        """
        # Now make a delegate if it worked.
        if self.tpu:
            self.interpreter = Interpreter(model_path=self.full_path,
                                           experimental_delegates=[load_delegate("libedgetpu.so.1.0")])
        else:
            self.interpreter = Interpreter(model_path=self.full_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.image_size = self.input_details[0]["shape"].tolist()[1:3]

    def disable(self):
        """
        Does nothing for TFLite.
        """
        pass

    def infer(self, image: np.ndarray) -> list:
        """
        Run inference.
        """
        image = np.expand_dims(cv2.cvtColor(cv2.resize(image, (self.image_size[0], self.image_size[1])),
                                            cv2.COLOR_BGR2RGB), axis=0)
        self.interpreter.set_tensor(self.input_details[0]["index"], image)
        self.interpreter.invoke()
        return list(zip(*[
            self.interpreter.get_tensor(self.output_details[2]["index"])[0],
            self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        ]))

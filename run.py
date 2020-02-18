import tensorflow as tf
import numpy as np
import cv2
from tensorflow.python.compiler.tensorrt import trt_convert as trt

conversion_params = trt.DEFAULT_TRT_CONVERSION_PARAMS
conversion_params = conversion_params._replace(max_workspace_size_bytes=(1<<32))
conversion_params = conversion_params._replace(precision_mode="FP16")
conversion_params = conversion_params._replace(maximum_cached_engines=100)

converter = trt.TrtGraphConverterV2(
    input_saved_model_dir="/home/nvidia/Documents/Programming/Python/MLRun/model",
    conversion_params=conversion_params
)
converter.convert()
def input_fn():
    for _ in range(128):
        inp = np.random.normal(size=(512, 512, 3)).astype(np.float32)
        result, output = cv2.imencode(".jpg", inp)
        yield output.tobytes()

converter.build(input=input_fn)

converter.save("/home/nvidia/Documents/Programming/Python/MLRun/output")

# -*- coding: utf-8 -*-
"""Strings for AutoML.
These strings are used by MLRun to ensure that all of the text shown is correct.
"""
mlrun_started: str = "Welcome to MLRun! Starting up..."
opencv_loading: str = "Loading OpenCV..."
opencv_successful: str = "Successfully loaded OpenCV."
opencv_unsuccessful: str = "Unable to load OpenCV. Make sure that you have installed OpenCV on your path."
opencv_camera_error: str = "OpenCV was unable to open the camera /dev/video{cam}. Please check your configuration."
networktables_loading: str = "Loading NetworkTables..."
networktables_successful: str = "Successfully loaded NetworkTables."
networktables_unsuccessful: str = "NetworkTables support is enabled, but PyNetworkTables could not be found in " \
                                  "your Python path. Please make sure that PyNetworkTables is installed."
networktables_connection_established: str = "Established connection with {ip}:{port} over protocol version {ver}."
networktables_connection_lost: str = "Lost connection with NetworkTables server."
networktables_unloading: str = "Unloading NetworkTables..."
networktables_unloaded: str = "Unloaded NetworkTables."
tensorflow_error: str = "TensorFlow could not be found. Please make sure that TensorFlow is installed."
tensorflow_model_present: str = "A model was located at the location specified in your configuration file; continuing."
tensorflow_model_missing: str = "A model was not found in the specified location. Please ensure that your model has " \
                                "a name of 'saved_model.pb' in the specified location."
tensorflow_loading_model: str = "Please wait for TensorFlow to load the model into memory. This may take a long " \
                                "period of time depending on which platform you are using."
tensorflow_loaded_model: str = "Model has finished loading; inference will begin once input is provided."
tflite_not_found: str = "TensorFlow Lite could not be found. You may be missing some dependencies."
tflite_model_present: str = "Found a TensorFlow Lite model in the configured path."
tflite_coral_model_present: str = "Found a Coral Edge TPU model in the configured path."
tflite_model_missing: str = "Unable to load a TensorFlow Lite model from the configured path. Please check your " \
                            "configuration and try again."
debug_log: str = "FPS: {fps}; top left: ({xmin}, {ymin}); bottom right: ({xmin}, {ymin})"
stopped_nt: str = "Pipeline stopped by NetworkTables disable command."
stopped_keyboard: str = "Pipeline stopped with KeyboardInterrupt."
error_wrong_arguments: str = "Incorrect number of arguments.\nMLRun should be invoked as follows:\n\tpython3 -m mlrun" \
                             " [config_name]"
error_camera_fault: str = "Camera ID /dev/video{id} did not provide any content when requested."
error_nonexistant_config: str = "The provided configuration name does not exist. You may have to create it yet."
warning_coloredlogs: str = "Coloredlogs is not present; logs will be less readable and difficult to understand."
warning_config_name: str = "WARNING: Configuration not specified; assuming \"desktop\" configuration."
warning_show_debug: str = "WARNING! Showing the output from the pipeline in a window will dramatically reduce" \
                          "performance. You have been warned!"

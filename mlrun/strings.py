# -*- coding: utf-8 -*-
"""Strings for AutoML.

These strings are used by MLRun to ensure that all of the text shown is correct.
"""
mlrun_started: str = "Welcome to MLRun! Starting up..."

debugging_disabled: str = "Debugging is not enabled."
debugging_logs_only: str = "Log-based debugging is enabled."
debugging_show_only: str = "Visualization debugging is enabled. Performance will be dramatically reduced."
debugging_full_enabled: str = "Both log and visualization debugging are enabled. Performance will be dramatically " \
                              "reduced."

tensorflow_deprecation_disabled: str = "TensorFlow deprecation warnings have been disabled. If you intend on " \
                                       "upgrading TensorFlow later, please enable these in your configuration file. " \
                                       "Otherwise, you can ignore this message."
tensorflow_deprecation_enabled: str = "TensorFlow deprecation warnings have been enabled. These can safely be " \
                                      "ignored, or turned off in your configuration file if they don't affect your " \
                                      "use case. "
tensorflow_deprecation_irrelevant: str = "TensorFlow deprecation warnings are irrelevant for your usage case; you " \
                                         "are running a more recent version of TensorFlow. "

tensorflow_log_level_full: str = "TensorFlow minimum logging level set to allow information, warnings, non-fatal " \
                                 "errors, and fatal errors. This may reduce performance; recommended setting is FATAL."
tensorflow_log_level_warnings: str = "TensorFlow minimum logging level set to allow warnings, non-fatal errors and " \
                                     "fatal errors. "
tensorflow_log_level_errors: str = "TensorFlow minimum logging level set to allow non-fatal errors and fatal errors."
tensorflow_log_level_fatal: str = "Tensorflow minimum logging level set to allow only fatal errors."

opencv_loading: str = "Loading OpenCV..."
opencv_successful: str = "Successfully loaded OpenCV."
opencv_unsuccessful: str = "Unable to load OpenCV. Make sure that you have installed OpenCV on your path."
opencv_camera_error: str = "OpenCV was unable to open the camera /dev/video{cam}. Please check your configuration."

networktables_loading: str = "Loading NetworkTables..."
networktables_successful: str = "NetworkTables support is enabled."
networktables_expected_disable: str = "NetworkTables support is disabled. Results will not be broadcasted over the " \
                                      "network."
networktables_unexpected_disable: str = "NetworkTables support is enabled, but PyNetworkTables could not be found in " \
                                        "your Python path. Please make sure that PyNetworkTables is installed."
networktables_connection_established: str = "Established connection with {ip}:{port} over protocol version {ver}."
networktables_connection_lost: str = "Lost connection with NetworkTables server."

tensorflow_legacy_mode: str = "TensorFlow is running in legacy mode. This is a kludge for replacing legacy code with " \
                              "modern TensorFlow 2.0 code. Fix your code, or if your use case is not covered, " \
                              "you may ignore this warning."
tensorflow_legacy_loading: str = "Loading TensorFlow in legacy mode..."
tensorflow_legacy_loaded: str = "TensorFlow loaded in legacy mode."
tensorflow_legacy_error: str = "TensorFlow could not be loaded in legacy mode. Please make sure that TensorFlow is " \
                               "installed."
tensorflow_modern_mode: str = "TensorFlow is running in modern mode."
tensorflow_modern_loading: str = "Loading TensorFlow in modern mode..."
tensorflow_modern_loaded: str = "TensorFlow loaded in modern mode."
tensorflow_modern_error: str = "TensorFlow could not be loaded in modern mode. Please make sure that TensorFlow is " \
                               "installed."

tensorflow_model_present: str = "A model was located at the location specified in your configuration file; continuing."
tensorflow_model_missing: str = "A model was not found in the specified location. Please ensure that your model has " \
                                "a name of 'saved_model.pb' in the specified location."

opencv_tick_frequency: str = "System's stated tick frequency is {freq}."

tensorflow_loading_model: str = "Please wait for TensorFlow to load the model into memory. This may take a long " \
                                "period of time depending on which platform you are using."
tensorflow_loaded_model: str = "Model has finished loading; inference will begin momentarily."

debug_log: str = "FPS: {fps}; top left: ({xmin}, {ymin}); bottom right: ({xmin}, {ymin})"

stopped_nt: str = "Pipeline stopped by NetworkTables disable command."
stopped_keyboard: str = "Pipeline stopped with KeyboardInterrupt."

error_wrong_arguments: str = "Incorrect number of arguments.\nMLRun should be invoked as follows:\n\tpython3 -m mlrun" \
                             " [config_name]"
error_nonexistant_camera: str = "Camera ID /dev/video{id} does not exist!"

average_fps_message: str = "Average FPS: {fps}"

warning_coloredlogs: str = "Coloredlogs is not present; logs will be less readable and difficult to understand."

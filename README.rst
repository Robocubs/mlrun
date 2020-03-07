*****
MLRun
*****

An inference operator for TensorFlow-based object detection models. Designed for modularity and ease of use.

Installation
************

Only supported on Ubuntu 18.04 at this time. You'll need the following dependencies:

* `NVIDIA CUDA Toolkit 10.2 <https://developer.nvidia.com/cuda-downloads>`_ (for Jetson/AArch64: included with JetPack)
* `TensorFlow for Jetson <https://docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform/index.html>`_ (only on AArch64/Jetson systems, follow the instructions exactly and *only* install TensorFlow version 2)
* `Google Coral AI Toolkit <https://coral.ai/docs/accelerator/get-started>`_ (if you want to use the TensorFlow Lite engine)
* `Poetry <https://pypi.org/project/poetry>`_ (make sure to install it with `PipX <https://pipxproject.github.io/pipx/installation/>`_ to avoid conflicts!)
* `python3-opencv <https://packages.ubuntu.com/bionic/python3-opencv>`_ (only on AArch64/Jetson systems)

All the other dependencies are managed by Poetry. Once you've satisfied this somewhat onerous list of requirements:

    >>> git clone https://github.com/Robocubs/mlrun
    >>> poetry install
    >>> python3 -m mlrun.__init__


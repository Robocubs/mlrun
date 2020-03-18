"""Setuptools configuration for MLRun."""
from setuptools import setup, find_packages
from os import path
import sys
import toml

# Error out if running on Python 2.
if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    print("ERROR! This package requires Python 3.6 to use.")
    print("You appear to have Python {}.{} installed.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

# Get the absolute path to our current location.
here = path.abspath(path.dirname(__file__))

# Get most of the meta information from the PyProject TOML file.
with open(path.join(here, "pyproject.toml"), encoding="utf-8") as handle:
    meta = toml.load(handle)

# Get the long description from our README.rst file.
with open(path.join(here, "README.rst"), encoding="utf-8") as handle:
    long_description = handle.read()

# Start the setup process.
setup(
    name=meta.project.name,
    version=meta.project.version,
    description=meta.project.description,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url=meta.project.repository,
    author="Nicholas Hubbard",
    author_email="nhubbard@users.noreply.github.com",
    classifiers=meta.project.classifiers,
    keywords=meta.project.keywords,
    packages=["mlrun"],
    python_requires=">=3.5",
    install_requires=[
        "pip",
        "setuptools",
        "testresources",
        "coloredlogs==14.0",
        "pynetworktables==2020.0.3",
        "numpy==1.18.1",
        "coloredlogs==14.0",
        "pynetworktables==2020.0.3",
        "typing-extensions==3.7.4",
        "typed-config==0.1.3",
        "toml==0.10.0",
        "Click==7.1.1"
    ],
    extras_require={
        "desktop": [
            "tensorflow-gpu==2.1.0",
            "https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp36-cp36m-linux_x86_64.whl",
            "opencv-python==4.2.0.32"
        ],
        "jetson": [
            "numpy-aarch64",
            "future==0.17.1",
            "mock==3.0.5",
            "h5py==2.9.0",
            "keras_preprocessing==1.0.5",
            "keras_applications==1.0.8",
            "gast==0.2.2",
            "futures",
            "protobuf",
            "pybind11",
            "https://developer.download.nvidia.com/compute/redist/jp/v43/tensorflow-gpu/tensorflow_gpu-2.0.0+nv20.1-cp36-cp36m-linux_aarch64.whl",
            "https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp36-cp36m-linux_aarch64.whl"
        ]
    },
    entry_points="""
        [console_scripts]
        mlrun=mlrun.__main__:main
    """
)
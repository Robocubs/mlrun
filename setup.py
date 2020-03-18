"""Setuptools configuration for MLRun."""
import platform
import sys
import subprocess
from os import path
from setuptools import setup
import importlib.util

# Error out if running on Python 2.
if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    print("ERROR! This package requires Python 3.6 to use.")
    print("You appear to have Python {}.{} installed.".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

# Get the absolute path to our current location.
here = path.abspath(path.dirname(__file__))

# Get the long description from our README.rst file.
with open(path.join(here, "README.rst")) as handle:
    long_description = handle.read()

# Get dependency lists from the requirements files.
list_of_dependencies = []

with open(path.join(here, "requirements/all.txt")) as handle:
    all_dependencies = handle.read()
if platform.machine() == "x86_64":
    with open(path.join(here, "requirements/intel.txt")) as handle:
        system_specific_dependencies = handle.read()
elif platform.machine() == "aarch64" or platform.machine() == "arm64":
    with open(path.join(here, "requirements/arm.txt")) as handle:
        system_specific_dependencies = handle.read()

# Process dependency lists.
for dependency in all_dependencies.split("\n"):
    if dependency.startswith("#") or dependency == "":
        continue
    list_of_dependencies.append(dependency)
for dependency in system_specific_dependencies.split("\n"):
    if dependency.startswith("#") or dependency == "":
        continue
    list_of_dependencies.append(dependency)

# Install missing dependencies.
# Some of our dependencies are direct links to wheel files.
# Setuptools doesn't like this, so it fails. Hard.
print("Checking and installing MLRun dependencies...")
for dependency in list_of_dependencies:
    # A lot of edge case handling...
    j = dependency
    if "==" in dependency:
        j = dependency.split("==")[0]
    if "tflite_runtime" in dependency:
        j = "tflite_runtime"
    elif "tensorflow_gpu" in dependency or "tensorflow-gpu" in dependency:
        j = "tensorflow"
    elif "pynetworktables" in dependency:
        j = "networktables"
    elif "opencv" in dependency:
        j = "cv2"
    elif "typed-config" in dependency:
        j = "typedconfig"
    elif "Click" in dependency:
        j = "click"
    if importlib.util.find_spec(j) is None:
        print(f"\t - {dependency}...", end="\b")
        subprocess.run(["python3", "-m", "pip", "install", "-I", "-q", dependency])
        print(". done.")
print("All dependencies are installed and up-to-date.")

# Only import TOML after we know it's installed.
import toml
# Get most of the meta information from the PyProject TOML file.
with open(path.join(here, "pyproject.toml")) as handle:
    meta = toml.load(handle)

# Start the setup process.
setup(
    name=meta["project"]["name"],
    version=meta["project"]["version"],
    description=meta["project"]["description"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url=meta["project"]["repository"],
    author="Nicholas Hubbard",
    author_email="nhubbard@users.noreply.github.com",
    classifiers=meta["project"]["classifiers"],
    keywords=meta["project"]["keywords"],
    packages=["mlrun"],
    python_requires=">3.5",
    entry_points="""
        [console_scripts]
        mlrun=mlrun.__main__:main
    """
)
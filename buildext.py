"""Build extensions with Poetry."""
from Cython.Build import cythonize


def build(setup_kwargs):
	"""Add additional command to generated setup.py file."""
	setup_kwargs.update({
		"ext_modules": cythonize("mlrun/util.pyx")
	})

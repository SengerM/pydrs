import setuptools
# ~ from distutils.core import setup
from Cython.Build import cythonize
import numpy

ext_modules = cythonize("pydrs/pydrs_bindings.pyx")
ext_modules[0].extra_compile_args.extend(['-DOS_LINUX', '-DHAVE_USB', '-DHAVE_LIBUSB10'])
ext_modules[0].include_dirs.extend(['pydrs/cpp/include'])
ext_modules[0].include_dirs.extend([numpy.get_include()])

setuptools.setup(
	name = "pydrs",
	version = "0",
	author = "Matias Senger",
	author_email = "matias.senger@cern.ch",
	description = "Package to control the PSI DRS evaluation board from Python",
	url = "",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires = ['numpy','cython'],
	license = 'MIT',
	ext_modules = ext_modules,
)

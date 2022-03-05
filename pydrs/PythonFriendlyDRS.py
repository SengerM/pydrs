from .pydrs_bindings import PyBoard
import numpy as np
from . import _check_types as ct

class PythonFriendlyBoard:
	"""A wrapper for the `PyBoard` class that is less "C++ masochist" and 
	more "Python friendly"."""
	def __init__(self, board, auto_init=True):
		if not isinstance(board, PyBoard):
			raise TypeError(f'`board` must be an instance of {repr(PyBoard)}.')
		self.board = board
		if auto_init:
			self.board.init()
	
	@property
	def serial_number(self) -> str:
		"""Return the serial number of the board as a string."""
		if not hasattr(self, '_serial_number'):
			self._serial_number = str(self.board.get_board_serial_number())
		return self._serial_number
	
	@property
	def firmware_version(self) -> str:
		"""Return the firmware version of the board as a string."""
		if not hasattr(self, '_firmware_version'):
			self._firmware_version = str(self.board.get_firmware_version())
		return self._firmware_version
	
	def set_sampling_frequency(self, frequency_Hz: float, wait: bool=True):
		"""Set the sampling frequency.
		Parameters
		----------
		frequency_Hz: float
			The value for the sampling frequency in Hertz. If you want
			a sampling frequency of 1 GHz then use `frequency_Hz=1e9`.
		wait: bool, default True
			Wait until the PLL is locked.
		"""
		ct.check_is_instance(frequency_Hz, 'frequency_Hz', (int, float))
		ct.check_is_instance(wait, 'wait', bool)
		if not 100e6 <= frequency_Hz <= 6e9: # This is from `DRS.cpp`: /* allowed range is 100 MHz to 6 GHz */
			raise ValueError(f'`frequency_Hz` must be between 100e6 and 6e12, received {frequency_Hz}.')
		self.board.set_frequency(freq=frequency_Hz*1e-9, wait=wait)
	

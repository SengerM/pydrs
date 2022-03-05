from .pydrs_bindings import PyBoard
import numpy as np

class PythonFriendlyBoard:
	"""A wrapper for the `PyBoard` class that is less "C++ masochist" and 
	more "Python friendly"."""
	def __init__(self, board):
		if not isinstance(board, PyBoard):
			raise TypeError(f'`board` must be an instance of {repr(PyBoard)}.')
		self.board = board
	
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

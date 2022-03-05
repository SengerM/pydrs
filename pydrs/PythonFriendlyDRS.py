from .pydrs_bindings import PyDRS
import numpy as np
from . import _check_types as ct

class PythonFriendlyBoard:
	"""A wrapper for the `pydrs_bindings.PyBoard` class that is less 
	"C++ masochist" and more "Python friendly". This means that error 
	messages are meaningful, data types are those you would expect in 
	Python, and things are made	to make your life easier."""
	def __init__(self, n_board: int=0, auto_init=True):
		"""Create an instance of `PythonFriendlyBoard`.
		
		Parameters
		----------
		n_board: int, default `0`
			Number of board to connect to. If you are using only a single
			evaluation board connected through the USB, this number
			should be 0, which is the default. I have never used more 
			than one board, but probably if you put 1 you connect to the
			second board and so on.
		auto_init: bool, default `True`
			If `True` the `init` method is called which I believe it sets
			the board in a well defined state (like a reset).
		"""
		ct.check_is_instance(n_board,'n_board',int)
		ct.check_is_instance(auto_init,'auto_init',bool)
		self.board = PyDRS().get_board(n_board)
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
	
	@property
	def idn(self) -> str:
		"""Return a string with information about the board."""
		return f'PSI DRS4 Evaluation Board (serial number: {self.serial_number}, firmware version: {self.firmware_version})'
	
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
	
	def set_transparent_mode(self, status: str):
		"""Enable or disable the transparent mode.
	
		Parameters
		----------
		status: str
			Either 'on' or 'off'.
		"""
		ct.check_is_instance(status, 'status', str)
		if status.lower() not in {'on','off'}:
			raise ValueError(f'`status` must be either "on" or "off", received {repr(status)}.')
		self.board.set_transp_mode(True if status=='on' else False)
	
	def set_input_range(self, center: float):
		"""Set the input range.
		
		Parameters
		----------
		center: float
			From the help in `drscl` app: "Input range to <center>+=0.5V".
		"""
		ct.check_is_instance(center, 'center', (int, float))
		if not 0 <= center <= .5:
			raise ValueError(f'`center` must be between 0 and 0.5, received {repr(center)}.') # In `DRS.cpp` we find this: `if (center < 0 || center > 0.5) return 0;`
		self.board.set_input_range(center)
	
	def enable_trigger(self, flag1: bool, flag2: bool):
		"""Enable the trigger? Sorry, there is no documentation about this
		function.
	
		Parameters
		----------
		flag1: bool
			I have no idea what this flag does.
		flag2: bool
			I have no idea either. Sorry.
		"""
		ct.check_are_instances({'flag1':flag1,'flag2':flag2},bool)
		self.board.enable_trigger(flag1,flag2)
	
	def set_trigger_source(self, source: str):
		"""Set the trigger source (CH1, CH2, ...).
	
		Parameters
		----------
		source: str
			One of 'CH1','CH2','CH3','CH4','EXT'.
		"""
		VALID_TRIGGER_SOURCES = ['CH1','CH2','CH3','CH4','EXT']
		ct.check_is_instance(source, 'source', str)
		if source.upper() not in VALID_TRIGGER_SOURCES:
			raise ValueError(f'`source` must be one of {VALID_TRIGGER_SOURCES}, received {repr(source)}.')
		source = source.upper() # More human friendly to have this case unsensitive.
		if source=='EXT':
			raise NotImplementedError(f'I have implemented the external trigger, but I have not checked that it works.')
		self.board.set_trigger_source(1<<VALID_TRIGGER_SOURCES.index(source))
	
	def set_trigger_level(self, level: float):
		"""Set the trigger level, in volts.
	
		Parameters
		----------
		level: float
			Voltage value for the trigger level.
		"""
		ct.check_is_instance(level, 'level', (int, float))
		self.board.set_trigger_level(level)
	
	def set_trigger_polarity(self, edge: str):
		"""Set the trigger polarity to rising edge or falling edge.
	
		Parameters
		----------
		edge: str
			Either 'rising' or 'falling'.
		"""
		ct.check_is_instance(edge, 'edge', str)
		VALID_EDGE_VALUES = {'falling','rising'}
		if edge.lower() not in VALID_EDGE_VALUES:
			raise ValueError(f'`edge` must be one of {VALID_EDGE_VALUES}, received {repr(edge)}.')
		edge = edge.lower() # Make it case unsensitive, more human friendly.
		self.board.set_trigger_polarity(True if edge=='falling' else False)
	
	def set_trigger_delay(self, seconds: float):
		"""Set the trigger delay in seconds.
	
		Parameters
		----------
		seconds: float
			Delay time, in seconds. If you want 100 ns use `seconds=100e-9`.
		"""
		ct.check_is_instance(seconds,'seconds',(float, int))
		self.board.set_trigger_delay_ns(seconds*1e9)
	
	def wait_for_single_trigger(self):
		"""Blocks the execution of the program until the board triggers
		once. Then, the data is brought to the computer and you can later
		on access to it using the `get_waveform` method.
		"""
		# I wrote this function following the example `drs_exam.cpp`.
		self.board.start_domino() # Not sure what this is doing, but it is needed.
		while self.board.is_busy(): # Wait for the trigger to happen.
			pass
		self.board.transfer_waves(0,8) # Bring all the waveforms from board to PC.
		
	def get_waveform(self, n_channel: int) -> dict:
		"""After the board has triggered you can use this method to access
		the data.
		
		Parameters
		----------
		n_channel: int
			Number of channel from which to get the data.
		
		Returns
		-------
		waveform_data: dict
			A dictionary of the form `{'Time (s)': np.array, 'Amplitude (V)': np.array}`
			containing the data.
		"""
		# I wrote this function following the example `drs_exam.cpp`.
		ct.check_is_instance(n_channel,'n_channel',int)
		if n_channel not in {1,2,3,4}:
			raise ValueError(f'`n_channel` must be one of 1,2,3 or 4, received {repr(n_channel)}.')
		self.board.get_time(0,n_channel-1,self.board.get_trigger_cell()) # Not sure what this does, but it was in `drs_exam.cpp`.
		return {
			'Amplitude (V)': np.array(self.board.get_waveform_buffer(n_channel-1))*1e-3,
			'Time (s)': np.array(self.board.get_time_buffer(n_channel-1))*1e-9,
		}

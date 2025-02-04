# distutils: language = c++
# distutils: sources = pydrs/cpp/DRS.cpp pydrs/cpp/mxml.c pydrs/cpp/strlcpy.c pydrs/cpp/averager.cpp pydrs/cpp/musbstd.c
# distutils: libraries = usb-1.0 util
from libcpp cimport bool
cimport cython

cdef extern from "DRS.h" nogil:
	cdef cppclass DRSBoard:
		int GetBoardSerialNumber()
		int GetFirmwareVersion()
		int Init()
		int SetFrequency(double freq, bool wait)
		int SetInputRange(double center)
		int SetTranspMode(int flag)
		int EnableTrigger(int flag1, int flag2)
		int SetTriggerSource(int source)
		int SetTriggerDelayNs(int delay)
		int SetTriggerPolarity(bool negative)
		int SetTriggerLevel(double value)
		int GetBoardType()
		int StartDomino()
		int SetDominoMode(unsigned char mode)
		int SoftTrigger()
		int IsBusy()
		int TransferWaves(int firstChannel, int lastChannel)
		int IsEventAvailable()
		int GetWave(unsigned int chipIndex, unsigned char channel, float *waveform)
		double GetTemperature()
		int GetTime(unsigned int chipIndex, int channelIndex, int tc, float *time) # I could not find this function defined in the `DRS.cpp` file nor in `DRS.h`, but it is used in the `drs_exam.cpp` example. I don't know where it is defined or why does it work, but it works...
		int GetTriggerCell(unsigned int)

cdef extern from "DRS.h" nogil:
	cdef cppclass DRS:
		DRS() except +
		int GetNumberOfBoards()
		DRSBoard *GetBoard(int)

cdef class PyDRS:
	cdef DRS *drs

	def __cinit__(self):
		self.drs = new DRS()

	#dealloc deletes board :/
	def free(self):
		del self.drs

	def get_number_of_boards(self):
		return self.drs.GetNumberOfBoards()

	def get_board(self, int i):
		board = PyDRSBoard()
		board.from_board(self.drs.GetBoard(i), self.drs)
		return board

cdef class PyDRSBoard:
	cdef DRSBoard *board
	cdef DRS *drs
	cdef float waveforms_buffer[8][1024]
	cdef float times_buffer[8][1024]

	cdef void from_board(self, DRSBoard *board, DRS *drs):
		self.board = board
		self.drs = drs

	def __dealloc__(self):
		del self.board

	def get_board_serial_number(self):
		return self.board.GetBoardSerialNumber()

	def get_firmware_version(self):
		return self.board.GetFirmwareVersion()

	def get_board_type(self):
		return self.board.GetBoardType()

	def get_temperature(self):
		return self.board.GetTemperature()

	def init(self):
		self.board.Init()

	def set_frequency(self, freq, wait=True):
		return self.board.SetFrequency(freq, wait)

	def set_input_range(self, center):
		return self.board.SetInputRange(center)

	def set_transp_mode(self, flag):
		return self.board.SetTranspMode(flag)

	def enable_trigger(self, flag1, flag2):
		return self.board.EnableTrigger(flag1, flag2)

	def set_trigger_source(self, source):
		return self.board.SetTriggerSource(source)

	def set_trigger_delay_ns(self, ns):
		return self.board.SetTriggerDelayNs(ns)

	def set_trigger_polarity(self, pol):
		return self.board.SetTriggerPolarity(pol)

	def set_trigger_level(self, lvl):
		return self.board.SetTriggerLevel(lvl)

	def get_trigger_cell(self):
		return self.board.GetTriggerCell(0)

	def start_domino(self):
		return self.board.StartDomino()

	def soft_trigger(self):
		return self.board.SoftTrigger()

	def is_busy(self):
		return self.board.IsBusy()

	def transfer_waves(self, firstChannel: int, lastChannel: int):
		return self.board.TransferWaves(firstChannel, lastChannel)

	def is_event_available(self):
		return self.board.IsEventAvailable()

	def get_time(self, chip_index: int, channel_index: int, tc: int):
		return self.board.GetTime(chip_index, channel_index, tc, self.times_buffer[channel_index])

	@cython.boundscheck(False)
	cdef get_wave(self, unsigned int chip_index, unsigned char channel):
		self.board.GetWave(chip_index, 2*channel, self.waveforms_buffer[channel])

	def set_domino_mode(self, mode):
		self.board.SetDominoMode(mode)
	
	cpdef get_waveform_buffer(self, int n_channel):
		VALID_N_CHANNEL = {0,1,2,3}
		if n_channel not in VALID_N_CHANNEL:
			raise ValueError(f'`n_channel` must be in {repr(VALID_N_CHANNEL)}.')
		self.get_wave(0, n_channel) # I don't like the `0` hardcoded here, but I am not sure what it does...
		return self.waveforms_buffer[n_channel]
	
	cpdef get_time_buffer(self, int n_channel):
		VALID_N_CHANNEL = {0,1,2,3}
		if n_channel not in VALID_N_CHANNEL:
			raise ValueError(f'`n_channel` must be in {repr(VALID_N_CHANNEL)}.')
		self.get_wave(0, n_channel) # I don't like the `0` hardcoded here, but I am not sure what it does...
		return self.times_buffer[n_channel]

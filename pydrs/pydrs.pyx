# distutils: language = c++
# distutils: sources = pydrs/cpp/DRS.cpp pydrs/cpp/mxml.c pydrs/cpp/strlcpy.c pydrs/cpp/averager.cpp pydrs/cpp/musbstd.c
# distutils: libraries = usb-1.0 util
from libcpp cimport bool
from libc.math cimport fabs
cimport numpy as np
cimport cython
import numpy as npy
cdef bool can_remove = 1
from datetime import datetime
from struct import pack


cdef extern from "DRS.h" nogil:
	cdef cppclass DRSBoard:
		int GetBoardSerialNumber()
		int GetFirmwareVersion()
		int Init()
		int SetFrequency(double, bool)
		int SetInputRange(double)
		int SetTranspMode(int)
		int EnableTrigger(int, int)
		int SetTriggerSource(int)
		int SetTriggerDelayPercent(int)
		int SetTriggerDelayNs(int)
		int SetTriggerPolarity(int)
		int SetTriggerLevel(int)
		int GetBoardType()
		int StartDomino()
		int SetDominoMode(unsigned char)
		int SoftTrigger()
		int IsBusy()
		int TransferWaves()
		int TransferWaves(int firstChannel, int lastChannel)
		int TransferWaves(unsigned char*, int, int)
		int IsEventAvailable()
		int GetWave(unsigned int, unsigned char, float *)
		int GetWave(unsigned int, unsigned char, float *, bool, int, int, bool, float, bool)
		int GetWave(unsigned char *, unsigned int, unsigned char, float *, bool, int, int, bool, float, bool)
		double GetTemperature()
		int GetChannelCascading()
		int GetTimeCalibration(unsigned int, int, int, float *, bool)
		int GetTriggerCell(unsigned int)
		int GetStopCell(unsigned int)
		int GetWaveformBufferSize()
		unsigned char GetStopWSR(unsigned int)

cdef extern from "DRS.h" nogil:
	cdef cppclass DRS:
		DRS() except +
		int GetNumberOfBoards()
		DRSBoard *GetBoard(int)


cdef extern from "time.h" nogil:
	ctypedef int time_t
	time_t time(time_t *)


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
		board = PyBoard()
		board.from_board(self.drs.GetBoard(i), self.drs)
		return board


cdef class PyBoard:
	cdef DRSBoard *board
	cdef DRS *drs
	cdef public int sn, fw
	cdef float data[4][1024]
	cdef public float center
	cdef readonly bool normaltrigger
	cdef object ba
	cdef unsigned char[18432] buf

	cdef void from_board(self, DRSBoard *board, DRS *drs):
		self.board = board
		self.drs = drs

	def __dealloc__(self):
		del self.board

	def get_board_serial_number(self):
		self.sn = self.board.GetBoardSerialNumber()
		return self.sn

	def get_firmware_version(self):
		self.fw = self.board.GetFirmwareVersion()
		return self.fw

	def get_board_type(self):
		return self.board.GetBoardType()

	def get_temperature(self):
		return self.board.GetTemperature()

	def init(self):
		self.board.Init()

	def set_frequency(self, freq, wait=True):
		return self.board.SetFrequency(freq, wait)

	def set_input_range(self, center):
		self.center = center
		return self.board.SetInputRange(center)

	def set_transp_mode(self, flag):
		return self.board.SetTranspMode(flag)

	def enable_trigger(self, flag1, flag2):
		return self.board.EnableTrigger(flag1, flag2)

	def set_trigger_mode(self, mode):
		self.normaltrigger = mode

	def set_trigger_source(self, source):
		return self.board.SetTriggerSource(source)

	def set_trigger_delay_percent(self, percent):
		return self.board.SetTriggerDelayPercent(percent)
	
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

	def get_channel_cascading(self):
		return self.board.GetChannelCascading()

	def get_stop_cell(self, chip):
		return self.board.GetStopCell(chip)

	@cython.boundscheck(False)
	cdef get_waveform(self, unsigned int chip_index, unsigned char channel):
		self.board.GetWave(chip_index, channel*2, self.data[channel])

	@cython.boundscheck(False)
	cdef get_waveforms(self, unsigned int chip_index, np.ndarray[long] channels):
		cdef int i, channel
		for channel in channels:
			assert channel < 4
		self.board.TransferWaves(self.buf, 0, 8)
		cdef int trig_cell = self.board.GetStopCell(chip_index)

		for channel in channels:
			self.board.GetWave(self.buf, chip_index, channel*2, self.data[channel], True, trig_cell, 0, False, 0, True)

			self.data[channel][1] = 2*self.data[channel][2] - self.data[channel][3]
			self.data[channel][0] = 2*self.data[channel][1] - self.data[channel][2]

		if 3 not in channels:
			self.board.GetWave(self.buf, chip_index, 6, self.data[3], True, trig_cell, 0, False, 0, True)

			self.data[3][1] = 2.*self.data[3][2] - self.data[3][3]
			self.data[3][0] = 2.*self.data[3][1] - self.data[3][2]

	cpdef get_raw(self, int channel):
		VALID_N_CHANNEL = {0,1,2,3}
		if channel not in VALID_N_CHANNEL:
			raise ValueError(f'`n_channel` must be in {repr(VALID_N_CHANNEL)}.')
		self.get_waveform(0, channel)
		return self.data[channel]
	
	cdef _get_multiple(self, np.ndarray[long] channels):
		cdef int i, j
		self.get_waveforms(0, channels)
		for i in range(1024):
			for j in range(4):
				self.data[j][i] = (self.data[j][i] / 1000. - self.center + 0.5) * 65535

	def set_domino_mode(self, mode):
		self.board.SetDominoMode(mode)

	cpdef get_multiple(self, np.ndarray[long] channels):
		self._get_multiple(channels)
		cdef np.ndarray[float, ndim=2] parr = npy.zeros((4, 1024),ndtype=npy.float32)
		cdef int i, j
		for i in range(4):
			for j in range(1024):
				parr[i][j] = self.data[i][j]
		return parr

	def get_trigger(self):
		cdef int t
		self.board.StartDomino()
		if not self.normaltrigger:
			self.board.SoftTrigger()
			while self.board.IsBusy():
				pass
			return True
		else:
			t = time(NULL)
			while not self.board.IsEventAvailable() or self.board.IsBusy():
				if (time(NULL) - t) > 5:
					return False
			return True

	def get_triggered(self, np.ndarray[long] channels):
		if self.get_trigger():
			return self.get_multiple(channels)

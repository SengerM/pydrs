from pydrs.pydrs_bindings import PyDRS
from pydrs.PythonFriendlyDRS import PythonFriendlyBoard
import numpy as np
import plotly.express as px
import pandas

drs = PyDRS()
board = drs.get_board(0)
friendly_board = PythonFriendlyBoard(board)
print(f'Connected with serial number: {friendly_board.serial_number}, firmware version: {friendly_board.firmware_version}')

friendly_board.set_sampling_frequency(3e9)
friendly_board.set_transparent_mode('on')
friendly_board.set_input_range(0)
friendly_board.enable_trigger(True,False)
friendly_board.set_trigger_source('ch2')
friendly_board.set_trigger_level(.2)
friendly_board.set_trigger_polarity('rising')
friendly_board.set_trigger_delay(166e-9)

df = pandas.DataFrame()
for n_trigger in range(5):
	friendly_board.wait_for_single_trigger()
	for n_channel in [1,2,3,4]:
		for n_acquire in [1]:
			_ = pandas.DataFrame(
				friendly_board.get_waveform(n_channel),
			)
			_['n_trigger'] = n_trigger
			_['n_channel'] = n_channel
			_['n_sample'] = _.index
			_['n_acquire'] = n_acquire
			df = df.append(_, ignore_index=True)

fig = px.line(
	df,
	x = 'Time (s)',
	y = 'Amplitude (V)',
	color = 'n_trigger',
	facet_row = 'n_channel',
	symbol = 'n_acquire',
)
fig.write_html('deleteme.html', include_plotlyjs='cdn')

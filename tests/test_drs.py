from pydrs import PyDRS
import numpy as np
import plotly.express as px
import pandas

drs = PyDRS()
board = drs.get_board(0)
print(f'Connected with serial number: {board.get_board_serial_number()}, firmware version: {board.get_firmware_version()}')

board.init()
board.set_frequency(1, True)
board.set_transp_mode(1)
board.set_input_range(0)
board.enable_trigger(1,0)
board.set_trigger_source(1<<0)
board.set_trigger_level(-.05)
board.set_trigger_polarity(True)
board.set_trigger_delay_ns(980)

df = pandas.DataFrame()
for n_trigger in range(5):
	board.start_domino()
	while board.is_busy():
		pass
	board.transfer_waves(0,8) # Bring waveforms from board to PC.
	for n_channel in [0,1,2,3]:
		# ~ board.get_wave(n_channel)
		board.get_time(0,n_channel,board.get_trigger_cell())
		_ = pandas.DataFrame(
			{
				'Amplitude (V)': np.array(board.get_waveform_buffer(n_channel))*1e-3,
				'Time (s)': np.array(board.get_time_buffer(n_channel))*1e-9,
			}
		)
		_['n_trigger'] = n_trigger
		_['n_channel'] = n_channel
		_['n_sample'] = _.index
		df = df.append(_, ignore_index=True)

fig = px.line(
	df,
	x = 'Time (s)',
	y = 'Amplitude (V)',
	color = 'n_trigger',
	facet_row = 'n_channel',
)
fig.write_html('deleteme.html', include_plotlyjs='cdn')

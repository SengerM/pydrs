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
board.set_trigger_source(1<<3)
board.set_trigger_level(-.05)
board.set_trigger_polarity(True)
board.set_trigger_delay_ns(980)

df = pandas.DataFrame()
for n_trigger in range(5):
	board.start_domino()
	while board.is_busy():
		pass
	board.bring_all_waveforms(0,8)
	for n_channel in [0,1,2,3]:
		_ = pandas.DataFrame(
			{
				'raw': board.get_raw(n_channel),
			}
		)
		_['n_trigger'] = n_trigger
		_['n_channel'] = n_channel
		_['n_sample'] = _.index
		df = df.append(_, ignore_index=True)

fig = px.line(
	df,
	x = 'n_sample',
	y = 'raw',
	color = 'n_trigger',
	facet_row = 'n_channel',
)
fig.write_html('deleteme.html', include_plotlyjs='cdn')

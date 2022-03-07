from pydrs import PythonFriendlyBoard
import numpy as np
import plotly.express as px
import pandas

board = PythonFriendlyBoard() # Open the connection with the board. Here we assume only one board is connected to PC.
print(f'Connected with {repr(board.idn)}')

SAMPLING_FREQ = 3.5e9
TRIGGER_DELAY = 100e-9
# The following lines are self explanatory :)
board.set_sampling_frequency(Hz=SAMPLING_FREQ)
board.set_transparent_mode('on')
board.set_input_range(center=0)
board.enable_trigger(True,False) # Don't know what this line does, it was in the example `drs_exam.cpp`.
board.set_trigger_source('ch4')
board.set_trigger_level(volts=-.1)
board.set_trigger_polarity(edge='falling')
board.set_trigger_delay(seconds=TRIGGER_DELAY)

df = pandas.DataFrame() # Here I will store some data to plot later on.
for n_trigger in range(5):
	board.wait_for_single_trigger() # Halt the program until the board triggers so then we acquire the data.
	for n_channel in [1,2,4]:
		waveform_data = board.get_waveform(n_channel) # This returns data in standard numpy arrays.
		# Store the data in the data frame to plot later on...
		temp_df = pandas.DataFrame(waveform_data)
		temp_df['n_trigger'] = n_trigger
		temp_df['n_channel'] = n_channel
		temp_df['n_sample'] = temp_df.index
		df = df.append(temp_df, ignore_index=True)

# Plot...
fig = px.line(
	title = f'Sampling frequency = {SAMPLING_FREQ:.2e} Hz, trigger delay = {TRIGGER_DELAY:.2e} s',
	data_frame = df,
	x = 'Time (s)',
	y = 'Amplitude (V)',
	color = 'n_trigger',
	facet_row = 'n_channel',
)
fig.write_html('deleteme.html', include_plotlyjs='cdn')

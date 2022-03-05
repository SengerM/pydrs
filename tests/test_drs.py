from pydrs.PythonFriendlyDRS import PythonFriendlyBoard
import numpy as np
import plotly.express as px
import pandas

friendly_board = PythonFriendlyBoard() # Open the connection with the board. Here we assume only one board is connected to PC.
print(f'Connected with {repr(friendly_board.idn)}')

# The following lines are self explanatory :)
friendly_board.set_sampling_frequency(Hz=3e9)
friendly_board.set_transparent_mode('on')
friendly_board.set_input_range(center=0)
friendly_board.enable_trigger(True,False) # Don't know what this line does, it was in the example `drs_exam.cpp`.
friendly_board.set_trigger_source('ch2')
friendly_board.set_trigger_level(volts=.2)
friendly_board.set_trigger_polarity(edge='rising')
friendly_board.set_trigger_delay(seconds=166e-9)

df = pandas.DataFrame() # Here I will store some data to plot later on.
for n_trigger in range(5):
	friendly_board.wait_for_single_trigger() # Halt the program until the board triggers so then we acquire the data.
	for n_channel in [1,2,3,4]:
		waveform_data = friendly_board.get_waveform(n_channel)
		# Store the data in the data frame to plot later on...
		temp_df = pandas.DataFrame(waveform_data)
		temp_df['n_trigger'] = n_trigger
		temp_df['n_channel'] = n_channel
		temp_df['n_sample'] = temp_df.index
		df = df.append(temp_df, ignore_index=True)

# Plot...
fig = px.line(
	df,
	x = 'Time (s)',
	y = 'Amplitude (V)',
	color = 'n_trigger',
	facet_row = 'n_channel',
)
fig.write_html('deleteme.html', include_plotlyjs='cdn')

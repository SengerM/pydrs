import pydrs
import plotly.express as px
import pandas
from pathlib import Path

board = pydrs.get_board(0) # Open the connection with the board. Here we assume only one board is connected to PC.
print(f'Connected with {board.idn}')

# The following lines are self explanatory :)
board.set_sampling_frequency(Hz=5e9)
board.set_transparent_mode('on')
board.set_input_range(center=0)
board.enable_trigger(True,False) # Don't know what this line does, it was in the example `drs_exam.cpp`.
board.set_trigger_source('ch4')
board.set_trigger_level(volts=-.1)
board.set_trigger_polarity(edge='falling')
board.set_trigger_delay(seconds=150e-9)

df = pandas.DataFrame() # Here I will store the data to plot later on.
for n_trigger in range(5): # Trigger a few times, not just once.
	board.wait_for_single_trigger() # Halt the program until the board triggers so then we acquire the data.
	for n_channel in [1,2,4]:
		waveform_data = board.get_waveform(n_channel) # This returns data in standard numpy arrays, as you would probably expect in Python.
		# Store the data in the data frame to plot later on...
		temp_df = pandas.DataFrame(waveform_data)
		temp_df['n_trigger'] = n_trigger
		temp_df['n_channel'] = n_channel
		temp_df['n_sample'] = temp_df.index
		df = df.append(temp_df, ignore_index=True)

# Plot...
fig = px.line(
	title = f'Signals acquired with the PSI DRS4 Evaluation Board<br><sup>Using <em>pydrs</em> in Python</sup>',
	data_frame = df,
	x = 'Time (s)',
	y = 'Amplitude (V)',
	color = 'n_trigger',
	facet_row = 'n_channel',
)
plot_file_path = Path.home()/Path('pydrs_test.html')
fig.write_html(str(plot_file_path), include_plotlyjs='cdn')
print(f'You can now open {plot_file_path} with your favorite web broser and see the signals :)')

# pydrs

Use the [PSI DRS4 evaluation board](https://www.psi.ch/en/drs/evaluation-board) as an acquisition board easily with Python.

![PSI DRS4 Evaluation Board V5](https://www.psi.ch/sites/default/files/styles/primer_full_xl/public/import/drs/EvaluationBoardEN/drs4_eval5_front.jpg?itok=KrhB4thW)

**Note** Currently this was only tested on Ubuntu 20.04.

## Installation

Should be as easy as
```
pip install git+https://github.com/SengerM/pydrs
```
You may need to additionally install [Cython](https://cython.org/) (`pip install cython` should do the trick) and [libusb](https://libusb.info/) (in my case in Ubuntu `sudo apt install libusb-1.0-0-dev` worked).

## Usage

This package was designed to be easy and intuitive to use. Below there is a simple example, further examples [here](examples).
```Python
import pydrs

board = pydrs.get_board(0) # Open the connection with the board number 0.
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

print('Waiting for trigger...')
board.wait_for_single_trigger() # Halt the program until the board triggers so then we acquire the data.

waveform_data = board.get_waveform(n_channel=1) # This returns data in standard numpy arrays, as you would probably expect in Python.

print(waveform_data)
```
The previous code should print something like
```
Connected with PSI DRS4 Evaluation Board (serial number: 2946, firmware version: 30000)
{'Amplitude (V)': array([-0.0046    , -0.17189999, -0.0068    , ..., -0.007     ,
       -0.0064    , -0.0073    ]), 
 'Time (s)': array([0.00000000e+00, 1.95312500e-10, 3.90625000e-10, ...,
       1.99414063e-07, 1.99609375e-07, 1.99804688e-07])}
```

## Additional remarks

The C++ library that *pydrs* binds can be found [here](https://www.psi.ch/en/drs/software-download). To use *pydrs* you don't need to install it as I have included a copy of the C++ source files required so the installation of *pydrs* is trivial. It is recommended to install their software anyway in order to have access to the graphical interface *drsosc*.

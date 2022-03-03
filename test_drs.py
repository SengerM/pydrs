from pydrs import PyDRS

drs = PyDRS()
board = drs.get_board(0)
print(f'Serial number: {board.get_board_serial_number()}, firmware version: {board.get_firmware_version()}')

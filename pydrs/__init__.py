from .PythonFriendlyDRS import PythonFriendlyBoard
from . import _check_types as ct
from .pydrs_bindings import PyDRS

drs = PyDRS()

def get_board(n_board: int, auto_init: bool=True):
	"""Returns an instance of `PythonFriendlyBoard`.
	
	Parameters
	----------
	n_board: int
		Number of board to link the `PythonFriendlyBoard` instance to.
	auto_init: bool, default True
		If `True` the `DRS::Init` method is called.
	
	Returns
	-------
	board: PythonFriendlyBoard
		An instance to control the board.
	"""
	ct.check_is_instance(n_board,'n_board',int)
	ct.check_is_instance(auto_init,'auto_init',bool)
	board = PythonFriendlyBoard(drs.get_board(n_board))
	if auto_init:
		board.init()
	return board

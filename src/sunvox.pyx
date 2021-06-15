from sunvox cimport *

def hello():
	sv_load_dll()
	ver = sv_init(NULL, 44100, 2, 0)
	if ver >= 0:
		sv_open_slot(0)
		sv_close_slot(0)
		sv_deinit()
	sv_unload_dll()

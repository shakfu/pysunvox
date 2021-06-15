import time

from sunvox cimport *


def hello():
    sv_load_dll()
    ver = sv_init(NULL, 44100, 2, 0)
    if ver >= 0:
        sv_open_slot(0)
        sv_close_slot(0)
        sv_deinit()
    sv_unload_dll()


def play(path: str, volume: int = 256, slot: int = 0, secs: int = 10):
    sv_load_dll()
    ver = sv_init(NULL, 44100, 2, 0)
    if ver >= 0:
        sv_open_slot(slot)
        sv_load(slot, path.encode('utf8'))
        sv_volume(slot, volume)
        sv_play_from_beginning(slot)
        time.sleep(secs)
        sv_stop(slot)
        sv_close_slot(slot)
        sv_deinit()
    sv_unload_dll()


cdef class Patch:
    cdef readonly str path
    cdef readonly int slot
    cdef readonly int srate
    cdef readonly int nchannels
    cdef readonly uint32_t flags

    def __init__(self, path: str, slot: int = 0, 
                 srate: int = 44100, nchannels: int = 2, flags: uint32_t = 0):
        self.path = path
        self.slot = slot
        self.srate = srate
        self.nchannels = nchannels
        self.flags = flags

    def play(self, volume: int = 256, secs: int = 10):
        sv_load_dll()
        ver = sv_init(NULL, self.srate, self.nchannels, self.flags)
        if ver >= 0:
            sv_open_slot(self.slot)
            sv_load(self.slot, self.path.encode('utf8'))
            sv_volume(self.slot, volume)
            sv_play_from_beginning(self.slot)
            time.sleep(secs)
            sv_stop(self.slot)
            sv_close_slot(self.slot)
            sv_deinit()
        sv_unload_dll()

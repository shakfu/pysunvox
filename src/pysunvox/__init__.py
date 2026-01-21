"""
pysunvox - Python bindings for the SunVox modular synthesizer library.

This package provides two API levels:

1. High-level API (pysunvox.sunvox):
   Pythonic classes with context managers, properties, and type hints.

   Example:
       from pysunvox import SunVox, Slot

       with SunVox(sample_rate=44100) as sv:
           with sv.open_slot(0) as slot:
               slot.load("song.sunvox")
               print(f"Song: {slot.name}, BPM: {slot.bpm}")
               slot.play()

2. Low-level API (pysunvox._core):
   Direct 1:1 wrappers of the C sv_* functions.

   Example:
       from pysunvox import _core

       _core.init(None, 44100, 2, 0)
       _core.open_slot(0)
       _core.load(0, "song.sunvox")
       _core.play(0)
       _core.close_slot(0)
       _core.deinit()
"""

from pysunvox._core import (
    # Note class
    Note,
    # Constants - Note commands
    NOTECMD_NOTE_OFF,
    NOTECMD_ALL_NOTES_OFF,
    NOTECMD_CLEAN_SYNTHS,
    NOTECMD_STOP,
    NOTECMD_PLAY,
    NOTECMD_SET_PITCH,
    NOTECMD_CLEAN_MODULE,
    # Constants - Init flags
    SV_INIT_FLAG_NO_DEBUG_OUTPUT,
    SV_INIT_FLAG_USER_AUDIO_CALLBACK,
    SV_INIT_FLAG_OFFLINE,
    SV_INIT_FLAG_AUDIO_INT16,
    SV_INIT_FLAG_AUDIO_FLOAT32,
    SV_INIT_FLAG_ONE_THREAD,
    # Constants - Time map flags
    SV_TIME_MAP_SPEED,
    SV_TIME_MAP_FRAMECNT,
    # Constants - Module flags
    SV_MODULE_FLAG_EXISTS,
    SV_MODULE_FLAG_GENERATOR,
    SV_MODULE_FLAG_EFFECT,
    SV_MODULE_FLAG_MUTE,
    SV_MODULE_FLAG_SOLO,
    SV_MODULE_FLAG_BYPASS,
    SV_MODULE_INPUTS_OFF,
    SV_MODULE_INPUTS_MASK,
    SV_MODULE_OUTPUTS_OFF,
    SV_MODULE_OUTPUTS_MASK,
)

from pysunvox.sunvox import (
    SunVox,
    SunVoxError,
    Slot,
    Module,
    Controller,
    Pattern,
)

__all__ = [
    # High-level API classes
    "SunVox",
    "SunVoxError",
    "Slot",
    "Module",
    "Controller",
    "Pattern",
    # Low-level Note class
    "Note",
    # Constants - Note commands
    "NOTECMD_NOTE_OFF",
    "NOTECMD_ALL_NOTES_OFF",
    "NOTECMD_CLEAN_SYNTHS",
    "NOTECMD_STOP",
    "NOTECMD_PLAY",
    "NOTECMD_SET_PITCH",
    "NOTECMD_CLEAN_MODULE",
    # Constants - Init flags
    "SV_INIT_FLAG_NO_DEBUG_OUTPUT",
    "SV_INIT_FLAG_USER_AUDIO_CALLBACK",
    "SV_INIT_FLAG_OFFLINE",
    "SV_INIT_FLAG_AUDIO_INT16",
    "SV_INIT_FLAG_AUDIO_FLOAT32",
    "SV_INIT_FLAG_ONE_THREAD",
    # Constants - Time map flags
    "SV_TIME_MAP_SPEED",
    "SV_TIME_MAP_FRAMECNT",
    # Constants - Module flags
    "SV_MODULE_FLAG_EXISTS",
    "SV_MODULE_FLAG_GENERATOR",
    "SV_MODULE_FLAG_EFFECT",
    "SV_MODULE_FLAG_MUTE",
    "SV_MODULE_FLAG_SOLO",
    "SV_MODULE_FLAG_BYPASS",
    "SV_MODULE_INPUTS_OFF",
    "SV_MODULE_INPUTS_MASK",
    "SV_MODULE_OUTPUTS_OFF",
    "SV_MODULE_OUTPUTS_MASK",
]

__version__ = "0.1.1"

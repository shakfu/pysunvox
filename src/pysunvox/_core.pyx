# cython: language_level=3
"""
pysunvox low-level Cython wrapper for the SunVox library.

This module provides direct 1:1 wrappers of the sv_* C functions.
"""

from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from libc.stdint cimport int16_t
from cpython.bytes cimport PyBytes_AsString

cimport pysunvox._sunvox as sv


# Re-export constants
NOTECMD_NOTE_OFF = sv.NOTECMD_NOTE_OFF
NOTECMD_ALL_NOTES_OFF = sv.NOTECMD_ALL_NOTES_OFF
NOTECMD_CLEAN_SYNTHS = sv.NOTECMD_CLEAN_SYNTHS
NOTECMD_STOP = sv.NOTECMD_STOP
NOTECMD_PLAY = sv.NOTECMD_PLAY
NOTECMD_SET_PITCH = sv.NOTECMD_SET_PITCH
NOTECMD_CLEAN_MODULE = sv.NOTECMD_CLEAN_MODULE

SV_INIT_FLAG_NO_DEBUG_OUTPUT = sv.SV_INIT_FLAG_NO_DEBUG_OUTPUT
SV_INIT_FLAG_USER_AUDIO_CALLBACK = sv.SV_INIT_FLAG_USER_AUDIO_CALLBACK
SV_INIT_FLAG_OFFLINE = sv.SV_INIT_FLAG_OFFLINE
SV_INIT_FLAG_AUDIO_INT16 = sv.SV_INIT_FLAG_AUDIO_INT16
SV_INIT_FLAG_AUDIO_FLOAT32 = sv.SV_INIT_FLAG_AUDIO_FLOAT32
SV_INIT_FLAG_ONE_THREAD = sv.SV_INIT_FLAG_ONE_THREAD

SV_TIME_MAP_SPEED = sv.SV_TIME_MAP_SPEED
SV_TIME_MAP_FRAMECNT = sv.SV_TIME_MAP_FRAMECNT

SV_MODULE_FLAG_EXISTS = sv.SV_MODULE_FLAG_EXISTS
SV_MODULE_FLAG_GENERATOR = sv.SV_MODULE_FLAG_GENERATOR
SV_MODULE_FLAG_EFFECT = sv.SV_MODULE_FLAG_EFFECT
SV_MODULE_FLAG_MUTE = sv.SV_MODULE_FLAG_MUTE
SV_MODULE_FLAG_SOLO = sv.SV_MODULE_FLAG_SOLO
SV_MODULE_FLAG_BYPASS = sv.SV_MODULE_FLAG_BYPASS
SV_MODULE_INPUTS_OFF = sv.SV_MODULE_INPUTS_OFF
SV_MODULE_INPUTS_MASK = sv.SV_MODULE_INPUTS_MASK
SV_MODULE_OUTPUTS_OFF = sv.SV_MODULE_OUTPUTS_OFF
SV_MODULE_OUTPUTS_MASK = sv.SV_MODULE_OUTPUTS_MASK


cdef class Note:
    """Wrapper for the sunvox_note structure."""
    cdef sv.sunvox_note _note

    def __cinit__(self, int note=0, int vel=0, int module=0, int ctl=0, int ctl_val=0):
        self._note.note = note
        self._note.vel = vel
        self._note.module = module
        self._note.ctl = ctl
        self._note.ctl_val = ctl_val

    @property
    def note(self):
        return self._note.note

    @note.setter
    def note(self, int value):
        self._note.note = value

    @property
    def vel(self):
        return self._note.vel

    @vel.setter
    def vel(self, int value):
        self._note.vel = value

    @property
    def module(self):
        return self._note.module

    @module.setter
    def module(self, int value):
        self._note.module = value

    @property
    def ctl(self):
        return self._note.ctl

    @ctl.setter
    def ctl(self, int value):
        self._note.ctl = value

    @property
    def ctl_val(self):
        return self._note.ctl_val

    @ctl_val.setter
    def ctl_val(self, int value):
        self._note.ctl_val = value

    def __repr__(self):
        return f"Note(note={self.note}, vel={self.vel}, module={self.module}, ctl={self.ctl}, ctl_val={self.ctl_val})"


# ============================================================================
# Init/deinit functions
# ============================================================================

cpdef int init(str config=None, int freq=44100, int channels=2, unsigned int flags=0):
    """Initialize the SunVox engine.

    Args:
        config: Configuration string (e.g., "buffer=1024|audiodriver=alsa").
        freq: Desired sample rate in Hz (minimum 44100).
        channels: Number of channels (only 2 supported).
        flags: Combination of SV_INIT_FLAG_* constants.

    Returns:
        Version number on success, negative value on error.
    """
    cdef const char* c_config = NULL
    cdef bytes config_bytes
    if config is not None:
        config_bytes = config.encode('utf-8')
        c_config = config_bytes
    return sv.sv_init(c_config, freq, channels, flags)


cpdef int deinit():
    """Deinitialize the SunVox engine.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_deinit()


cpdef int get_sample_rate():
    """Get the current sampling rate.

    Returns:
        Current sample rate in Hz.
    """
    return sv.sv_get_sample_rate()


cpdef int update_input():
    """Handle input ON/OFF requests for sound card input ports.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_update_input()


# ============================================================================
# Audio callback functions
# ============================================================================

cpdef int audio_callback(buffer, int frames, int latency, unsigned int out_time):
    """Get the next piece of SunVox audio from the Output module.

    Args:
        buffer: Destination buffer (must be writable bytes-like object).
        frames: Number of frames in the buffer.
        latency: Audio latency in frames.
        out_time: Buffer output time in system ticks.

    Returns:
        0 if silence (buffer filled with zeros), 1 if audio was produced.
    """
    cdef char[:] buf_view = buffer
    return sv.sv_audio_callback(<void*>&buf_view[0], frames, latency, out_time)


cpdef int audio_callback2(out_buffer, int frames, int latency, unsigned int out_time,
                          int in_type, int in_channels, in_buffer):
    """Get audio from Output module while sending data to Input module.

    Args:
        out_buffer: Output buffer (writable bytes-like object).
        frames: Number of frames.
        latency: Audio latency in frames.
        out_time: Buffer output time in system ticks.
        in_type: Input buffer type (0=int16, 1=float).
        in_channels: Number of input channels.
        in_buffer: Input buffer (bytes-like object).

    Returns:
        0 if silence, 1 if audio was produced.
    """
    cdef char[:] out_view = out_buffer
    cdef char[:] in_view = in_buffer
    return sv.sv_audio_callback2(<void*>&out_view[0], frames, latency, out_time,
                                  in_type, in_channels, <void*>&in_view[0])


# ============================================================================
# Slot management
# ============================================================================

cpdef int open_slot(int slot):
    """Open a sound slot for SunVox.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_open_slot(slot)


cpdef int close_slot(int slot):
    """Close a sound slot.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_close_slot(slot)


cpdef int lock_slot(int slot):
    """Lock a slot for thread-safe access.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_lock_slot(slot)


cpdef int unlock_slot(int slot):
    """Unlock a slot after thread-safe access.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_unlock_slot(slot)


# ============================================================================
# Project I/O
# ============================================================================

cpdef int load(int slot, str filename):
    """Load a SunVox project from a file.

    Args:
        slot: Slot number.
        filename: Path to the .sunvox file.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_load(slot, filename_bytes)


cpdef int load_from_memory(int slot, bytes data):
    """Load a SunVox project from memory.

    Args:
        slot: Slot number.
        data: Project data as bytes.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_load_from_memory(slot, <void*>PyBytes_AsString(data), len(data))


cpdef int save(int slot, str filename):
    """Save a SunVox project to a file.

    Args:
        slot: Slot number.
        filename: Path to save the .sunvox file.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_save(slot, filename_bytes)


cpdef bytes save_to_memory(int slot):
    """Save a SunVox project to memory.

    Args:
        slot: Slot number.

    Returns:
        Project data as bytes, or None on error.
    """
    cdef size_t size = 0
    cdef void* data = sv.sv_save_to_memory(slot, &size)
    if data == NULL or size == 0:
        return None
    cdef bytes result = (<char*>data)[:size]
    free(data)
    return result


# ============================================================================
# Playback control
# ============================================================================

cpdef int play(int slot):
    """Play from the current position.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_play(slot)


cpdef int play_from_beginning(int slot):
    """Play from the beginning (line 0).

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_play_from_beginning(slot)


cpdef int stop(int slot):
    """Stop playing.

    First call stops playback; second call resets all activity to standby mode.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_stop(slot)


cpdef int pause(int slot):
    """Pause the audio stream.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_pause(slot)


cpdef int resume(int slot):
    """Resume the audio stream.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_resume(slot)


cpdef int sync_resume(int slot):
    """Wait for sync and resume the audio stream.

    Args:
        slot: Slot number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_sync_resume(slot)


# ============================================================================
# Autostop control
# ============================================================================

cpdef int set_autostop(int slot, int autostop):
    """Set autostop mode.

    Args:
        slot: Slot number.
        autostop: 0 to disable (loop forever), 1 to enable.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_autostop(slot, autostop)


cpdef int get_autostop(int slot):
    """Get autostop mode.

    Args:
        slot: Slot number.

    Returns:
        0 if disabled, 1 if enabled, negative on error.
    """
    return sv.sv_get_autostop(slot)


# ============================================================================
# Song status
# ============================================================================

cpdef int end_of_song(int slot):
    """Check if the song has ended.

    Args:
        slot: Slot number.

    Returns:
        0 if playing, 1 if stopped.
    """
    return sv.sv_end_of_song(slot)


cpdef int rewind(int slot, int line_num):
    """Rewind to a specific line.

    Args:
        slot: Slot number.
        line_num: Line number to rewind to.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_rewind(slot, line_num)


cpdef int volume(int slot, int vol):
    """Set the volume.

    Args:
        slot: Slot number.
        vol: Volume from 0 (min) to 256 (max 100%). Negative values are ignored.

    Returns:
        Previous volume value.
    """
    return sv.sv_volume(slot, vol)


# ============================================================================
# Events
# ============================================================================

cpdef int set_event_t(int slot, int set, int t):
    """Set the timestamp for events sent by send_event().

    Args:
        slot: Slot number.
        set: 1 to set timestamp, 0 to reset (use automatic time).
        t: Timestamp in system ticks.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_event_t(slot, set, t)


cpdef int send_event(int slot, int track_num, int note, int vel,
                     int module, int ctl, int ctl_val):
    """Send an event (note ON, note OFF, controller change, etc.).

    Args:
        slot: Slot number.
        track_num: Track number within the pattern.
        note: 0=nothing, 1-127=note, 128=note off, 129+=NOTECMD_*.
        vel: Velocity 1-129, 0=default.
        module: 0=empty, 1-65535=module number + 1.
        ctl: 0xCCEE where CC=controller number + 1, EE=effect.
        ctl_val: Controller value or effect parameter.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_send_event(slot, track_num, note, vel, module, ctl, ctl_val)


# ============================================================================
# Current position/state
# ============================================================================

cpdef int get_current_line(int slot):
    """Get the current line number.

    Args:
        slot: Slot number.

    Returns:
        Current line number.
    """
    return sv.sv_get_current_line(slot)


cpdef int get_current_line2(int slot):
    """Get the current line number in fixed point format 27.5.

    Args:
        slot: Slot number.

    Returns:
        Current line number in 27.5 fixed point format.
    """
    return sv.sv_get_current_line2(slot)


cpdef int get_current_signal_level(int slot, int channel):
    """Get the current signal level.

    Args:
        slot: Slot number.
        channel: Channel number.

    Returns:
        Signal level from 0 to 255.
    """
    return sv.sv_get_current_signal_level(slot, channel)


# ============================================================================
# Song properties
# ============================================================================

cpdef str get_song_name(int slot):
    """Get the song name.

    Args:
        slot: Slot number.

    Returns:
        Song name as string.
    """
    cdef const char* name = sv.sv_get_song_name(slot)
    if name == NULL:
        return ""
    return name.decode('utf-8')


cpdef int set_song_name(int slot, str name):
    """Set the song name.

    Args:
        slot: Slot number.
        name: New song name.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_set_song_name(slot, name_bytes)


cpdef int get_base_version(int slot):
    """Get the SunVox base version the project was created with.

    Args:
        slot: Slot number.

    Returns:
        Base version number.
    """
    return sv.sv_get_base_version(slot)


cpdef int get_song_bpm(int slot):
    """Get the song BPM.

    Args:
        slot: Slot number.

    Returns:
        Beats per minute.
    """
    return sv.sv_get_song_bpm(slot)


cpdef int get_song_tpl(int slot):
    """Get the song TPL (ticks per line).

    Args:
        slot: Slot number.

    Returns:
        Ticks per line.
    """
    return sv.sv_get_song_tpl(slot)


cpdef unsigned int get_song_length_frames(int slot):
    """Get the song length in frames.

    Args:
        slot: Slot number.

    Returns:
        Length in frames.
    """
    return sv.sv_get_song_length_frames(slot)


cpdef unsigned int get_song_length_lines(int slot):
    """Get the song length in lines.

    Args:
        slot: Slot number.

    Returns:
        Length in lines.
    """
    return sv.sv_get_song_length_lines(slot)


cpdef int get_time_map(int slot, int start_line, int length, unsigned int[:] dest, int flags):
    """Get the time map.

    Args:
        slot: Slot number.
        start_line: First line to read (usually 0).
        length: Number of lines to read.
        dest: Destination array (uint32 memoryview).
        flags: SV_TIME_MAP_SPEED or SV_TIME_MAP_FRAMECNT.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_get_time_map(slot, start_line, length, &dest[0], flags)


# ============================================================================
# Module operations
# ============================================================================

cpdef int new_module(int slot, str module_type, str name, int x, int y, int z):
    """Create a new module. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        module_type: Module type (e.g., "Generator", "Sampler").
        name: Module name.
        x, y, z: Module position coordinates.

    Returns:
        New module number, or negative value on error.
    """
    cdef bytes type_bytes = module_type.encode('utf-8')
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_new_module(slot, type_bytes, name_bytes, x, y, z)


cpdef int remove_module(int slot, int mod_num):
    """Remove a module. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_remove_module(slot, mod_num)


cpdef int connect_module(int slot, int source, int destination):
    """Connect two modules. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        source: Source module number.
        destination: Destination module number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_connect_module(slot, source, destination)


cpdef int disconnect_module(int slot, int source, int destination):
    """Disconnect two modules. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        source: Source module number.
        destination: Destination module number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_disconnect_module(slot, source, destination)


cpdef int load_module(int slot, str filename, int x, int y, int z):
    """Load a module from file.

    Args:
        slot: Slot number.
        filename: Path to file (sunsynth, xi, wav, aiff, ogg, mp3, flac).
        x, y, z: Module position coordinates.

    Returns:
        New module number, or negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_load_module(slot, filename_bytes, x, y, z)


cpdef int load_module_from_memory(int slot, bytes data, int x, int y, int z):
    """Load a module from memory.

    Args:
        slot: Slot number.
        data: Module data as bytes.
        x, y, z: Module position coordinates.

    Returns:
        New module number, or negative value on error.
    """
    return sv.sv_load_module_from_memory(slot, <void*>PyBytes_AsString(data),
                                          len(data), x, y, z)


# ============================================================================
# Sampler operations
# ============================================================================

cpdef int sampler_load(int slot, int mod_num, str filename, int sample_slot):
    """Load a sample into a Sampler module.

    Args:
        slot: Slot number.
        mod_num: Sampler module number.
        filename: Path to sample file.
        sample_slot: Sample slot (-1 to replace whole sampler).

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_sampler_load(slot, mod_num, filename_bytes, sample_slot)


cpdef int sampler_load_from_memory(int slot, int mod_num, bytes data, int sample_slot):
    """Load a sample into a Sampler module from memory.

    Args:
        slot: Slot number.
        mod_num: Sampler module number.
        data: Sample data as bytes.
        sample_slot: Sample slot (-1 to replace whole sampler).

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_sampler_load_from_memory(slot, mod_num, <void*>PyBytes_AsString(data),
                                           len(data), sample_slot)


cpdef int sampler_par(int slot, int mod_num, int sample_slot, int par, int par_val, int set):
    """Get/set sampler parameter.

    Args:
        slot: Slot number.
        mod_num: Sampler module number.
        sample_slot: Sample slot.
        par: Parameter number (0-8, see sunvox.h for details).
        par_val: Parameter value (for set).
        set: 0 to get, 1 to set.

    Returns:
        Parameter value or error code.
    """
    return sv.sv_sampler_par(slot, mod_num, sample_slot, par, par_val, set)


# ============================================================================
# MetaModule/Vorbis player
# ============================================================================

cpdef int metamodule_load(int slot, int mod_num, str filename):
    """Load a file into a MetaModule.

    Args:
        slot: Slot number.
        mod_num: MetaModule number.
        filename: Path to file (sunvox, mod, xm, midi).

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_metamodule_load(slot, mod_num, filename_bytes)


cpdef int metamodule_load_from_memory(int slot, int mod_num, bytes data):
    """Load a file into a MetaModule from memory.

    Args:
        slot: Slot number.
        mod_num: MetaModule number.
        data: File data as bytes.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_metamodule_load_from_memory(slot, mod_num,
                                              <void*>PyBytes_AsString(data), len(data))


cpdef int vplayer_load(int slot, int mod_num, str filename):
    """Load a file into a Vorbis Player.

    Args:
        slot: Slot number.
        mod_num: Vorbis Player module number.
        filename: Path to .ogg file.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes filename_bytes = filename.encode('utf-8')
    return sv.sv_vplayer_load(slot, mod_num, filename_bytes)


cpdef int vplayer_load_from_memory(int slot, int mod_num, bytes data):
    """Load a file into a Vorbis Player from memory.

    Args:
        slot: Slot number.
        mod_num: Vorbis Player module number.
        data: .ogg file data as bytes.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_vplayer_load_from_memory(slot, mod_num,
                                           <void*>PyBytes_AsString(data), len(data))


# ============================================================================
# Module queries
# ============================================================================

cpdef int get_number_of_modules(int slot):
    """Get the number of module slots.

    Args:
        slot: Slot number.

    Returns:
        Number of module slots (some may be empty).
    """
    return sv.sv_get_number_of_modules(slot)


cpdef int find_module(int slot, str name):
    """Find a module by name.

    Args:
        slot: Slot number.
        name: Module name.

    Returns:
        Module number, or -1 if not found.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_find_module(slot, name_bytes)


cpdef unsigned int get_module_flags(int slot, int mod_num):
    """Get module flags.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Flags (see SV_MODULE_FLAG_* constants).
    """
    return sv.sv_get_module_flags(slot, mod_num)


cpdef list get_module_inputs(int slot, int mod_num):
    """Get module input connections.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        List of input module numbers (-1 for empty links).
    """
    cdef unsigned int flags = sv.sv_get_module_flags(slot, mod_num)
    cdef int num_inputs = (flags & sv.SV_MODULE_INPUTS_MASK) >> sv.SV_MODULE_INPUTS_OFF
    cdef int* inputs = sv.sv_get_module_inputs(slot, mod_num)
    if inputs == NULL:
        return []
    return [inputs[i] for i in range(num_inputs)]


cpdef list get_module_outputs(int slot, int mod_num):
    """Get module output connections.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        List of output module numbers (-1 for empty links).
    """
    cdef unsigned int flags = sv.sv_get_module_flags(slot, mod_num)
    cdef int num_outputs = (flags & sv.SV_MODULE_OUTPUTS_MASK) >> sv.SV_MODULE_OUTPUTS_OFF
    cdef int* outputs = sv.sv_get_module_outputs(slot, mod_num)
    if outputs == NULL:
        return []
    return [outputs[i] for i in range(num_outputs)]


cpdef str get_module_type(int slot, int mod_num):
    """Get module type name.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Module type as string.
    """
    cdef const char* type_name = sv.sv_get_module_type(slot, mod_num)
    if type_name == NULL:
        return ""
    return type_name.decode('utf-8')


cpdef str get_module_name(int slot, int mod_num):
    """Get module name.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Module name as string.
    """
    cdef const char* name = sv.sv_get_module_name(slot, mod_num)
    if name == NULL:
        return ""
    return name.decode('utf-8')


cpdef int set_module_name(int slot, int mod_num, str name):
    """Set module name.

    Args:
        slot: Slot number.
        mod_num: Module number.
        name: New module name.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_set_module_name(slot, mod_num, name_bytes)


cpdef tuple get_module_xy(int slot, int mod_num):
    """Get module XY coordinates.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Tuple of (x, y) coordinates.
    """
    cdef unsigned int xy = sv.sv_get_module_xy(slot, mod_num)
    cdef int x = xy & 0xFFFF
    cdef int y = (xy >> 16) & 0xFFFF
    if x & 0x8000:
        x -= 0x10000
    if y & 0x8000:
        y -= 0x10000
    return (x, y)


cpdef int set_module_xy(int slot, int mod_num, int x, int y):
    """Set module XY coordinates.

    Args:
        slot: Slot number.
        mod_num: Module number.
        x, y: New coordinates.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_module_xy(slot, mod_num, x, y)


cpdef int get_module_color(int slot, int mod_num):
    """Get module color.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Color in 0xBBGGRR format.
    """
    return sv.sv_get_module_color(slot, mod_num)


cpdef int set_module_color(int slot, int mod_num, int color):
    """Set module color.

    Args:
        slot: Slot number.
        mod_num: Module number.
        color: Color in 0xBBGGRR format.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_module_color(slot, mod_num, color)


cpdef tuple get_module_finetune(int slot, int mod_num):
    """Get module finetune and relative note.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Tuple of (finetune, relative_note).
    """
    cdef unsigned int ft = sv.sv_get_module_finetune(slot, mod_num)
    cdef int finetune = ft & 0xFFFF
    cdef int relative_note = (ft >> 16) & 0xFFFF
    if finetune & 0x8000:
        finetune -= 0x10000
    if relative_note & 0x8000:
        relative_note -= 0x10000
    return (finetune, relative_note)


cpdef int set_module_finetune(int slot, int mod_num, int finetune):
    """Set module finetune.

    Args:
        slot: Slot number.
        mod_num: Module number.
        finetune: Finetune value.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_module_finetune(slot, mod_num, finetune)


cpdef int set_module_relnote(int slot, int mod_num, int relative_note):
    """Set module relative note.

    Args:
        slot: Slot number.
        mod_num: Module number.
        relative_note: Relative note value.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_module_relnote(slot, mod_num, relative_note)


cpdef unsigned int get_module_scope2(int slot, int mod_num, int channel, int16_t[:] dest):
    """Get module scope data.

    Args:
        slot: Slot number.
        mod_num: Module number.
        channel: Channel number.
        dest: Destination buffer (int16 memoryview).

    Returns:
        Number of samples actually read.
    """
    return sv.sv_get_module_scope2(slot, mod_num, channel, &dest[0], len(dest))


cpdef int module_curve(int slot, int mod_num, int curve_num, float[:] data, int w):
    """Read or write module curve data.

    Args:
        slot: Slot number.
        mod_num: Module number.
        curve_num: Curve number.
        data: Data buffer (float memoryview).
        w: 0 to read, 1 to write.

    Returns:
        Number of items processed.
    """
    return sv.sv_module_curve(slot, mod_num, curve_num, &data[0], len(data), w)


# ============================================================================
# Module controllers
# ============================================================================

cpdef int get_number_of_module_ctls(int slot, int mod_num):
    """Get number of module controllers.

    Args:
        slot: Slot number.
        mod_num: Module number.

    Returns:
        Number of controllers.
    """
    return sv.sv_get_number_of_module_ctls(slot, mod_num)


cpdef str get_module_ctl_name(int slot, int mod_num, int ctl_num):
    """Get controller name.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.

    Returns:
        Controller name as string.
    """
    cdef const char* name = sv.sv_get_module_ctl_name(slot, mod_num, ctl_num)
    if name == NULL:
        return ""
    return name.decode('utf-8')


cpdef int get_module_ctl_value(int slot, int mod_num, int ctl_num, int scaled):
    """Get controller value.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.
        scaled: 0=real, 1=scaled, 2=displayed value.

    Returns:
        Controller value.
    """
    return sv.sv_get_module_ctl_value(slot, mod_num, ctl_num, scaled)


cpdef int set_module_ctl_value(int slot, int mod_num, int ctl_num, int val, int scaled):
    """Set controller value.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.
        val: New value.
        scaled: 0=real, 1=scaled.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_module_ctl_value(slot, mod_num, ctl_num, val, scaled)


cpdef int get_module_ctl_min(int slot, int mod_num, int ctl_num, int scaled):
    """Get controller minimum value.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.
        scaled: 0=real, 1=scaled.

    Returns:
        Minimum value.
    """
    return sv.sv_get_module_ctl_min(slot, mod_num, ctl_num, scaled)


cpdef int get_module_ctl_max(int slot, int mod_num, int ctl_num, int scaled):
    """Get controller maximum value.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.
        scaled: 0=real, 1=scaled.

    Returns:
        Maximum value.
    """
    return sv.sv_get_module_ctl_max(slot, mod_num, ctl_num, scaled)


cpdef int get_module_ctl_offset(int slot, int mod_num, int ctl_num):
    """Get controller display offset.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.

    Returns:
        Display offset.
    """
    return sv.sv_get_module_ctl_offset(slot, mod_num, ctl_num)


cpdef int get_module_ctl_type(int slot, int mod_num, int ctl_num):
    """Get controller type.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.

    Returns:
        0=normal (scaled), 1=selector (enum).
    """
    return sv.sv_get_module_ctl_type(slot, mod_num, ctl_num)


cpdef int get_module_ctl_group(int slot, int mod_num, int ctl_num):
    """Get controller group.

    Args:
        slot: Slot number.
        mod_num: Module number.
        ctl_num: Controller number.

    Returns:
        Group number.
    """
    return sv.sv_get_module_ctl_group(slot, mod_num, ctl_num)


# ============================================================================
# Pattern operations
# ============================================================================

cpdef int new_pattern(int slot, int clone, int x, int y, int tracks, int lines,
                      int icon_seed, str name):
    """Create a new pattern. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        clone: Pattern to clone (-1 for new empty pattern).
        x, y: Pattern position on timeline.
        tracks: Number of tracks.
        lines: Number of lines.
        icon_seed: Icon seed.
        name: Pattern name.

    Returns:
        New pattern number, or negative value on error.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_new_pattern(slot, clone, x, y, tracks, lines, icon_seed, name_bytes)


cpdef int remove_pattern(int slot, int pat_num):
    """Remove a pattern. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_remove_pattern(slot, pat_num)


cpdef int get_number_of_patterns(int slot):
    """Get the number of pattern slots.

    Args:
        slot: Slot number.

    Returns:
        Number of pattern slots (some may be empty).
    """
    return sv.sv_get_number_of_patterns(slot)


cpdef int find_pattern(int slot, str name):
    """Find a pattern by name.

    Args:
        slot: Slot number.
        name: Pattern name.

    Returns:
        Pattern number, or -1 if not found.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_find_pattern(slot, name_bytes)


cpdef int get_pattern_x(int slot, int pat_num):
    """Get pattern X position (line number on timeline).

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        X position.
    """
    return sv.sv_get_pattern_x(slot, pat_num)


cpdef int get_pattern_y(int slot, int pat_num):
    """Get pattern Y position (vertical position on timeline).

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        Y position.
    """
    return sv.sv_get_pattern_y(slot, pat_num)


cpdef int set_pattern_xy(int slot, int pat_num, int x, int y):
    """Set pattern position. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        x, y: New position.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_pattern_xy(slot, pat_num, x, y)


cpdef int get_pattern_tracks(int slot, int pat_num):
    """Get number of pattern tracks.

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        Number of tracks.
    """
    return sv.sv_get_pattern_tracks(slot, pat_num)


cpdef int get_pattern_lines(int slot, int pat_num):
    """Get number of pattern lines.

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        Number of lines.
    """
    return sv.sv_get_pattern_lines(slot, pat_num)


cpdef int set_pattern_size(int slot, int pat_num, int tracks, int lines):
    """Set pattern size. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        tracks: Number of tracks.
        lines: Number of lines.

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_pattern_size(slot, pat_num, tracks, lines)


cpdef str get_pattern_name(int slot, int pat_num):
    """Get pattern name.

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        Pattern name as string.
    """
    cdef const char* name = sv.sv_get_pattern_name(slot, pat_num)
    if name == NULL:
        return ""
    return name.decode('utf-8')


cpdef int set_pattern_name(int slot, int pat_num, str name):
    """Set pattern name. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        name: New pattern name.

    Returns:
        0 on success, negative value on error.
    """
    cdef bytes name_bytes = name.encode('utf-8')
    return sv.sv_set_pattern_name(slot, pat_num, name_bytes)


cpdef int set_pattern_event(int slot, int pat_num, int track, int line,
                            int nn, int vv, int mm, int ccee, int xxyy):
    """Set a pattern event.

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        track: Track number.
        line: Line number.
        nn: Note (negative values are ignored).
        vv: Velocity (negative values are ignored).
        mm: Module (negative values are ignored).
        ccee: Controller/effect (negative values are ignored).
        xxyy: Controller value/effect parameter (negative values are ignored).

    Returns:
        0 on success, negative value on error.
    """
    return sv.sv_set_pattern_event(slot, pat_num, track, line, nn, vv, mm, ccee, xxyy)


cpdef int get_pattern_event(int slot, int pat_num, int track, int line, int column):
    """Get a pattern event field.

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        track: Track number.
        line: Line number.
        column: Field (0=note, 1=vel, 2=module, 3=ctl, 4=ctl_val).

    Returns:
        Field value, or negative error code.
    """
    return sv.sv_get_pattern_event(slot, pat_num, track, line, column)


def get_pattern_data(int slot, int pat_num):
    """Get pattern data buffer for direct read/write access.

    Returns a memoryview of the pattern data containing sunvox_note structures
    in row-major order (line 0 track 0, line 0 track 1, ..., line 1 track 0, ...).

    Each note is 8 bytes: [note:u8, vel:u8, module:u16, ctl:u16, ctl_val:u16]

    Args:
        slot: Slot number.
        pat_num: Pattern number.

    Returns:
        Memoryview of pattern data (tracks * lines * 8 bytes), or None if pattern
        doesn't exist.

    Example:
        data = get_pattern_data(0, 0)
        tracks = get_pattern_tracks(0, 0)
        # Access note at line 5, track 2:
        offset = (5 * tracks + 2) * 8
        note_byte = data[offset]  # note value
    """
    cdef sv.sunvox_note* data = sv.sv_get_pattern_data(slot, pat_num)
    if data == NULL:
        return None
    cdef int tracks = sv.sv_get_pattern_tracks(slot, pat_num)
    cdef int lines = sv.sv_get_pattern_lines(slot, pat_num)
    if tracks <= 0 or lines <= 0:
        return None
    cdef Py_ssize_t size = tracks * lines * sizeof(sv.sunvox_note)
    return (<char*>data)[:size]


cpdef int pattern_mute(int slot, int pat_num, int mute):
    """Mute/unmute a pattern. USE LOCK/UNLOCK!

    Args:
        slot: Slot number.
        pat_num: Pattern number.
        mute: 1 to mute, 0 to unmute, negative to ignore.

    Returns:
        Previous state (1=muted, 0=unmuted), or -1 on error.
    """
    return sv.sv_pattern_mute(slot, pat_num, mute)


# ============================================================================
# System ticks
# ============================================================================

cpdef unsigned int get_ticks():
    """Get current tick counter.

    Returns:
        Current tick counter (0 to 0xFFFFFFFF).
    """
    return sv.sv_get_ticks()


cpdef unsigned int get_ticks_per_second():
    """Get number of ticks per second.

    Returns:
        Ticks per second.
    """
    return sv.sv_get_ticks_per_second()


# ============================================================================
# Logging
# ============================================================================

cpdef str get_log(int size):
    """Get the latest messages from the log.

    Args:
        size: Max number of bytes to read.

    Returns:
        Log messages as string.
    """
    cdef const char* log = sv.sv_get_log(size)
    if log == NULL:
        return ""
    return log.decode('utf-8')

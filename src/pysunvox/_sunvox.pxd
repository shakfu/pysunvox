# cython: language_level=3
"""
Cython declaration file for the SunVox library.

This file declares the C structures, constants, and functions from sunvox.h.
"""

from libc.stdint cimport uint8_t, uint16_t, uint32_t, int16_t


# Constants
cdef extern from "sunvox.h":
    # Note commands
    int NOTECMD_NOTE_OFF
    int NOTECMD_ALL_NOTES_OFF
    int NOTECMD_CLEAN_SYNTHS
    int NOTECMD_STOP
    int NOTECMD_PLAY
    int NOTECMD_SET_PITCH
    int NOTECMD_CLEAN_MODULE

    # Init flags
    unsigned int SV_INIT_FLAG_NO_DEBUG_OUTPUT
    unsigned int SV_INIT_FLAG_USER_AUDIO_CALLBACK
    unsigned int SV_INIT_FLAG_OFFLINE
    unsigned int SV_INIT_FLAG_AUDIO_INT16
    unsigned int SV_INIT_FLAG_AUDIO_FLOAT32
    unsigned int SV_INIT_FLAG_ONE_THREAD

    # Time map flags
    int SV_TIME_MAP_SPEED
    int SV_TIME_MAP_FRAMECNT

    # Module flags
    unsigned int SV_MODULE_FLAG_EXISTS
    unsigned int SV_MODULE_FLAG_GENERATOR
    unsigned int SV_MODULE_FLAG_EFFECT
    unsigned int SV_MODULE_FLAG_MUTE
    unsigned int SV_MODULE_FLAG_SOLO
    unsigned int SV_MODULE_FLAG_BYPASS
    int SV_MODULE_INPUTS_OFF
    unsigned int SV_MODULE_INPUTS_MASK
    int SV_MODULE_OUTPUTS_OFF
    unsigned int SV_MODULE_OUTPUTS_MASK


# Structures
cdef extern from "sunvox.h":
    ctypedef struct sunvox_note:
        uint8_t note
        uint8_t vel
        uint16_t module
        uint16_t ctl
        uint16_t ctl_val


# Functions
cdef extern from "sunvox.h":
    # Init/deinit
    int sv_init(const char* config, int freq, int channels, uint32_t flags)
    int sv_deinit()
    int sv_get_sample_rate()
    int sv_update_input()

    # Audio callback
    int sv_audio_callback(void* buf, int frames, int latency, uint32_t out_time)
    int sv_audio_callback2(void* buf, int frames, int latency, uint32_t out_time,
                           int in_type, int in_channels, void* in_buf)

    # Slot management
    int sv_open_slot(int slot)
    int sv_close_slot(int slot)
    int sv_lock_slot(int slot)
    int sv_unlock_slot(int slot)

    # Project I/O
    int sv_load(int slot, const char* name)
    int sv_load_from_memory(int slot, void* data, uint32_t data_size)
    int sv_save(int slot, const char* name)
    void* sv_save_to_memory(int slot, size_t* size)

    # Playback control
    int sv_play(int slot)
    int sv_play_from_beginning(int slot)
    int sv_stop(int slot)
    int sv_pause(int slot)
    int sv_resume(int slot)
    int sv_sync_resume(int slot)

    # Autostop
    int sv_set_autostop(int slot, int autostop)
    int sv_get_autostop(int slot)

    # Song status
    int sv_end_of_song(int slot)
    int sv_rewind(int slot, int line_num)
    int sv_volume(int slot, int vol)

    # Events
    int sv_set_event_t(int slot, int set, int t)
    int sv_send_event(int slot, int track_num, int note, int vel,
                      int module, int ctl, int ctl_val)

    # Current position/state
    int sv_get_current_line(int slot)
    int sv_get_current_line2(int slot)
    int sv_get_current_signal_level(int slot, int channel)

    # Song properties
    const char* sv_get_song_name(int slot)
    int sv_set_song_name(int slot, const char* name)
    int sv_get_base_version(int slot)
    int sv_get_song_bpm(int slot)
    int sv_get_song_tpl(int slot)
    uint32_t sv_get_song_length_frames(int slot)
    uint32_t sv_get_song_length_lines(int slot)
    int sv_get_time_map(int slot, int start_line, int len, uint32_t* dest, int flags)

    # Module operations (USE LOCK/UNLOCK)
    int sv_new_module(int slot, const char* type, const char* name, int x, int y, int z)
    int sv_remove_module(int slot, int mod_num)
    int sv_connect_module(int slot, int source, int destination)
    int sv_disconnect_module(int slot, int source, int destination)

    # Module loading
    int sv_load_module(int slot, const char* file_name, int x, int y, int z)
    int sv_load_module_from_memory(int slot, void* data, uint32_t data_size, int x, int y, int z)

    # Sampler operations
    int sv_sampler_load(int slot, int mod_num, const char* file_name, int sample_slot)
    int sv_sampler_load_from_memory(int slot, int mod_num, void* data, uint32_t data_size, int sample_slot)
    int sv_sampler_par(int slot, int mod_num, int sample_slot, int par, int par_val, int set)

    # MetaModule/Vorbis player
    int sv_metamodule_load(int slot, int mod_num, const char* file_name)
    int sv_metamodule_load_from_memory(int slot, int mod_num, void* data, uint32_t data_size)
    int sv_vplayer_load(int slot, int mod_num, const char* file_name)
    int sv_vplayer_load_from_memory(int slot, int mod_num, void* data, uint32_t data_size)

    # Module queries
    int sv_get_number_of_modules(int slot)
    int sv_find_module(int slot, const char* name)
    uint32_t sv_get_module_flags(int slot, int mod_num)
    int* sv_get_module_inputs(int slot, int mod_num)
    int* sv_get_module_outputs(int slot, int mod_num)
    const char* sv_get_module_type(int slot, int mod_num)
    const char* sv_get_module_name(int slot, int mod_num)
    int sv_set_module_name(int slot, int mod_num, const char* name)
    uint32_t sv_get_module_xy(int slot, int mod_num)
    int sv_set_module_xy(int slot, int mod_num, int x, int y)
    int sv_get_module_color(int slot, int mod_num)
    int sv_set_module_color(int slot, int mod_num, int color)
    uint32_t sv_get_module_finetune(int slot, int mod_num)
    int sv_set_module_finetune(int slot, int mod_num, int finetune)
    int sv_set_module_relnote(int slot, int mod_num, int relative_note)

    # Module scope
    uint32_t sv_get_module_scope2(int slot, int mod_num, int channel,
                                   int16_t* dest_buf, uint32_t samples_to_read)

    # Module curves
    int sv_module_curve(int slot, int mod_num, int curve_num,
                        float* data, int len, int w)

    # Module controllers
    int sv_get_number_of_module_ctls(int slot, int mod_num)
    const char* sv_get_module_ctl_name(int slot, int mod_num, int ctl_num)
    int sv_get_module_ctl_value(int slot, int mod_num, int ctl_num, int scaled)
    int sv_set_module_ctl_value(int slot, int mod_num, int ctl_num, int val, int scaled)
    int sv_get_module_ctl_min(int slot, int mod_num, int ctl_num, int scaled)
    int sv_get_module_ctl_max(int slot, int mod_num, int ctl_num, int scaled)
    int sv_get_module_ctl_offset(int slot, int mod_num, int ctl_num)
    int sv_get_module_ctl_type(int slot, int mod_num, int ctl_num)
    int sv_get_module_ctl_group(int slot, int mod_num, int ctl_num)

    # Pattern operations (USE LOCK/UNLOCK)
    int sv_new_pattern(int slot, int clone, int x, int y, int tracks, int lines,
                       int icon_seed, const char* name)
    int sv_remove_pattern(int slot, int pat_num)

    # Pattern queries
    int sv_get_number_of_patterns(int slot)
    int sv_find_pattern(int slot, const char* name)
    int sv_get_pattern_x(int slot, int pat_num)
    int sv_get_pattern_y(int slot, int pat_num)
    int sv_set_pattern_xy(int slot, int pat_num, int x, int y)
    int sv_get_pattern_tracks(int slot, int pat_num)
    int sv_get_pattern_lines(int slot, int pat_num)
    int sv_set_pattern_size(int slot, int pat_num, int tracks, int lines)
    const char* sv_get_pattern_name(int slot, int pat_num)
    int sv_set_pattern_name(int slot, int pat_num, const char* name)

    # Pattern data
    sunvox_note* sv_get_pattern_data(int slot, int pat_num)
    int sv_set_pattern_event(int slot, int pat_num, int track, int line,
                             int nn, int vv, int mm, int ccee, int xxyy)
    int sv_get_pattern_event(int slot, int pat_num, int track, int line, int column)
    int sv_pattern_mute(int slot, int pat_num, int mute)

    # System ticks
    uint32_t sv_get_ticks()
    uint32_t sv_get_ticks_per_second()

    # Logging
    const char* sv_get_log(int size)



cdef extern from "stdint.h":
    ctypedef unsigned int uint8_t
    ctypedef unsigned int uint16_t
    ctypedef unsigned int uint32_t
    ctypedef signed int int16_t

cdef extern from *:
    """
    #include <dlfcn.h>
    #include <string.h>
    #define SUNVOX_MAIN
    #include <sunvox.h>
    """

cdef extern from "sunvox.h":

    cdef enum:
        NOTECMD_NOTE_OFF      = 128
        NOTECMD_ALL_NOTES_OFF
        NOTECMD_CLEAN_SYNTHS
        NOTECMD_STOP
        NOTECMD_PLAY
        NOTECMD_SET_PITCH

    ctypedef struct sunvox_note:
        uint8_t note
        uint8_t vel
        uint16_t module
        uint16_t ctl
        uint16_t ctl_val


    cdef int SV_INIT_FLAG_NO_DEBUG_OUTPUT = 1
    cdef int SV_INIT_FLAG_USER_AUDIO_CALLBACK = 2
    cdef int SV_INIT_FLAG_OFFLINE = 2
    cdef int SV_INIT_FLAG_AUDIO_INT16 = 4
    cdef int SV_INIT_FLAG_AUDIO_FLOAT32 = 8
    cdef int SV_INIT_FLAG_ONE_THREAD = 16

    cdef int SV_TIME_MAP_SPEED = 0
    cdef int SV_TIME_MAP_FRAMECNT = 1

    cdef int SV_MODULE_FLAG_EXISTS = 1
    cdef int SV_MODULE_FLAG_EFFECT = 2
    cdef int SV_MODULE_FLAG_MUTE = 4
    cdef int SV_MODULE_FLAG_SOLO = 8
    cdef int SV_MODULE_FLAG_BYPASS = 16
    cdef int SV_MODULE_INPUTS_OFF =  16
    cdef int SV_MODULE_INPUTS_MASK = 16711680
    cdef int SV_MODULE_OUTPUTS_OFF = 24
    cdef int SV_MODULE_OUTPUTS_MASK = 16711680

    cdef int sv_init(char* config, int freq, int channels, uint32_t flags) 
    cdef int sv_deinit()
    cdef int sv_get_sample_rate()
    cdef int sv_update_input()
    cdef int sv_audio_callback(void* buf, int frames, int latency, uint32_t out_time)

    cdef int sv_audio_callback2(void* buf, int frames, int latency, uint32_t out_time, int in_type, int in_channels, void* in_buf)
    cdef int sv_open_slot(int slot)
    cdef int sv_close_slot(int slot)
    cdef int sv_lock_slot(int slot)
    cdef int sv_unlock_slot(int slot)
    cdef int sv_load(int slot, char* name)
    cdef int sv_load_from_memory(int slot, void* data, uint32_t data_size)
    cdef int sv_play(int slot)
    cdef int sv_play_from_beginning(int slot)
    cdef int sv_stop(int slot)
    cdef int sv_pause(int slot)
    cdef int sv_resume(int slot)
    cdef int sv_set_autostop(int slot, int autostop)
    cdef int sv_get_autostop(int slot)
    cdef int sv_end_of_song(int slot)
    cdef int sv_rewind(int slot, int line_num)
    cdef int sv_volume(int slot, int vol)
    cdef int sv_set_event_t(int slot, int set, int t)
    cdef int sv_send_event(int slot, int track_num, int note, int vel, int module, int ctl, int ctl_val)
    cdef int sv_get_current_line(int slot)
    cdef int sv_get_current_line2(int slot)
    cdef int sv_get_current_signal_level(int slot, int channel)
    cdef char* sv_get_song_name(int slot)
    cdef int sv_get_song_bpm(int slot)
    cdef int sv_get_song_tpl(int slot)
    cdef uint32_t sv_get_song_length_frames(int slot)
    cdef uint32_t sv_get_song_length_lines(int slot)
    cdef int sv_get_time_map(int slot, int start_line, int len, uint32_t* dest, int flags)
    cdef int sv_new_module(int slot, char* type, char* name, int x, int y, int z)
    cdef int sv_remove_module(int slot, int mod_num)
    cdef int sv_connect_module(int slot, int source, int destination)
    cdef int sv_disconnect_module(int slot, int source, int destination)
    cdef int sv_load_module(int slot, char* file_name, int x, int y, int z)
    cdef int sv_load_module_from_memory(int slot, void* data, uint32_t data_size, int x, int y, int z)
    cdef int sv_sampler_load(int slot, int sampler_module, char* file_name, int sample_slot)
    cdef int sv_sampler_load_from_memory(int slot, int sampler_module, void* data, uint32_t data_size, int sample_slot)
    cdef int sv_get_number_of_modules(int slot)
    cdef int sv_find_module(int slot, char* name)
    cdef uint32_t sv_get_module_flags(int slot, int mod_num)
    cdef int* sv_get_module_inputs(int slot, int mod_num)
    cdef int* sv_get_module_outputs(int slot, int mod_num)
    cdef char* sv_get_module_name(int slot, int mod_num)
    cdef uint32_t sv_get_module_xy(int slot, int mod_num)
    cdef int sv_get_module_color(int slot, int mod_num)
    cdef uint32_t sv_get_module_finetune(int slot, int mod_num)
    cdef uint32_t sv_get_module_scope2(int slot, int mod_num, int channel, int16_t* dest_buf, uint32_t samples_to_read)
    cdef int sv_module_curve(int slot, int mod_num, int curve_num, float* data, int len, int w)
    cdef int sv_get_number_of_module_ctls(int slot, int mod_num)
    cdef char* sv_get_module_ctl_name(int slot, int mod_num, int ctl_num)
    cdef int sv_get_module_ctl_value(int slot, int mod_num, int ctl_num, int scaled)
    cdef int sv_get_number_of_patterns(int slot)
    cdef int sv_find_pattern(int slot, char* name)
    cdef int sv_get_pattern_x(int slot, int pat_num)
    cdef int sv_get_pattern_y(int slot, int pat_num)
    cdef int sv_get_pattern_tracks(int slot, int pat_num)
    cdef int sv_get_pattern_lines(int slot, int pat_num)
    cdef char* sv_get_pattern_name(int slot, int pat_num)
    cdef sunvox_note* sv_get_pattern_data(int slot, int pat_num)
    cdef int sv_pattern_mute(int slot, int pat_num, int mute)
    cdef uint32_t sv_get_ticks()
    cdef uint32_t sv_get_ticks_per_second()
    cdef char* sv_get_log(int size)
    ctypedef int (*tsv_audio_callback)(void* buf, int frames, int latency, uint32_t out_time)
    ctypedef int (*tsv_audio_callback2)(void* buf, int frames, int latency, uint32_t out_time, int in_type, int in_channels, void* in_buf)
    ctypedef int (*tsv_open_slot)(int slot)
    ctypedef int (*tsv_close_slot)(int slot)
    ctypedef int (*tsv_lock_slot)(int slot)
    ctypedef int (*tsv_unlock_slot)(int slot)
    ctypedef int (*tsv_init)(char* config, int freq, int channels, uint32_t flags)
    ctypedef int (*tsv_deinit)()
    ctypedef int (*tsv_get_sample_rate)()
    ctypedef int (*tsv_update_input)()
    ctypedef int (*tsv_load)(int slot, char* name)
    ctypedef int (*tsv_load_from_memory)(int slot, void* data, uint32_t data_size)
    ctypedef int (*tsv_play)(int slot)
    ctypedef int (*tsv_play_from_beginning)(int slot)
    ctypedef int (*tsv_stop)(int slot)
    ctypedef int (*tsv_pause)(int slot)
    ctypedef int (*tsv_resume)(int slot)
    ctypedef int (*tsv_set_autostop)(int slot, int autostop)
    ctypedef int (*tsv_get_autostop)(int slot)
    ctypedef int (*tsv_end_of_song)(int slot)
    ctypedef int (*tsv_rewind)(int slot, int t)
    ctypedef int (*tsv_volume)(int slot, int vol)
    ctypedef int (*tsv_set_event_t)(int slot, int set, int t)
    ctypedef int (*tsv_send_event)(int slot, int track_num, int note, int vel, int module, int ctl, int ctl_val)
    ctypedef int (*tsv_get_current_line)(int slot)
    ctypedef int (*tsv_get_current_line2)(int slot)
    ctypedef int (*tsv_get_current_signal_level)(int slot, int channel)
    ctypedef char* (*tsv_get_song_name)(int slot)
    ctypedef int (*tsv_get_song_bpm)(int slot)
    ctypedef int (*tsv_get_song_tpl)(int slot)
    ctypedef uint32_t (*tsv_get_song_length_frames)(int slot)
    ctypedef uint32_t (*tsv_get_song_length_lines)(int slot)
    ctypedef int (*tsv_get_time_map)(int slot, int start_line, int len, uint32_t* dest, int flags)
    ctypedef int (*tsv_new_module)(int slot, char* type, char* name, int x, int y, int z)
    ctypedef int (*tsv_remove_module)(int slot, int mod_num)
    ctypedef int (*tsv_connect_module)(int slot, int source, int destination)
    ctypedef int (*tsv_disconnect_module)(int slot, int source, int destination)
    ctypedef int (*tsv_load_module)(int slot, char* file_name, int x, int y, int z)
    ctypedef int (*tsv_load_module_from_memory)(int slot, void* data, uint32_t data_size, int x, int y, int z)
    ctypedef int (*tsv_sampler_load)(int slot, int sampler_module, char* file_name, int sample_slot)
    ctypedef int (*tsv_sampler_load_from_memory)(int slot, int sampler_module, void* data, uint32_t data_size, int sample_slot)
    ctypedef int (*tsv_get_number_of_modules)(int slot)
    ctypedef int (*tsv_find_module)(int slot, char* name)
    ctypedef uint32_t (*tsv_get_module_flags)(int slot, int mod_num)
    ctypedef int* (*tsv_get_module_inputs)(int slot, int mod_num)
    ctypedef int* (*tsv_get_module_outputs)(int slot, int mod_num)
    ctypedef char* (*tsv_get_module_name)(int slot, int mod_num)
    ctypedef uint32_t (*tsv_get_module_xy)(int slot, int mod_num)
    ctypedef int (*tsv_get_module_color)(int slot, int mod_num)
    ctypedef uint32_t (*tsv_get_module_finetune)(int slot, int mod_num)
    ctypedef uint32_t (*tsv_get_module_scope2)(int slot, int mod_num, int channel, int16_t* dest_buf, uint32_t samples_to_read)
    ctypedef int (*tsv_module_curve)(int slot, int mod_num, int curve_num, float* data, int len, int w)
    ctypedef int (*tsv_get_number_of_module_ctls)(int slot, int mod_num)
    ctypedef char* (*tsv_get_module_ctl_name)(int slot, int mod_num, int ctl_num)
    ctypedef int (*tsv_get_module_ctl_value)(int slot, int mod_num, int ctl_num, int scaled)
    ctypedef int (*tsv_get_number_of_patterns)(int slot)
    ctypedef int (*tsv_find_pattern)(int slot, char* name)
    ctypedef int (*tsv_get_pattern_x)(int slot, int pat_num)
    ctypedef int (*tsv_get_pattern_y)(int slot, int pat_num)
    ctypedef int (*tsv_get_pattern_tracks)(int slot, int pat_num)
    ctypedef int (*tsv_get_pattern_lines)(int slot, int pat_num)
    ctypedef char* (*tsv_get_pattern_name)(int slot, int pat_num)
    ctypedef sunvox_note* (*tsv_get_pattern_data)(int slot, int pat_num)
    ctypedef int (*tsv_pattern_mute)(int slot, int pat_num, int mute)
    ctypedef uint32_t (*tsv_get_ticks)()
    ctypedef uint32_t (*tsv_get_ticks_per_second)()
    ctypedef char* (*tsv_get_log)(int size)

    cdef int sv_load_dll()
    cdef int sv_unload_dll()
    cdef int sv_load_dll2(char * filename)

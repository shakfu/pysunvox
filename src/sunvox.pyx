import time

from libc.stdlib cimport malloc, free
from libc.stdio cimport FILE, fopen, fwrite, fclose, printf

from sunvox cimport *


DEF SAMPLE_RATE = 44100
DEF NUM_CHANNELS = 2
DEF BUFFER_SIZE = 1024
DEF SAMPLE_TYPE = 2


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


# def generate(path: str, wav_out: str):
#     _generate(path.encode('utf8'), wav_out.encode('utf8'))


# cdef int keep_running = 1

# cdef void int_handler(int param):
#     keep_running = 0

# def generate(path: str, wav_out: str):

#     # signal(SIGINT, int_handler)

#     cdef int frame_size = NUM_CHANNELS * SAMPLE_TYPE # bytes per frame
#     cdef void* buf = malloc( BUFFER_SIZE * frame_size ) # Audio buffer
#     cdef int song_len_frames = sv_get_song_length_frames( 0 )
#     cdef int song_len_bytes = song_len_frames * frame_size
#     cdef int cur_frame = 0
#     cdef int val = 0
#     cdef int pos = 0
#     cdef int frames_num = 0
#     cdef int new_pos = 0
#     # cdef int keep_running = 1
#     cdef int volume = 256
#     cdef int slot = 0
#     cdef FILE* f = NULL

#     ver = sv_init(NULL, 44100, 2, 0)
#     if ver >= 0:
#         sv_open_slot(slot)
#         sv_load(slot, path.encode('utf8'))
#         sv_volume(slot, volume)
#         sv_play_from_beginning(slot)

#         # Saving the audio stream to the WAV file:
#         # (audio format: 16/32-bit stereo interleaved (LRLRLRLR...))
#         f = fopen(wav_out.encode('utf8'), "wb")
#         if f:
#             # WAV header:
#             fwrite(<void*>"RIFF", 1, 4, f)
#             val = 4 + 24 + 8 + song_len_bytes
#             fwrite(&val, 4, 1, f )
#             fwrite(<void*>"WAVE", 1, 4, f)

#             # WAV FORMAT:
#             fwrite(<void*>"fmt ", 1, 4, f)
#             val = 16
#             fwrite(&val, 4, 1, f)

#             # format
#             val = 1
#             if (SAMPLE_TYPE == 4):
#                 val = 3
#             fwrite(&val, 2, 1, f) 
            
#             # channels
#             val = NUM_CHANNELS
#             fwrite(&val, 2, 1, f)

#             # frames per second
#             val = SAMPLE_RATE
#             fwrite(&val, 4, 1, f) 

#             # bytes per second
#             val = SAMPLE_RATE * frame_size
#             fwrite(&val, 4, 1, f)
            
#             # block align
#             val = frame_size
#             fwrite(&val, 2, 1, f) 

#             # bits
#             val = SAMPLE_TYPE * 8
#             fwrite(&val, 2, 1, f) 

#             # WAV DATA:
#             fwrite(<void*>"data", 1, 4, f)
#             fwrite(&song_len_bytes, 4, 1, f)

#             # while (keep_running and cur_frame < song_len_frames):
#             while (cur_frame < song_len_frames):
#                 # Get the next piece of audio:
#                 frames_num = BUFFER_SIZE
#                 if (cur_frame + frames_num > song_len_frames):
#                     frames_num = song_len_frames - cur_frame
#                 sv_audio_callback( buf, frames_num, 0, sv_get_ticks() )
#                 cur_frame += frames_num

#                 # Save this data to the file:
#                 fwrite( buf, 1, frames_num * frame_size, f )

#                 # Print some info:
#                 new_pos = <int>( ( <float>cur_frame / <float>song_len_frames ) * 100 )
#                 if( pos != new_pos ):
#                     printf( "Playing position: %d %%\n", pos )
#                     pos = new_pos

#             fclose(f)
#             free(buf)
        
#         else:

#             print( "Can't open the file\n" )

#         sv_stop(0)
#         sv_close_slot(0)
#         sv_deinit()

#     else:
#         printf( "sv_init() error %d\n", ver )

#     sv_unload_dll()

#     return 0


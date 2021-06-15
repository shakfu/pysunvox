from sunvox cimport *

"""
Basically python/cython translation of this test code from the sunvox library:

#define SUNVOX_MAIN 

#include <dlfcn.h>
#include "sunvox.h"

int main()
{
    if( sv_load_dll() ) return 1;
    int ver = sv_init( 0, 44100, 2, 0 );
    if( ver >= 0 )
    {
        sv_open_slot( 0 );
        /*
        The SunVox is initialized.
        Slot 0 is open and ready for use.
        Then you can load and play some files in this slot.
        */
        sv_close_slot( 0 );
        sv_deinit();
    }
    sv_unload_dll();
    return 0;
}
"""


def hello():
    sv_load_dll()
    ver = sv_init(NULL, 44100, 2, 0)
    if ver >= 0:
        sv_open_slot(0)
        sv_close_slot(0)
        sv_deinit()
    sv_unload_dll()

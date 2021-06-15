/* We are using a dynamic lib. 
   SUNVOX_MAIN adds implementation of sv_load_dll()/sv_unload_dll()
*/
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


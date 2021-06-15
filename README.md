# pysunvox - a cython wrap of the sunvoxlib

This is a minimal proof-of-concept cython wrap of the [sunvox](https://warmplace.ru/soft/sunvox/) [library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php) for macOS.


## Usage
```python

import sunvox

sunvox.play('resources/test.sunvox')

```

The cython code for the function above is


```cython
import time
from sunvox cimport *


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
```




## Requirements

Tested on macOS only.

- [sunvox library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php)
- python3
- cython


## Compilation

```base
# to compile
make

# to test
make test

# to clean
make clean

# to reset (removes cython generated c-code)
make reset

```


## License / Credits
All rights for `sunvox` and its developer library reserved to its author, Alexander Zolotov. 

(see: https://warmplace.ru)

Powered by SunVox (modular synth & tracker)
Copyright (c) 2008 - 2020, Alexander Zolotov <nightradio@gmail.com>, WarmPlace.ru

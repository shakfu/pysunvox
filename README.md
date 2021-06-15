# pysunvox - a cython wrap of the sunvoxlib

This is a minimal proof-of-concept cython wrap of the [sunvox](https://warmplace.ru/soft/sunvox/) [library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php) for macOS.



## Requirements

Tested on macOS only.

- [sunvox library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php)
- python3
- cython


## Usage

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

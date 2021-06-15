# pysunvox - a cython wrap of the sunvoxlib

This is a minimal proof-of-concept cython wrap of the [sunvox](https://warmplace.ru/soft/sunvox/) [library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php) for macOS.

All rights for `sunvox` and its developer library reserved to its author, Alexander Zolotov. (see: https://warmplace.ru)


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


# pysunvox

Python bindings for the [SunVox](https://warmplace.ru/soft/sunvox/) modular synthesizer [library](https://warmplace.ru/soft/sunvox/sunvox_lib.php).

## Features

- High-level Pythonic API with context managers, properties, and type hints
- Low-level 1:1 wrappers of the C `sv_*` functions
- Full access to modules, controllers, patterns, and playback
- Thread-safe slot locking

## Installation

```bash
pip install pysunvox
```

## Quick Start

```python
import time
from pysunvox import SunVox

with SunVox(sample_rate=44100) as sv:
    with sv.open_slot(0) as slot:
        slot.load("song.sunvox")
        print(f"Song: {slot.name}, BPM: {slot.bpm}")
        slot.volume = 256
        slot.play_from_beginning()
        time.sleep(10)
        slot.stop()
```

## Command-Line Interface

pysunvox provides a CLI for common operations:

```bash
# Show help
pysunvox --help

# Display project information
pysunvox info song.sunvox

# List all modules in a project
pysunvox modules song.sunvox

# Show detailed module info (including controllers)
pysunvox module song.sunvox 1

# List all patterns
pysunvox patterns song.sunvox

# Play a project
pysunvox play song.sunvox

# Play with options
pysunvox play song.sunvox --duration 30 --volume 200 --line 0

# Show version information
pysunvox version
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `info <file>` | Show project metadata (name, BPM, TPL, duration, counts) |
| `modules <file>` | List all modules with type, name, and flags |
| `module <file> <id>` | Show detailed module info including controllers |
| `patterns <file>` | List all patterns with tracks, lines, and position |
| `play <file>` | Play a project (`-d` duration, `-v` volume, `-l` start line) |
| `version` | Show pysunvox and SunVox library versions |

## API Overview

### High-Level API

The high-level API provides Pythonic classes with context managers:

```python
from pysunvox import SunVox, Slot, Module, Pattern

# Initialize engine and open a slot
with SunVox(sample_rate=44100) as sv:
    with sv.open_slot(0) as slot:
        # Load and play a project
        slot.load("project.sunvox")
        slot.play()

        # Access song properties
        print(f"BPM: {slot.bpm}, TPL: {slot.tpl}")
        print(f"Length: {slot.length_lines} lines")

        # Work with modules
        for i in range(slot.num_modules):
            module = slot.get_module(i)
            if module.exists:
                print(f"Module {i}: {module.name} ({module.type})")

        # Create modules (requires lock)
        with slot.lock():
            synth = slot.new_module("Generator", "MySynth", x=256, y=256)
            synth.connect_to(0)  # Connect to Output

        # Access module controllers
        ctl = synth.get_controller(0)
        print(f"{ctl.name}: {ctl.value} (range: {ctl.min_value}-{ctl.max_value})")
        ctl.value = 128

        # Work with patterns
        with slot.lock():
            pattern = slot.new_pattern("MyPattern", tracks=4, lines=32)
            pattern.set_event(track=0, line=0, note=60, vel=128, module=synth.num + 1)

        # Save the project
        slot.save("modified.sunvox")
```

### Low-Level API

Direct access to `sv_*` functions via the `_core` module:

```python
from pysunvox import _core

# Initialize
_core.init(None, 44100, 2, 0)
_core.open_slot(0)

# Load and play
_core.load(0, "song.sunvox")
_core.play_from_beginning(0)

# Query state
print(f"BPM: {_core.get_song_bpm(0)}")
print(f"Current line: {_core.get_current_line(0)}")

# Cleanup
_core.stop(0)
_core.close_slot(0)
_core.deinit()
```

### Constants

```python
from pysunvox import (
    # Note commands
    NOTECMD_NOTE_OFF,
    NOTECMD_ALL_NOTES_OFF,
    NOTECMD_PLAY,
    NOTECMD_STOP,

    # Init flags
    SV_INIT_FLAG_NO_DEBUG_OUTPUT,
    SV_INIT_FLAG_OFFLINE,
    SV_INIT_FLAG_AUDIO_FLOAT32,

    # Module flags
    SV_MODULE_FLAG_EXISTS,
    SV_MODULE_FLAG_GENERATOR,
    SV_MODULE_FLAG_EFFECT,
)
```

## Supported Platforms

Pre-built wheels are available for:

- **macOS**: x86_64, arm64
- **Linux**: x86_64, aarch64 (glibc only, no musl/Alpine)
- **Windows**: AMD64

Python versions: 3.10, 3.11, 3.12, 3.13

## Building from Source

Requires the [SunVox library for developers](https://warmplace.ru/soft/sunvox/sunvox_lib.php).

```bash
# Install dependencies and build
make sync
make build

# Run tests
make test

# Build wheel with bundled library
make wheel

# Clean build artifacts
make clean
```

## License / Credits

All rights for SunVox and its developer library reserved to its author, Alexander Zolotov.

See: <https://warmplace.ru>

Powered by SunVox (modular synth & tracker)
Copyright (c) 2008 - 2024, Alexander Zolotov <nightradio@gmail.com>, WarmPlace.ru

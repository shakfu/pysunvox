# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2]

### Fixed

- Fixed Windows build with MSVC:
  - Fixed `sunvox.h` header compatibility with MSVC C compiler (trailing `__stdcall` not supported in C)
  - Fixed library path to use architecture-specific directory (`lib_x86_64`)
  - Added import library (`sunvox.lib`) generation for MSVC linking
  - Fixed DLL bundling with delvewheel for wheel packaging
- Fixed macOS wheels built for the non-host architecture linking the wrong
  `sunvox.dylib`. CMake picked `sunvox_lib/macos/lib_<arch>` from
  `CMAKE_SYSTEM_PROCESSOR`, which reports the build host, while cibuildwheel builds
  x86_64 wheels on arm64 runners. The linker discarded the mismatched dylib, and
  because Python extension modules link with `-undefined dynamic_lookup` the build
  still succeeded; it failed at import with `symbol not found in flat namespace
  '_sv_audio_callback'`. Selection now reads `CMAKE_OSX_ARCHITECTURES` when set.
- Fixed the build-wheels workflow: the `check` job listed the commented-out
  `build_sdist` in `needs`, so GitHub rejected the file and every run finished with
  zero jobs.
- Fixed delvewheel failing with `Unable to find library: sunvox.dll`. The DLL is
  installed beside `_core.pyd` by CMake, so repair now excludes it.

### Changed

- The SunVox library is no longer tracked in git. `scripts/fetch_sunvox_lib.py`
  downloads a pinned URL, verifies its SHA-256, extracts the subset the build can
  reach into `thirdparty/`, and reapplies the two MSVC edits to `sunvox.h`. Each
  edit must match upstream text exactly, so an upstream change to either region
  fails the fetch instead of silently reverting the patch. `make sync` and
  `make build` depend on it; the CI workflow runs it before cibuildwheel.

  `sdist.include` keeps `thirdparty/sunvox_lib/**` in source distributions, so
  installing from an sdist still needs no network. The pruned subset drops
  `lib_arm/` and the `*_lofi` builds, which `CMakeLists.txt` never selects, along
  with the android, iOS and JS payloads: the sdist is 4.2 MB, down from 6.3 MB.

- Windows builds generate `sunvox.lib` at CMake configure time from the tracked
  `support/sunvox.def` using `lib.exe`, replacing the committed import library.
  Upstream ships only `sunvox.dll`.

- Updated the SunVox library from 2.1.4 to 2.1.4d
  (https://www.warmplace.ru/soft/sunvox/sunvox_lib-2.1.4d.zip). Binaries and docs
  only: `headers/sunvox.h` is unchanged upstream, the exported symbol set is
  identical (96 entries, still matching `support/sunvox.def`), and `sv_init()`
  still reports 2.1.4.
- Linux wheels target `manylinux_2_34` instead of `manylinux_2_28`. The vendored
  `sunvox.so` references `GLIBC_2.34`, which the older policy rejects. `libasound.so.2`
  is left unvendored so ALSA loads its plugins and configuration from the host.
- Linux aarch64 wheels build on a native ARM runner rather than under QEMU.

## [0.1.1]

### Fixed

- Updated README.md CLI documentation to match actual command-line interface
  - `modules`, `module`, `patterns` are now flags (`-m`, `-M`, `-p`) on the `info` command
  - `version` is now `info --version`
  - Added documentation for the `songs` command

## [0.1.0]

### Added

- Command-line interface (`pysunvox` command) with the following subcommands:
  - `info` - Display project metadata (name, BPM, TPL, duration, module/pattern counts)
  - `modules` - List all modules with type, name, and flags
  - `module` - Show detailed module information including all controllers
  - `patterns` - List all patterns with tracks, lines, and position
  - `play` - Play a project with options for duration, start line, and volume
  - `version` - Show pysunvox and SunVox library versions
- Script entry point in `pyproject.toml` for CLI access via `pysunvox` command

- Initial release
- High-level Pythonic API with context managers, properties, and type hints
- Low-level 1:1 wrappers of the C `sv_*` functions
- Full access to modules, controllers, patterns, and playback
- Thread-safe slot locking
- Pre-built wheels for macOS (x86_64, arm64), Linux (x86_64, aarch64), and Windows (AMD64)
- Support for Python 3.10, 3.11, 3.12, 3.13, 3.14

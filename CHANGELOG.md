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

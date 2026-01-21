"""
pysunvox CLI - Command-line interface for the SunVox modular synthesizer library.

Usage:
    pysunvox songs <dir> [-r]              Scan and analyze all songs in a directory
    pysunvox info <file>                   Show song information (default)
    pysunvox info <file> --modules         List all modules in a project
    pysunvox info <file> --module <id>     Show detailed module info
    pysunvox info <file> --patterns        List all patterns in a project
    pysunvox info --version                Show SunVox library version
    pysunvox play <file>                   Play a project
"""

import argparse
import sys
import time
from pathlib import Path

from pysunvox import SunVox, __version__


def cmd_songs(args: argparse.Namespace) -> int:
    """Scan and analyze all songs in a directory."""
    dirpath = Path(args.directory)
    if not dirpath.exists():
        print(f"Error: Directory not found: {dirpath}", file=sys.stderr)
        return 1
    if not dirpath.is_dir():
        print(f"Error: Not a directory: {dirpath}", file=sys.stderr)
        return 1

    if args.recursive:
        sunvox_files = sorted(dirpath.rglob("*.sunvox"))
    else:
        sunvox_files = sorted(dirpath.glob("*.sunvox"))

    if not sunvox_files:
        print(f"No .sunvox files found in {dirpath}")
        return 0

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            print(f"{'File':<40}  {'Name':<20}  {'BPM':>4}  {'Mod':>4}  {'Pat':>4}  {'Duration':>10}")
            print("-" * 92)
            for filepath in sunvox_files:
                try:
                    slot.load(str(filepath))
                    duration = slot.length_frames / sv.sample_rate
                    duration_str = f"{duration:.2f}s"
                    display_path = str(filepath.relative_to(dirpath)) if args.recursive else filepath.name
                    print(f"{display_path:<40}  {slot.name:<20}  {slot.bpm:>4}  "
                          f"{slot.num_modules:>4}  {slot.num_patterns:>4}  {duration_str:>10}")
                except Exception as e:
                    display_path = str(filepath.relative_to(dirpath)) if args.recursive else filepath.name
                    print(f"{display_path:<40}  (error: {e})")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Show information about a SunVox file or library."""
    # Handle --version separately (no file required)
    if args.lib_version:
        print(f"pysunvox: {__version__}")
        with SunVox() as sv:
            version = sv.version
            if version is not None:
                major = (version >> 16) & 0xFF
                minor = (version >> 8) & 0xFF
                patch = version & 0xFF
                print(f"SunVox library: {major}.{minor}.{patch}")
            print(f"Sample rate: {sv.sample_rate} Hz")
        return 0

    # All other options require a file
    if args.file is None:
        print("Error: A file is required unless using --version", file=sys.stderr)
        return 1

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))

            if args.module is not None:
                # Show detailed module info
                mod = slot.get_module(args.module)
                if not mod.exists:
                    print(f"Error: Module {args.module} does not exist", file=sys.stderr)
                    return 1

                print(f"Module {args.module}: {mod.name}")
                print(f"  Type: {mod.type}")
                print(f"  Position: {mod.position}")
                print(f"  Color: #{mod.color:06x}")
                print(f"  Generator: {mod.is_generator}")
                print(f"  Effect: {mod.is_effect}")
                print(f"  Muted: {mod.is_muted}")
                print(f"  Solo: {mod.is_solo}")
                print(f"  Bypassed: {mod.is_bypassed}")
                print(f"  Inputs: {mod.inputs}")
                print(f"  Outputs: {mod.outputs}")
                print()
                print(f"  Controllers ({mod.num_controllers}):")
                for j in range(mod.num_controllers):
                    ctl = mod.get_controller(j)
                    print(f"    {j}: {ctl.name} = {ctl.display_value} "
                          f"(range: {ctl.min_value}-{ctl.max_value})")

            elif args.modules:
                # List all modules
                print(f"Modules in '{slot.name}':")
                print()
                print(f"{'ID':>4}  {'Type':<20}  {'Name':<24}  {'Flags'}")
                print("-" * 70)
                for i in range(slot.num_modules):
                    mod = slot.get_module(i)
                    if mod.exists:
                        flags = []
                        if mod.is_generator:
                            flags.append("gen")
                        if mod.is_effect:
                            flags.append("fx")
                        if mod.is_muted:
                            flags.append("mute")
                        if mod.is_solo:
                            flags.append("solo")
                        if mod.is_bypassed:
                            flags.append("bypass")
                        flags_str = ",".join(flags) if flags else "-"
                        print(f"{i:>4}  {mod.type:<20}  {mod.name:<24}  {flags_str}")

            elif args.patterns:
                # List all patterns
                print(f"Patterns in '{slot.name}':")
                print()
                print(f"{'ID':>4}  {'Name':<24}  {'Tracks':>6}  {'Lines':>6}  {'Position'}")
                print("-" * 70)
                for i in range(slot.num_patterns):
                    pat = slot.get_pattern(i)
                    if pat.exists:
                        x, y = pat.position
                        print(f"{i:>4}  {pat.name:<24}  {pat.tracks:>6}  "
                              f"{pat.lines:>6}  ({x}, {y})")

            else:
                # Default: show song info
                print(f"File: {filepath.name}")
                print(f"Name: {slot.name}")
                print(f"BPM: {slot.bpm}")
                print(f"TPL: {slot.tpl}")
                print(f"Lines: {slot.length_lines}")
                print(f"Frames: {slot.length_frames}")
                duration = slot.length_frames / sv.sample_rate
                print(f"Duration: {duration:.2f}s")
                print(f"Modules: {slot.num_modules}")
                print(f"Patterns: {slot.num_patterns}")

    return 0


def cmd_play(args: argparse.Namespace) -> int:
    """Play a project."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))
            duration = slot.length_frames / sv.sample_rate

            if args.duration is not None:
                play_duration = min(args.duration, duration)
            else:
                play_duration = duration

            print(f"Playing: {slot.name}")
            print(f"Duration: {play_duration:.2f}s (total: {duration:.2f}s)")
            print("Press Ctrl+C to stop")

            if args.line is not None:
                slot.rewind(args.line)

            slot.volume = args.volume

            try:
                slot.play()
                start_time = time.time()
                while time.time() - start_time < play_duration:
                    if not slot.is_playing and slot.autostop:
                        break
                    time.sleep(0.1)
                slot.stop()
            except KeyboardInterrupt:
                slot.stop()
                print("\nStopped")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pysunvox",
        description="Command-line interface for the SunVox modular synthesizer library",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"pysunvox {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # songs command
    songs_parser = subparsers.add_parser("songs", help="Scan and analyze all songs in a directory")
    songs_parser.add_argument("directory", help="Path to directory containing .sunvox files")
    songs_parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Scan subdirectories recursively",
    )
    songs_parser.set_defaults(func=cmd_songs)

    # info command (consolidated info subcommand)
    info_parser = subparsers.add_parser("info", help="Show information about a SunVox file or library")
    info_parser.add_argument("file", nargs="?", help="Path to .sunvox file")
    info_parser.add_argument(
        "-m", "--modules",
        action="store_true",
        help="List all modules in the project",
    )
    info_parser.add_argument(
        "-M", "--module",
        type=int,
        metavar="ID",
        help="Show detailed info for a specific module",
    )
    info_parser.add_argument(
        "-p", "--patterns",
        action="store_true",
        help="List all patterns in the project",
    )
    info_parser.add_argument(
        "--version",
        dest="lib_version",
        action="store_true",
        help="Show SunVox library version (no file required)",
    )
    info_parser.set_defaults(func=cmd_info)

    # play command
    play_parser = subparsers.add_parser("play", help="Play a project")
    play_parser.add_argument("file", help="Path to .sunvox file")
    play_parser.add_argument(
        "-d", "--duration",
        type=float,
        default=None,
        help="Maximum playback duration in seconds",
    )
    play_parser.add_argument(
        "-l", "--line",
        type=int,
        default=None,
        help="Start playback from this line",
    )
    play_parser.add_argument(
        "-v", "--volume",
        type=int,
        default=256,
        help="Playback volume (0-256, default: 256)",
    )
    play_parser.set_defaults(func=cmd_play)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

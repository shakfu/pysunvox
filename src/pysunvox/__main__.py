"""
pysunvox CLI - Command-line interface for the SunVox modular synthesizer library.

Usage:
    pysunvox info <file>           Show project information
    pysunvox modules <file>        List all modules in a project
    pysunvox patterns <file>       List all patterns in a project
    pysunvox play <file>           Play a project
    pysunvox version               Show SunVox library version
"""

import argparse
import sys
import time
from pathlib import Path

from pysunvox import SunVox, Slot, __version__


def cmd_info(args: argparse.Namespace) -> int:
    """Show project information."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))
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


def cmd_modules(args: argparse.Namespace) -> int:
    """List all modules in a project."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))
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
    return 0


def cmd_module_info(args: argparse.Namespace) -> int:
    """Show detailed information about a module."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))
            mod = slot.get_module(args.id)
            if not mod.exists:
                print(f"Error: Module {args.id} does not exist", file=sys.stderr)
                return 1

            print(f"Module {args.id}: {mod.name}")
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
    return 0


def cmd_patterns(args: argparse.Namespace) -> int:
    """List all patterns in a project."""
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    with SunVox() as sv:
        with sv.open_slot(0) as slot:
            slot.load(str(filepath))
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


def cmd_version(args: argparse.Namespace) -> int:
    """Show version information."""
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

    # info command
    info_parser = subparsers.add_parser("info", help="Show project information")
    info_parser.add_argument("file", help="Path to .sunvox file")
    info_parser.set_defaults(func=cmd_info)

    # modules command
    modules_parser = subparsers.add_parser("modules", help="List all modules")
    modules_parser.add_argument("file", help="Path to .sunvox file")
    modules_parser.set_defaults(func=cmd_modules)

    # module command (detailed info)
    module_parser = subparsers.add_parser("module", help="Show module details")
    module_parser.add_argument("file", help="Path to .sunvox file")
    module_parser.add_argument("id", type=int, help="Module ID")
    module_parser.set_defaults(func=cmd_module_info)

    # patterns command
    patterns_parser = subparsers.add_parser("patterns", help="List all patterns")
    patterns_parser.add_argument("file", help="Path to .sunvox file")
    patterns_parser.set_defaults(func=cmd_patterns)

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

    # version command
    version_parser = subparsers.add_parser(
        "version", help="Show SunVox library version"
    )
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

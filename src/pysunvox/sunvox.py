"""
High-level Pythonic API for SunVox.

This module provides a clean, object-oriented interface to the SunVox
modular synthesizer library with context managers, properties, and
type hints.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional, Union

from pysunvox import _core


class SunVoxError(Exception):
    """Base exception for SunVox errors."""

    pass


class SunVox:
    """Main SunVox engine class.

    Manages the global SunVox engine initialization. Use as a context manager
    for automatic cleanup.

    Example:
        with SunVox(sample_rate=44100) as sv:
            with sv.open_slot(0) as slot:
                slot.load("song.sunvox")
                slot.play()
    """

    _initialized: bool = False

    def __init__(
        self,
        config: Optional[str] = None,
        sample_rate: int = 44100,
        channels: int = 2,
        flags: int = 0,
    ):
        """Initialize the SunVox engine.

        Args:
            config: Configuration string (e.g., "buffer=1024|audiodriver=alsa").
            sample_rate: Desired sample rate in Hz (minimum 44100).
            channels: Number of channels (only 2 supported).
            flags: Combination of SV_INIT_FLAG_* constants.
        """
        self._config = config
        self._sample_rate = sample_rate
        self._channels = channels
        self._flags = flags
        self._version: Optional[int] = None

    def __enter__(self) -> "SunVox":
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.deinit()

    def init(self) -> int:
        """Initialize the SunVox engine.

        Returns:
            Version number on success.

        Raises:
            SunVoxError: If initialization fails.
        """
        if SunVox._initialized:
            raise SunVoxError("SunVox is already initialized")

        result = _core.init(self._config, self._sample_rate, self._channels, self._flags)
        if result < 0:
            raise SunVoxError(f"Failed to initialize SunVox: error code {result}")

        SunVox._initialized = True
        self._version = result
        return result

    def deinit(self) -> None:
        """Deinitialize the SunVox engine."""
        if SunVox._initialized:
            _core.deinit()
            SunVox._initialized = False

    @property
    def version(self) -> Optional[int]:
        """Get the SunVox version number."""
        return self._version

    @property
    def sample_rate(self) -> int:
        """Get the actual sample rate (may differ from requested)."""
        return _core.get_sample_rate()

    @staticmethod
    def get_ticks() -> int:
        """Get current system tick counter."""
        return _core.get_ticks()

    @staticmethod
    def get_ticks_per_second() -> int:
        """Get number of system ticks per second."""
        return _core.get_ticks_per_second()

    def open_slot(self, slot_num: int = 0) -> "Slot":
        """Create a Slot object for the given slot number.

        Args:
            slot_num: Slot number (default 0).

        Returns:
            Slot object (use as context manager for auto open/close).
        """
        return Slot(slot_num)


class Slot:
    """Represents a SunVox slot.

    A slot is an independent SunVox engine instance that can load and play
    a single project. Use as a context manager for automatic open/close.

    Example:
        with sv.open_slot(0) as slot:
            slot.load("song.sunvox")
            print(f"Song: {slot.name}, BPM: {slot.bpm}")
            slot.play()
    """

    def __init__(self, slot_num: int):
        """Initialize a Slot object.

        Args:
            slot_num: Slot number.
        """
        self._slot = slot_num
        self._is_open = False

    def __enter__(self) -> "Slot":
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @property
    def slot_num(self) -> int:
        """Get the slot number."""
        return self._slot

    @property
    def is_open(self) -> bool:
        """Check if the slot is open."""
        return self._is_open

    def open(self) -> None:
        """Open the slot.

        Raises:
            SunVoxError: If opening fails.
        """
        result = _core.open_slot(self._slot)
        if result < 0:
            raise SunVoxError(f"Failed to open slot {self._slot}: error code {result}")
        self._is_open = True

    def close(self) -> None:
        """Close the slot."""
        if self._is_open:
            _core.close_slot(self._slot)
            self._is_open = False

    @contextmanager
    def lock(self) -> Iterator[None]:
        """Context manager for thread-safe slot access.

        Use this when reading/modifying SunVox data from multiple threads.

        Example:
            with slot.lock():
                module_id = slot.new_module("Generator", "synth")
        """
        _core.lock_slot(self._slot)
        try:
            yield
        finally:
            _core.unlock_slot(self._slot)

    # ========================================================================
    # Project I/O
    # ========================================================================

    def load(self, filename: str) -> None:
        """Load a SunVox project from file.

        Args:
            filename: Path to the .sunvox file.

        Raises:
            SunVoxError: If loading fails.
        """
        result = _core.load(self._slot, filename)
        if result < 0:
            raise SunVoxError(f"Failed to load '{filename}': error code {result}")

    def load_from_memory(self, data: bytes) -> None:
        """Load a SunVox project from memory.

        Args:
            data: Project data as bytes.

        Raises:
            SunVoxError: If loading fails.
        """
        result = _core.load_from_memory(self._slot, data)
        if result < 0:
            raise SunVoxError(f"Failed to load from memory: error code {result}")

    def save(self, filename: str) -> None:
        """Save the project to a file.

        Args:
            filename: Path to save the .sunvox file.

        Raises:
            SunVoxError: If saving fails.
        """
        result = _core.save(self._slot, filename)
        if result < 0:
            raise SunVoxError(f"Failed to save '{filename}': error code {result}")

    def save_to_memory(self) -> bytes:
        """Save the project to memory.

        Returns:
            Project data as bytes.

        Raises:
            SunVoxError: If saving fails.
        """
        result = _core.save_to_memory(self._slot)
        if result is None:
            raise SunVoxError("Failed to save to memory")
        return result

    # ========================================================================
    # Playback control
    # ========================================================================

    def play(self) -> None:
        """Start playback from the current position."""
        _core.play(self._slot)

    def play_from_beginning(self) -> None:
        """Start playback from line 0."""
        _core.play_from_beginning(self._slot)

    def stop(self) -> None:
        """Stop playback.

        First call stops playback; second call resets to standby mode.
        """
        _core.stop(self._slot)

    def pause(self) -> None:
        """Pause the audio stream."""
        _core.pause(self._slot)

    def resume(self) -> None:
        """Resume the audio stream."""
        _core.resume(self._slot)

    def rewind(self, line: int = 0) -> None:
        """Rewind to a specific line.

        Args:
            line: Line number to rewind to (default 0).
        """
        _core.rewind(self._slot, line)

    # ========================================================================
    # Song properties
    # ========================================================================

    @property
    def name(self) -> str:
        """Get/set the song name."""
        return _core.get_song_name(self._slot)

    @name.setter
    def name(self, value: str) -> None:
        _core.set_song_name(self._slot, value)

    @property
    def bpm(self) -> int:
        """Get the song BPM (beats per minute)."""
        return _core.get_song_bpm(self._slot)

    @property
    def tpl(self) -> int:
        """Get the song TPL (ticks per line)."""
        return _core.get_song_tpl(self._slot)

    @property
    def length_frames(self) -> int:
        """Get the song length in frames."""
        return _core.get_song_length_frames(self._slot)

    @property
    def length_lines(self) -> int:
        """Get the song length in lines."""
        return _core.get_song_length_lines(self._slot)

    @property
    def current_line(self) -> int:
        """Get the current line number."""
        return _core.get_current_line(self._slot)

    @property
    def is_playing(self) -> bool:
        """Check if the song is playing."""
        return _core.end_of_song(self._slot) == 0

    @property
    def autostop(self) -> bool:
        """Get/set autostop mode (True = stop at end, False = loop forever)."""
        return _core.get_autostop(self._slot) == 1

    @autostop.setter
    def autostop(self, value: bool) -> None:
        _core.set_autostop(self._slot, 1 if value else 0)

    @property
    def volume(self) -> int:
        """Get/set the volume (0-256)."""
        return _core.volume(self._slot, -1)

    @volume.setter
    def volume(self, value: int) -> None:
        _core.volume(self._slot, value)

    # ========================================================================
    # Events
    # ========================================================================

    def send_event(
        self,
        track: int,
        note: int = 0,
        vel: int = 0,
        module: int = 0,
        ctl: int = 0,
        ctl_val: int = 0,
    ) -> None:
        """Send an event (note ON, note OFF, controller change, etc.).

        Args:
            track: Track number within the pattern.
            note: 0=nothing, 1-127=note, 128=note off, 129+=NOTECMD_*.
            vel: Velocity 1-129, 0=default.
            module: 0=empty, 1-65535=module number + 1.
            ctl: 0xCCEE where CC=controller number + 1, EE=effect.
            ctl_val: Controller value or effect parameter.
        """
        _core.send_event(self._slot, track, note, vel, module, ctl, ctl_val)

    # ========================================================================
    # Module operations
    # ========================================================================

    @property
    def num_modules(self) -> int:
        """Get the number of module slots."""
        return _core.get_number_of_modules(self._slot)

    def get_module(self, mod_num: int) -> "Module":
        """Get a Module object for the given module number.

        Args:
            mod_num: Module number.

        Returns:
            Module object.
        """
        return Module(self, mod_num)

    def find_module(self, name: str) -> Optional["Module"]:
        """Find a module by name.

        Args:
            name: Module name.

        Returns:
            Module object, or None if not found.
        """
        mod_num = _core.find_module(self._slot, name)
        if mod_num < 0:
            return None
        return Module(self, mod_num)

    def new_module(
        self,
        module_type: str,
        name: str,
        x: int = 512,
        y: int = 512,
        z: int = 0,
    ) -> "Module":
        """Create a new module.

        Must be called within a lock() context.

        Args:
            module_type: Module type (e.g., "Generator", "Sampler").
            name: Module name.
            x, y, z: Position coordinates.

        Returns:
            New Module object.

        Raises:
            SunVoxError: If creation fails.
        """
        mod_num = _core.new_module(self._slot, module_type, name, x, y, z)
        if mod_num < 0:
            raise SunVoxError(f"Failed to create module '{name}': error code {mod_num}")
        return Module(self, mod_num)

    def load_module(
        self,
        filename: str,
        x: int = 512,
        y: int = 512,
        z: int = 0,
    ) -> "Module":
        """Load a module from file.

        Args:
            filename: Path to file (sunsynth, xi, wav, aiff, ogg, mp3, flac).
            x, y, z: Position coordinates.

        Returns:
            New Module object.

        Raises:
            SunVoxError: If loading fails.
        """
        mod_num = _core.load_module(self._slot, filename, x, y, z)
        if mod_num < 0:
            raise SunVoxError(f"Failed to load module '{filename}': error code {mod_num}")
        return Module(self, mod_num)

    # ========================================================================
    # Pattern operations
    # ========================================================================

    @property
    def num_patterns(self) -> int:
        """Get the number of pattern slots."""
        return _core.get_number_of_patterns(self._slot)

    def get_pattern(self, pat_num: int) -> "Pattern":
        """Get a Pattern object for the given pattern number.

        Args:
            pat_num: Pattern number.

        Returns:
            Pattern object.
        """
        return Pattern(self, pat_num)

    def find_pattern(self, name: str) -> Optional["Pattern"]:
        """Find a pattern by name.

        Args:
            name: Pattern name.

        Returns:
            Pattern object, or None if not found.
        """
        pat_num = _core.find_pattern(self._slot, name)
        if pat_num < 0:
            return None
        return Pattern(self, pat_num)

    def new_pattern(
        self,
        name: str,
        tracks: int = 4,
        lines: int = 32,
        x: int = 0,
        y: int = 0,
        clone: int = -1,
        icon_seed: int = 0,
    ) -> "Pattern":
        """Create a new pattern.

        Must be called within a lock() context.

        Args:
            name: Pattern name.
            tracks: Number of tracks.
            lines: Number of lines.
            x, y: Position on timeline.
            clone: Pattern to clone (-1 for new empty pattern).
            icon_seed: Icon seed.

        Returns:
            New Pattern object.

        Raises:
            SunVoxError: If creation fails.
        """
        pat_num = _core.new_pattern(self._slot, clone, x, y, tracks, lines, icon_seed, name)
        if pat_num < 0:
            raise SunVoxError(f"Failed to create pattern '{name}': error code {pat_num}")
        return Pattern(self, pat_num)


class Module:
    """Represents a SunVox module."""

    def __init__(self, slot: Slot, mod_num: int):
        """Initialize a Module object.

        Args:
            slot: Parent Slot object.
            mod_num: Module number.
        """
        self._slot = slot
        self._mod_num = mod_num

    @property
    def slot(self) -> Slot:
        """Get the parent Slot."""
        return self._slot

    @property
    def num(self) -> int:
        """Get the module number."""
        return self._mod_num

    @property
    def exists(self) -> bool:
        """Check if the module exists."""
        return bool(_core.get_module_flags(self._slot.slot_num, self._mod_num) & _core.SV_MODULE_FLAG_EXISTS)

    @property
    def type(self) -> str:
        """Get the module type name."""
        return _core.get_module_type(self._slot.slot_num, self._mod_num)

    @property
    def name(self) -> str:
        """Get/set the module name."""
        return _core.get_module_name(self._slot.slot_num, self._mod_num)

    @name.setter
    def name(self, value: str) -> None:
        _core.set_module_name(self._slot.slot_num, self._mod_num, value)

    @property
    def flags(self) -> int:
        """Get the module flags."""
        return _core.get_module_flags(self._slot.slot_num, self._mod_num)

    @property
    def is_generator(self) -> bool:
        """Check if module is a generator (produces sound)."""
        return bool(self.flags & _core.SV_MODULE_FLAG_GENERATOR)

    @property
    def is_effect(self) -> bool:
        """Check if module is an effect (processes sound)."""
        return bool(self.flags & _core.SV_MODULE_FLAG_EFFECT)

    @property
    def is_muted(self) -> bool:
        """Check if module is muted."""
        return bool(self.flags & _core.SV_MODULE_FLAG_MUTE)

    @property
    def is_solo(self) -> bool:
        """Check if module is in solo mode."""
        return bool(self.flags & _core.SV_MODULE_FLAG_SOLO)

    @property
    def is_bypassed(self) -> bool:
        """Check if module is bypassed."""
        return bool(self.flags & _core.SV_MODULE_FLAG_BYPASS)

    @property
    def position(self) -> tuple[int, int]:
        """Get/set the module position (x, y)."""
        return _core.get_module_xy(self._slot.slot_num, self._mod_num)

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        _core.set_module_xy(self._slot.slot_num, self._mod_num, value[0], value[1])

    @property
    def color(self) -> int:
        """Get/set the module color (0xBBGGRR format)."""
        return _core.get_module_color(self._slot.slot_num, self._mod_num)

    @color.setter
    def color(self, value: int) -> None:
        _core.set_module_color(self._slot.slot_num, self._mod_num, value)

    @property
    def inputs(self) -> list[int]:
        """Get list of input module numbers."""
        return _core.get_module_inputs(self._slot.slot_num, self._mod_num)

    @property
    def outputs(self) -> list[int]:
        """Get list of output module numbers."""
        return _core.get_module_outputs(self._slot.slot_num, self._mod_num)

    @property
    def num_controllers(self) -> int:
        """Get number of controllers."""
        return _core.get_number_of_module_ctls(self._slot.slot_num, self._mod_num)

    def get_controller(self, ctl_num: int) -> "Controller":
        """Get a Controller object.

        Args:
            ctl_num: Controller number.

        Returns:
            Controller object.
        """
        return Controller(self, ctl_num)

    def connect_to(self, destination: Union["Module", int]) -> None:
        """Connect this module to another module.

        Must be called within a lock() context.

        Args:
            destination: Destination module or module number.
        """
        dest_num = destination.num if isinstance(destination, Module) else destination
        _core.connect_module(self._slot.slot_num, self._mod_num, dest_num)

    def disconnect_from(self, destination: Union["Module", int]) -> None:
        """Disconnect this module from another module.

        Must be called within a lock() context.

        Args:
            destination: Destination module or module number.
        """
        dest_num = destination.num if isinstance(destination, Module) else destination
        _core.disconnect_module(self._slot.slot_num, self._mod_num, dest_num)

    def remove(self) -> None:
        """Remove this module.

        Must be called within a lock() context.
        """
        _core.remove_module(self._slot.slot_num, self._mod_num)

    def __repr__(self) -> str:
        return f"Module({self._mod_num}, type='{self.type}', name='{self.name}')"


class Controller:
    """Represents a module controller."""

    def __init__(self, module: Module, ctl_num: int):
        """Initialize a Controller object.

        Args:
            module: Parent Module object.
            ctl_num: Controller number.
        """
        self._module = module
        self._ctl_num = ctl_num
        self._slot_num = module.slot.slot_num
        self._mod_num = module.num

    @property
    def module(self) -> Module:
        """Get the parent Module."""
        return self._module

    @property
    def num(self) -> int:
        """Get the controller number."""
        return self._ctl_num

    @property
    def name(self) -> str:
        """Get the controller name."""
        return _core.get_module_ctl_name(self._slot_num, self._mod_num, self._ctl_num)

    @property
    def value(self) -> int:
        """Get/set the controller value (real value)."""
        return _core.get_module_ctl_value(self._slot_num, self._mod_num, self._ctl_num, 0)

    @value.setter
    def value(self, val: int) -> None:
        _core.set_module_ctl_value(self._slot_num, self._mod_num, self._ctl_num, val, 0)

    @property
    def scaled_value(self) -> int:
        """Get/set the controller value (scaled 0x0000-0x8000)."""
        return _core.get_module_ctl_value(self._slot_num, self._mod_num, self._ctl_num, 1)

    @scaled_value.setter
    def scaled_value(self, val: int) -> None:
        _core.set_module_ctl_value(self._slot_num, self._mod_num, self._ctl_num, val, 1)

    @property
    def display_value(self) -> int:
        """Get the controller display value."""
        return _core.get_module_ctl_value(self._slot_num, self._mod_num, self._ctl_num, 2)

    @property
    def min_value(self) -> int:
        """Get the minimum value."""
        return _core.get_module_ctl_min(self._slot_num, self._mod_num, self._ctl_num, 0)

    @property
    def max_value(self) -> int:
        """Get the maximum value."""
        return _core.get_module_ctl_max(self._slot_num, self._mod_num, self._ctl_num, 0)

    @property
    def is_enum(self) -> bool:
        """Check if controller is an enum/selector type."""
        return _core.get_module_ctl_type(self._slot_num, self._mod_num, self._ctl_num) == 1

    def __repr__(self) -> str:
        return f"Controller({self._ctl_num}, name='{self.name}', value={self.value})"


class Pattern:
    """Represents a SunVox pattern."""

    def __init__(self, slot: Slot, pat_num: int):
        """Initialize a Pattern object.

        Args:
            slot: Parent Slot object.
            pat_num: Pattern number.
        """
        self._slot = slot
        self._pat_num = pat_num

    @property
    def slot(self) -> Slot:
        """Get the parent Slot."""
        return self._slot

    @property
    def num(self) -> int:
        """Get the pattern number."""
        return self._pat_num

    @property
    def exists(self) -> bool:
        """Check if the pattern exists (has lines > 0)."""
        return _core.get_pattern_lines(self._slot.slot_num, self._pat_num) > 0

    @property
    def name(self) -> str:
        """Get/set the pattern name."""
        return _core.get_pattern_name(self._slot.slot_num, self._pat_num)

    @name.setter
    def name(self, value: str) -> None:
        _core.set_pattern_name(self._slot.slot_num, self._pat_num, value)

    @property
    def x(self) -> int:
        """Get the pattern X position (line number on timeline)."""
        return _core.get_pattern_x(self._slot.slot_num, self._pat_num)

    @property
    def y(self) -> int:
        """Get the pattern Y position (vertical position on timeline)."""
        return _core.get_pattern_y(self._slot.slot_num, self._pat_num)

    @property
    def position(self) -> tuple[int, int]:
        """Get/set the pattern position (x, y)."""
        return (self.x, self.y)

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        _core.set_pattern_xy(self._slot.slot_num, self._pat_num, value[0], value[1])

    @property
    def tracks(self) -> int:
        """Get the number of tracks."""
        return _core.get_pattern_tracks(self._slot.slot_num, self._pat_num)

    @property
    def lines(self) -> int:
        """Get the number of lines."""
        return _core.get_pattern_lines(self._slot.slot_num, self._pat_num)

    def set_size(self, tracks: int, lines: int) -> None:
        """Set pattern size.

        Must be called within a lock() context.

        Args:
            tracks: Number of tracks.
            lines: Number of lines.
        """
        _core.set_pattern_size(self._slot.slot_num, self._pat_num, tracks, lines)

    def get_event(self, track: int, line: int) -> tuple[int, int, int, int, int]:
        """Get a pattern event.

        Args:
            track: Track number.
            line: Line number.

        Returns:
            Tuple of (note, vel, module, ctl, ctl_val).
        """
        return (
            _core.get_pattern_event(self._slot.slot_num, self._pat_num, track, line, 0),
            _core.get_pattern_event(self._slot.slot_num, self._pat_num, track, line, 1),
            _core.get_pattern_event(self._slot.slot_num, self._pat_num, track, line, 2),
            _core.get_pattern_event(self._slot.slot_num, self._pat_num, track, line, 3),
            _core.get_pattern_event(self._slot.slot_num, self._pat_num, track, line, 4),
        )

    def set_event(
        self,
        track: int,
        line: int,
        note: int = -1,
        vel: int = -1,
        module: int = -1,
        ctl: int = -1,
        ctl_val: int = -1,
    ) -> None:
        """Set a pattern event.

        Negative values are ignored (field not modified).

        Args:
            track: Track number.
            line: Line number.
            note: Note value.
            vel: Velocity.
            module: Module number.
            ctl: Controller/effect.
            ctl_val: Controller value/effect parameter.
        """
        _core.set_pattern_event(
            self._slot.slot_num, self._pat_num, track, line, note, vel, module, ctl, ctl_val
        )

    def mute(self) -> None:
        """Mute this pattern.

        Must be called within a lock() context.
        """
        _core.pattern_mute(self._slot.slot_num, self._pat_num, 1)

    def unmute(self) -> None:
        """Unmute this pattern.

        Must be called within a lock() context.
        """
        _core.pattern_mute(self._slot.slot_num, self._pat_num, 0)

    def remove(self) -> None:
        """Remove this pattern.

        Must be called within a lock() context.
        """
        _core.remove_pattern(self._slot.slot_num, self._pat_num)

    def __repr__(self) -> str:
        return f"Pattern({self._pat_num}, name='{self.name}', tracks={self.tracks}, lines={self.lines})"

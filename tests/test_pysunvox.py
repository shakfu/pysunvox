"""Tests for pysunvox SunVox wrapper module."""

import os
import pytest

import pysunvox
from pysunvox import (
    SunVox,
    SunVoxError,
    Slot,
    Module,
    Pattern,
    Note,
    NOTECMD_NOTE_OFF,
    SV_INIT_FLAG_NO_DEBUG_OUTPUT,
    SV_INIT_FLAG_OFFLINE,
    SV_INIT_FLAG_AUDIO_INT16,
    SV_INIT_FLAG_ONE_THREAD,
    SV_MODULE_FLAG_EXISTS,
)
from pysunvox import _core


# Path to test resources
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "..", "sunvox_lib", "resources")
SAMPLE_SONG = os.path.join(RESOURCES_DIR, "song01.sunvox")


class TestConstants:
    """Test that constants are exported correctly."""

    def test_note_commands(self):
        assert pysunvox.NOTECMD_NOTE_OFF == 128
        assert pysunvox.NOTECMD_ALL_NOTES_OFF == 129
        assert pysunvox.NOTECMD_CLEAN_SYNTHS == 130
        assert pysunvox.NOTECMD_STOP == 131
        assert pysunvox.NOTECMD_PLAY == 132

    def test_init_flags(self):
        assert pysunvox.SV_INIT_FLAG_NO_DEBUG_OUTPUT == (1 << 0)
        assert pysunvox.SV_INIT_FLAG_USER_AUDIO_CALLBACK == (1 << 1)
        assert pysunvox.SV_INIT_FLAG_OFFLINE == (1 << 1)
        assert pysunvox.SV_INIT_FLAG_AUDIO_INT16 == (1 << 2)
        assert pysunvox.SV_INIT_FLAG_AUDIO_FLOAT32 == (1 << 3)

    def test_module_flags(self):
        assert pysunvox.SV_MODULE_FLAG_EXISTS == (1 << 0)
        assert pysunvox.SV_MODULE_FLAG_GENERATOR == (1 << 1)
        assert pysunvox.SV_MODULE_FLAG_EFFECT == (1 << 2)


class TestNote:
    """Test the Note class."""

    def test_default_construction(self):
        note = Note()
        assert note.note == 0
        assert note.vel == 0
        assert note.module == 0
        assert note.ctl == 0
        assert note.ctl_val == 0

    def test_construction_with_values(self):
        note = Note(note=60, vel=100, module=1, ctl=0x0100, ctl_val=0x8000)
        assert note.note == 60
        assert note.vel == 100
        assert note.module == 1
        assert note.ctl == 0x0100
        assert note.ctl_val == 0x8000

    def test_property_setters(self):
        note = Note()
        note.note = 72
        note.vel = 127
        note.module = 5
        note.ctl = 0x0200
        note.ctl_val = 0x4000
        assert note.note == 72
        assert note.vel == 127
        assert note.module == 5
        assert note.ctl == 0x0200
        assert note.ctl_val == 0x4000

    def test_repr(self):
        note = Note(note=60, vel=100)
        repr_str = repr(note)
        assert "Note(" in repr_str
        assert "note=60" in repr_str
        assert "vel=100" in repr_str


class TestLowLevelAPI:
    """Test the low-level _core API."""

    def test_init_deinit(self):
        """Test basic init/deinit cycle."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        result = _core.init(None, 44100, 2, flags)
        try:
            assert result >= 0, f"init failed with code {result}"
            sample_rate = _core.get_sample_rate()
            assert sample_rate > 0
        finally:
            _core.deinit()

    def test_slot_operations(self):
        """Test slot open/close."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        _core.init(None, 44100, 2, flags)
        try:
            result = _core.open_slot(0)
            assert result >= 0, f"open_slot failed with code {result}"
            _core.close_slot(0)
        finally:
            _core.deinit()

    def test_ticks(self):
        """Test tick functions."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        _core.init(None, 44100, 2, flags)
        try:
            ticks = _core.get_ticks()
            tps = _core.get_ticks_per_second()
            assert ticks >= 0
            assert tps > 0
        finally:
            _core.deinit()


class TestHighLevelAPI:
    """Test the high-level SunVox API."""

    def test_sunvox_context_manager(self):
        """Test SunVox as context manager."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            assert sv.version is not None
            assert sv.version >= 0
            assert sv.sample_rate > 0

    def test_double_init_raises(self):
        """Test that double initialization raises error."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags):
            with pytest.raises(SunVoxError):
                sv2 = SunVox(sample_rate=44100, flags=flags)
                sv2.init()

    def test_slot_context_manager(self):
        """Test Slot as context manager."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                assert slot.is_open
                assert slot.slot_num == 0
            assert not slot.is_open


@pytest.mark.skipif(not os.path.exists(SAMPLE_SONG), reason="Sample song not found")
class TestProjectOperations:
    """Test project loading and manipulation."""

    def test_load_project(self):
        """Test loading a project file."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                assert slot.name != ""
                assert slot.bpm > 0
                assert slot.tpl > 0
                assert slot.length_lines > 0

    def test_project_properties(self):
        """Test reading project properties."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                # Test basic properties
                name = slot.name
                bpm = slot.bpm
                tpl = slot.tpl
                length_frames = slot.length_frames
                length_lines = slot.length_lines

                assert isinstance(name, str)
                assert bpm > 0
                assert tpl > 0
                assert length_frames > 0
                assert length_lines > 0

    def test_volume_control(self):
        """Test volume get/set."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                original = slot.volume
                slot.volume = 128
                assert slot.volume == 128
                slot.volume = original

    def test_autostop(self):
        """Test autostop get/set."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                slot.autostop = True
                assert slot.autostop == True
                slot.autostop = False
                assert slot.autostop == False


@pytest.mark.skipif(not os.path.exists(SAMPLE_SONG), reason="Sample song not found")
class TestModuleOperations:
    """Test module operations."""

    def test_enumerate_modules(self):
        """Test enumerating modules in a project."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                num_modules = slot.num_modules
                assert num_modules > 0

                # Module 0 is always the Output module
                output = slot.get_module(0)
                assert output.exists
                assert output.type == "Output"

    def test_module_properties(self):
        """Test reading module properties."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                output = slot.get_module(0)

                # Test properties
                assert isinstance(output.name, str)
                assert isinstance(output.type, str)
                assert isinstance(output.position, tuple)
                assert len(output.position) == 2
                assert isinstance(output.flags, int)

    def test_create_module(self):
        """Test creating a new module."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                with slot.lock():
                    gen = slot.new_module("Generator", "TestGen", x=400, y=400)
                    assert gen.exists
                    assert gen.name == "TestGen"
                    assert gen.type == "Generator"

    def test_connect_modules(self):
        """Test connecting modules."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                with slot.lock():
                    gen = slot.new_module("Generator", "TestGen", x=400, y=400)
                    output = slot.get_module(0)
                    gen.connect_to(output)
                    # Verify connection
                    assert 0 in gen.outputs


@pytest.mark.skipif(not os.path.exists(SAMPLE_SONG), reason="Sample song not found")
class TestPatternOperations:
    """Test pattern operations."""

    def test_enumerate_patterns(self):
        """Test enumerating patterns in a project."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                num_patterns = slot.num_patterns
                assert num_patterns > 0

                # Find first existing pattern
                for i in range(num_patterns):
                    pattern = slot.get_pattern(i)
                    if pattern.exists:
                        assert pattern.lines > 0
                        assert pattern.tracks > 0
                        break

    def test_pattern_properties(self):
        """Test reading pattern properties."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                # Find first existing pattern
                for i in range(slot.num_patterns):
                    pattern = slot.get_pattern(i)
                    if pattern.exists:
                        assert isinstance(pattern.name, str)
                        assert isinstance(pattern.position, tuple)
                        assert len(pattern.position) == 2
                        assert pattern.tracks > 0
                        assert pattern.lines > 0
                        break

    def test_create_pattern(self):
        """Test creating a new pattern."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                with slot.lock():
                    pattern = slot.new_pattern("TestPattern", tracks=8, lines=64)
                    assert pattern.exists
                    assert pattern.name == "TestPattern"
                    assert pattern.tracks == 8
                    assert pattern.lines == 64

    def test_pattern_events(self):
        """Test getting/setting pattern events."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                with slot.lock():
                    pattern = slot.new_pattern("TestPattern", tracks=4, lines=16)
                    # Set an event
                    pattern.set_event(track=0, line=0, note=60, vel=100, module=1)
                    # Get the event back
                    event = pattern.get_event(track=0, line=0)
                    assert event[0] == 60  # note
                    assert event[1] == 100  # vel
                    assert event[2] == 1  # module

    def test_pattern_data_memoryview(self):
        """Test direct pattern data access via memoryview."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                with slot.lock():
                    pattern = slot.new_pattern("TestPattern", tracks=4, lines=16)
                    # Set an event using the high-level API
                    pattern.set_event(track=0, line=0, note=60, vel=100, module=1)

                    # Get raw pattern data
                    data = _core.get_pattern_data(0, pattern.num)
                    assert data is not None
                    assert len(data) == 4 * 16 * 8  # tracks * lines * sizeof(sunvox_note)

                    # Verify we can read the note we set (offset 0, first byte is note)
                    assert data[0] == 60  # note
                    assert data[1] == 100  # vel


@pytest.mark.skipif(not os.path.exists(SAMPLE_SONG), reason="Sample song not found")
class TestPlayback:
    """Test playback control."""

    def test_playback_control(self):
        """Test basic playback operations."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                slot.autostop = True

                # Should start at beginning
                assert slot.current_line == 0

                # Play and stop
                slot.play_from_beginning()
                slot.stop()

                # Rewind and verify (current_line may be -1 when stopped)
                slot.rewind(0)
                line = slot.current_line
                assert line == 0 or line == -1  # -1 indicates stopped/standby state


@pytest.mark.skipif(not os.path.exists(SAMPLE_SONG), reason="Sample song not found")
class TestSaveLoad:
    """Test save/load operations."""

    def test_save_load_memory(self):
        """Test saving and loading from memory."""
        flags = SV_INIT_FLAG_NO_DEBUG_OUTPUT | SV_INIT_FLAG_OFFLINE | SV_INIT_FLAG_AUDIO_INT16 | SV_INIT_FLAG_ONE_THREAD
        with SunVox(sample_rate=44100, flags=flags) as sv:
            with sv.open_slot(0) as slot:
                slot.load(SAMPLE_SONG)
                original_name = slot.name
                original_bpm = slot.bpm

                # Save to memory
                data = slot.save_to_memory()
                assert data is not None
                assert len(data) > 0

                # Load back from memory in a new slot
                with sv.open_slot(1) as slot2:
                    slot2.load_from_memory(data)
                    assert slot2.name == original_name
                    assert slot2.bpm == original_bpm

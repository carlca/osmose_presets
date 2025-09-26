"""
Unit tests for the Preset model.

This module contains comprehensive tests for the Preset data model,
including validation, helper methods, and search functionality.
"""

import pytest
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.models.preset import Preset, PresetType


class TestPresetCreation:
   """Test Preset object creation and validation."""

   def test_valid_preset_creation(self):
      """Test creating a valid preset."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm", "analog"])

      assert preset.pack == "Factory"
      assert preset.type == "bass"
      assert preset.cc0 == 0
      assert preset.pgm == 1
      assert preset.preset == "Deep Bass"
      assert preset.chars == ["warm", "analog"]

   def test_preset_immutability(self):
      """Test that presets are immutable."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      with pytest.raises(AttributeError):
         preset.pack = "Modified"

   def test_invalid_cc0_value_too_high(self):
      """Test that invalid CC0 values raise an error."""
      with pytest.raises(ValueError, match="Invalid CC0 value: 128"):
         Preset(pack="Factory", type="bass", cc0=128, pgm=1, preset="Deep Bass")

   def test_invalid_cc0_value_negative(self):
      """Test that negative CC0 values raise an error."""
      with pytest.raises(ValueError, match="Invalid CC0 value: -1"):
         Preset(pack="Factory", type="bass", cc0=-1, pgm=1, preset="Deep Bass")

   def test_invalid_pgm_value_too_high(self):
      """Test that invalid program values raise an error."""
      with pytest.raises(ValueError, match="Invalid program value: 200"):
         Preset(pack="Factory", type="bass", cc0=0, pgm=200, preset="Deep Bass")

   def test_empty_pack_name(self):
      """Test that empty pack name raises an error."""
      with pytest.raises(ValueError, match="Pack name cannot be empty"):
         Preset(pack="", type="bass", cc0=0, pgm=1, preset="Deep Bass")

   def test_empty_preset_name(self):
      """Test that empty preset name raises an error."""
      with pytest.raises(ValueError, match="Preset name cannot be empty"):
         Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="")


class TestPresetProperties:
   """Test Preset property methods."""

   def test_preset_type_enum_valid(self):
      """Test getting valid preset type enum."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.preset_type_enum == PresetType.BASS

   def test_preset_type_enum_invalid(self):
      """Test preset type enum with unknown type."""
      preset = Preset(pack="Factory", type="unknown", cc0=0, pgm=1, preset="Unknown")

      assert preset.preset_type_enum is None

   def test_display_chars_with_chars(self):
      """Test display_chars property with characteristics."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm", "analog", "deep"])

      assert preset.display_chars == "warm, analog, deep"

   def test_display_chars_empty(self):
      """Test display_chars property with no characteristics."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.display_chars == ""

   def test_has_chars(self):
      """Test has_chars property."""
      preset_with = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm"])

      preset_without = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset_with.has_chars is True
      assert preset_without.has_chars is False

   def test_char_set(self):
      """Test char_set property."""
      preset = Preset(
         pack="Factory",
         type="bass",
         cc0=0,
         pgm=1,
         preset="Deep Bass",
         chars=["warm", "analog", "warm"],  # Duplicate to test set conversion
      )

      assert preset.char_set == {"warm", "analog"}


class TestPresetSearch:
   """Test preset search functionality."""

   def test_simple_search(self):
      """Test simple search without operators."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass Groove")

      assert preset.matches_search("Bass") is True
      assert preset.matches_search("Deep") is True
      assert preset.matches_search("Groove") is True
      assert preset.matches_search("Piano") is False

   def test_case_insensitive_search(self):
      """Test that search is case-insensitive."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_search("DEEP") is True
      assert preset.matches_search("bass") is True
      assert preset.matches_search("DeEp BaSs") is True

   def test_search_with_and_operator(self):
      """Test search with AND operator."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass Groove")

      assert preset.matches_search("Deep AND Bass") is True
      assert preset.matches_search("Deep AND Groove") is True
      assert preset.matches_search("Deep AND Piano") is False

   def test_search_with_or_operator(self):
      """Test search with OR operator."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_search("Deep OR Piano") is True
      assert preset.matches_search("Piano OR Guitar") is False
      assert preset.matches_search("Piano OR Bass") is True

   def test_search_with_combined_operators(self):
      """Test search with AND and OR operators (AND has precedence)."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass Groove")

      # (Deep AND Bass) OR (Piano AND Keys)
      assert preset.matches_search("Deep AND Bass OR Piano AND Keys") is True
      # (Deep AND Piano) OR (Bass AND Groove)
      assert preset.matches_search("Deep AND Piano OR Bass AND Groove") is True
      # (Piano AND Keys) OR (Guitar AND Amp)
      assert preset.matches_search("Piano AND Keys OR Guitar AND Amp") is False

   def test_empty_search(self):
      """Test that empty search returns True."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_search("") is True


class TestPresetFilters:
   """Test preset filter methods."""

   def test_pack_filter(self):
      """Test pack filter matching."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_pack_filter({"Factory", "User"}) is True
      assert preset.matches_pack_filter({"User", "Custom"}) is False
      assert preset.matches_pack_filter(set()) is True  # Empty filter matches all

   def test_type_filter(self):
      """Test type filter matching."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_type_filter({"bass", "lead"}) is True
      assert preset.matches_type_filter({"lead", "pads"}) is False
      assert preset.matches_type_filter(set()) is True  # Empty filter matches all

   def test_char_filter(self):
      """Test character filter matching."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm", "analog", "deep"])

      assert preset.matches_char_filter({"warm", "digital"}) is True
      assert preset.matches_char_filter({"analog"}) is True
      assert preset.matches_char_filter({"digital", "cold"}) is False
      assert preset.matches_char_filter(set()) is True  # Empty filter matches all

   def test_char_filter_no_chars(self):
      """Test character filter with preset that has no chars."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      assert preset.matches_char_filter({"warm"}) is False
      assert preset.matches_char_filter(set()) is True


class TestPresetSerialization:
   """Test preset serialization methods."""

   def test_to_dict(self):
      """Test converting preset to dictionary."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm", "analog"])

      result = preset.to_dict()

      assert result == {"pack": "Factory", "type": "bass", "cc0": 0, "pgm": 1, "preset": "Deep Bass", "chars": ["warm", "analog"]}

   def test_from_dict(self):
      """Test creating preset from dictionary."""
      data = {"pack": "Factory", "type": "bass", "cc0": 0, "pgm": 1, "preset": "Deep Bass", "chars": ["warm", "analog"]}

      preset = Preset.from_dict(data)

      assert preset.pack == "Factory"
      assert preset.type == "bass"
      assert preset.cc0 == 0
      assert preset.pgm == 1
      assert preset.preset == "Deep Bass"
      assert preset.chars == ["warm", "analog"]

   def test_from_dict_missing_optional(self):
      """Test creating preset from dictionary without optional fields."""
      data = {"pack": "Factory", "type": "bass", "cc0": 0, "pgm": 1, "preset": "Deep Bass"}

      preset = Preset.from_dict(data)

      assert preset.chars == []

   def test_from_dict_missing_required(self):
      """Test that missing required fields raise an error."""
      data = {
         "pack": "Factory",
         "type": "bass",
         "cc0": 0,
         # Missing pgm
         "preset": "Deep Bass",
      }

      with pytest.raises(KeyError):
         Preset.from_dict(data)

   def test_to_tuple(self):
      """Test converting preset to tuple for display."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm", "analog"])

      result = preset.to_tuple()

      assert result == ("Factory", "bass", 0, 1, "Deep Bass", "warm, analog")


class TestPresetStringRepresentations:
   """Test preset string representations."""

   def test_str_representation(self):
      """Test __str__ method."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass")

      result = str(preset)

      assert result == "Preset(Factory/Deep Bass - CC0:0, PGM:1)"

   def test_repr_representation(self):
      """Test __repr__ method."""
      preset = Preset(pack="Factory", type="bass", cc0=0, pgm=1, preset="Deep Bass", chars=["warm"])

      result = repr(preset)

      expected = "Preset(pack='Factory', type='bass', cc0=0, pgm=1, preset='Deep Bass', chars=['warm'])"
      assert result == expected


class TestPresetType:
   """Test PresetType enum."""

   def test_preset_type_values(self):
      """Test that all preset types are defined."""
      types = PresetType.get_display_values()

      expected = ["bass", "bowed", "brass", "elec piano", "flute reeds", "keys", "lead", "mallets", "organ", "pads", "perc", "plucked", "sfx"]

      assert sorted(types) == sorted(expected)

   def test_from_string_valid(self):
      """Test creating PresetType from valid string."""
      assert PresetType.from_string("bass") == PresetType.BASS
      assert PresetType.from_string("elec piano") == PresetType.ELEC_PIANO
      assert PresetType.from_string("BASS") == PresetType.BASS  # Case insensitive

   def test_from_string_invalid(self):
      """Test creating PresetType from invalid string."""
      assert PresetType.from_string("invalid") is None
      assert PresetType.from_string("") is None


if __name__ == "__main__":
   # Run tests with pytest
   pytest.main([__file__, "-v"])

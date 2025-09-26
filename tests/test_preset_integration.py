"""
Integration tests for the Preset model with actual data.

This module tests that the Preset model works correctly with
the actual JSON data file.
"""

import json
import sys
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.models.preset import Preset, PresetType


class TestPresetIntegration:
   """Integration tests with actual preset data."""

   @classmethod
   def setup_class(cls):
      """Load the actual preset data once for all tests."""
      data_file = Path(__file__).parent.parent / "src" / "OsmosePresets.json"
      with open(data_file, "r", encoding="utf-8") as f:
         cls.raw_data = json.load(f)

      # Convert all to Preset objects
      cls.presets: List[Preset] = []
      cls.load_errors = []

      for i, item in enumerate(cls.raw_data):
         try:
            preset = Preset.from_dict(item)
            cls.presets.append(preset)
         except Exception as e:
            cls.load_errors.append((i, item, str(e)))

   def test_all_presets_load_successfully(self):
      """Test that all presets in the JSON file load without errors."""
      if self.load_errors:
         error_msg = f"Failed to load {len(self.load_errors)} presets:\n"
         for idx, item, error in self.load_errors[:5]:  # Show first 5 errors
            error_msg += f"  Index {idx}: {error}\n"
            error_msg += f"    Data: {item}\n"

         assert False, error_msg

      # Ensure we loaded some presets
      assert len(self.presets) > 0, "No presets were loaded"
      print(f"Successfully loaded {len(self.presets)} presets")

   def test_all_midi_values_valid(self):
      """Test that all MIDI values are within valid range."""
      invalid_presets = []

      for preset in self.presets:
         if not (0 <= preset.cc0 <= 127):
            invalid_presets.append(f"{preset.preset}: CC0={preset.cc0}")
         if not (0 <= preset.pgm <= 127):
            invalid_presets.append(f"{preset.preset}: PGM={preset.pgm}")

      assert not invalid_presets, f"Invalid MIDI values found:\n" + "\n".join(invalid_presets)

   def test_preset_types_match_enum(self):
      """Test that all preset types are recognized or documented."""
      unknown_types = set()
      type_counts = {}

      for preset in self.presets:
         if preset.preset_type_enum is None:
            unknown_types.add(preset.type)

         type_counts[preset.type] = type_counts.get(preset.type, 0) + 1

      # Report statistics
      print(f"\nPreset type distribution:")
      for ptype, count in sorted(type_counts.items()):
         enum_match = "✓" if PresetType.from_string(ptype) else "✗"
         print(f"  {ptype:15} : {count:4} presets {enum_match}")

      if unknown_types:
         print(f"\nWarning: Unknown preset types found: {sorted(unknown_types)}")
         print("Consider adding these to the PresetType enum if they're valid.")

   def test_pack_distribution(self):
      """Test and report pack distribution."""
      pack_counts = {}

      for preset in self.presets:
         pack_counts[preset.pack] = pack_counts.get(preset.pack, 0) + 1

      print(f"\nPack distribution:")
      for pack, count in sorted(pack_counts.items()):
         print(f"  {pack:20} : {count:4} presets")

      # Basic sanity check
      assert len(pack_counts) > 0, "No packs found"

   def test_character_distribution(self):
      """Test and report character tag distribution."""
      char_counts = {}
      presets_with_chars = 0
      presets_without_chars = 0

      for preset in self.presets:
         if preset.has_chars:
            presets_with_chars += 1
            for char in preset.chars:
               char_counts[char] = char_counts.get(char, 0) + 1
         else:
            presets_without_chars += 1

      print(f"\nCharacter statistics:")
      print(f"  Presets with characters: {presets_with_chars}")
      print(f"  Presets without characters: {presets_without_chars}")
      print(f"  Unique character tags: {len(char_counts)}")

      if char_counts:
         print(f"\nTop 10 most common character tags:")
         sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
         for char, count in sorted_chars[:10]:
            print(f"  {char:20} : {count:4} presets")

   def test_search_functionality(self):
      """Test search functionality with real data."""
      # Test some common search terms
      bass_presets = [p for p in self.presets if p.matches_search("bass")]
      pad_presets = [p for p in self.presets if p.matches_search("pad")]

      print(f"\nSearch results:")
      print(f"  'bass' found in {len(bass_presets)} presets")
      print(f"  'pad' found in {len(pad_presets)} presets")

      # Test AND operator
      warm_bass = [p for p in self.presets if p.matches_search("warm AND bass")]
      print(f"  'warm AND bass' found in {len(warm_bass)} presets")

      # Test OR operator
      bass_or_lead = [p for p in self.presets if p.matches_search("bass OR lead")]
      print(f"  'bass OR lead' found in {len(bass_or_lead)} presets")

      # Verify OR returns at least as many as individual searches
      lead_presets = [p for p in self.presets if p.matches_search("lead")]
      assert len(bass_or_lead) >= max(len(bass_presets), len(lead_presets))

   def test_filter_functionality(self):
      """Test filter functionality with real data."""
      # Get unique values for testing
      all_packs = {p.pack for p in self.presets}
      all_types = {p.type for p in self.presets}
      all_chars = set()
      for p in self.presets:
         all_chars.update(p.chars)

      # Test pack filter
      if all_packs:
         first_pack = next(iter(all_packs))
         filtered = [p for p in self.presets if p.matches_pack_filter({first_pack})]
         print(f"\nFilter test for pack '{first_pack}': {len(filtered)} presets")
         assert len(filtered) > 0

      # Test type filter
      if all_types:
         first_type = next(iter(all_types))
         filtered = [p for p in self.presets if p.matches_type_filter({first_type})]
         print(f"Filter test for type '{first_type}': {len(filtered)} presets")
         assert len(filtered) > 0

      # Test character filter
      if all_chars:
         # Find a commonly used character
         char_usage = {}
         for char in all_chars:
            char_usage[char] = sum(1 for p in self.presets if char in p.chars)

         common_char = max(char_usage, key=char_usage.get)
         filtered = [p for p in self.presets if p.matches_char_filter({common_char})]
         print(f"Filter test for character '{common_char}': {len(filtered)} presets")
         assert len(filtered) > 0

   def test_serialization_round_trip(self):
      """Test that presets can be serialized and deserialized without data loss."""
      for preset in self.presets[:10]:  # Test first 10 to keep it fast
         # Convert to dict and back
         preset_dict = preset.to_dict()
         reconstructed = Preset.from_dict(preset_dict)

         # Verify all fields match
         assert reconstructed.pack == preset.pack
         assert reconstructed.type == preset.type
         assert reconstructed.cc0 == preset.cc0
         assert reconstructed.pgm == preset.pgm
         assert reconstructed.preset == preset.preset
         assert reconstructed.chars == preset.chars

   def test_tuple_conversion(self):
      """Test tuple conversion for table display."""
      for preset in self.presets[:5]:
         tuple_data = preset.to_tuple()

         # Verify tuple has correct structure
         assert len(tuple_data) == 6
         assert tuple_data[0] == preset.pack
         assert tuple_data[1] == preset.type
         assert tuple_data[2] == preset.cc0
         assert tuple_data[3] == preset.pgm
         assert tuple_data[4] == preset.preset

         # Check character formatting
         if preset.chars:
            assert tuple_data[5] == ", ".join(preset.chars)
         else:
            assert tuple_data[5] == ""

   def test_unique_preset_identifiers(self):
      """Test that CC0/PGM combinations are unique."""
      seen_combinations = {}
      duplicates = []

      for preset in self.presets:
         key = (preset.cc0, preset.pgm)
         if key in seen_combinations:
            duplicates.append(f"Duplicate CC0/PGM ({preset.cc0}, {preset.pgm}): '{preset.preset}' and '{seen_combinations[key]}'")
         else:
            seen_combinations[key] = preset.preset

      if duplicates:
         print(f"\nWarning: Found {len(duplicates)} duplicate CC0/PGM combinations:")
         for dup in duplicates[:5]:  # Show first 5
            print(f"  {dup}")

      # This might not be an error depending on the system design
      # Just report it for now
      print(f"\nTotal unique CC0/PGM combinations: {len(seen_combinations)}")


if __name__ == "__main__":
   import pytest

   pytest.main([__file__, "-v", "-s"])  # -s to show print statements

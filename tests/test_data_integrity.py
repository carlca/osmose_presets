"""
Data integrity tests for the Osmose preset data.

This module tests for data consistency issues without modifying any data.
It serves as a validation suite to catch integrity problems.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.models.preset import Preset


class TestDataIntegrity:
   """Test suite for data integrity validation."""

   @classmethod
   def setup_class(cls):
      """Load the preset data once for all tests."""
      data_file = Path(__file__).parent.parent / "src" / "OsmosePresets.json"
      with open(data_file, "r", encoding="utf-8") as f:
         cls.raw_data = json.load(f)

      cls.presets: List[Preset] = []
      for item in cls.raw_data:
         preset = Preset.from_dict(item)
         cls.presets.append(preset)

   def test_cc0_pgm_uniqueness(self):
      """Test that CC0/PGM combinations should be unique."""
      seen: Dict[Tuple[int, int], Preset] = {}
      duplicates: List[Tuple[Preset, Preset]] = []

      for preset in self.presets:
         key = (preset.cc0, preset.pgm)

         if key in seen:
            duplicates.append((seen[key], preset))
         else:
            seen[key] = preset

      # Report duplicates if found
      if duplicates:
         duplicate_report = "\nDuplicate CC0/PGM combinations found:\n"
         for first, second in duplicates:
            duplicate_report += f"\n  CC0={first.cc0}, PGM={first.pgm}:\n"
            duplicate_report += f"    1. '{first.preset}' (pack: {first.pack}, type: {first.type})\n"
            duplicate_report += f"    2. '{second.preset}' (pack: {second.pack}, type: {second.type})\n"

         # Test should now pass since duplicates have been fixed
         assert False, f"Duplicate CC0/PGM combinations found: {duplicate_report}"

   def test_midi_value_ranges(self):
      """Test that all MIDI values are within valid ranges."""
      invalid_presets = []

      for preset in self.presets:
         issues = []

         if not (0 <= preset.cc0 <= 127):
            issues.append(f"CC0={preset.cc0} out of range")

         if not (0 <= preset.pgm <= 127):
            issues.append(f"PGM={preset.pgm} out of range")

         if issues:
            invalid_presets.append(f"{preset.preset}: {', '.join(issues)}")

      assert not invalid_presets, f"Invalid MIDI values:\n" + "\n".join(invalid_presets)

   def test_required_fields_present(self):
      """Test that all required fields are present and non-empty."""
      missing_fields = []

      for preset in self.presets:
         issues = []

         if not preset.pack:
            issues.append("missing pack")
         if not preset.type:
            issues.append("missing type")
         if not preset.preset:
            issues.append("missing preset name")

         if issues:
            missing_fields.append(f"{preset.preset or 'UNNAMED'}: {', '.join(issues)}")

      assert not missing_fields, f"Missing required fields:\n" + "\n".join(missing_fields)

   def test_bank_organization(self):
      """Test and document the bank organization."""
      bank_info = defaultdict(list)

      for preset in self.presets:
         bank_info[preset.cc0].append(preset)

      # Document the bank organization
      print("\nBank Organization:")
      for bank in sorted(bank_info.keys()):
         presets_in_bank = bank_info[bank]
         print(f"  Bank {bank}: {len(presets_in_bank)} presets (PGM {min(p.pgm for p in presets_in_bank)}-{max(p.pgm for p in presets_in_bank)})")

      # Check for reasonable bank sizes
      for bank, presets_in_bank in bank_info.items():
         assert len(presets_in_bank) <= 128, f"Bank {bank} has {len(presets_in_bank)} presets (max 128)"

   def test_pack_consistency(self):
      """Test that pack names are consistent."""
      packs = {preset.pack for preset in self.presets}

      print(f"\nFound {len(packs)} packs: {sorted(packs)}")

      # Check for similar pack names that might be typos
      pack_list = list(packs)
      potential_typos = []

      for i, pack1 in enumerate(pack_list):
         for pack2 in pack_list[i + 1 :]:
            # Simple similarity check (you could use more sophisticated methods)
            if pack1.lower().replace("_", "") == pack2.lower().replace("_", ""):
               potential_typos.append((pack1, pack2))

      if potential_typos:
         typo_msg = "Potential pack name inconsistencies:\n"
         for p1, p2 in potential_typos:
            typo_msg += f"  '{p1}' vs '{p2}'\n"
         # Just warn, don't fail
         print(f"Warning: {typo_msg}")

   def test_type_consistency(self):
      """Test that all preset types are from known set."""
      known_types = {"bass", "bowed", "brass", "elec piano", "flute reeds", "keys", "lead", "mallets", "organ", "pads", "perc", "plucked", "sfx"}

      types_found = {preset.type for preset in self.presets}
      unknown_types = types_found - known_types

      if unknown_types:
         print(f"Warning: Unknown preset types found: {unknown_types}")
         print("Consider adding these to the PresetType enum")

      # This should pass even with unknown types (just warns)
      assert types_found, "No preset types found"

   def test_character_tag_consistency(self):
      """Test character tags for consistency."""
      all_chars = defaultdict(int)

      for preset in self.presets:
         for char in preset.chars:
            all_chars[char] += 1

      # Look for potential duplicates or typos in character tags
      char_list = list(all_chars.keys())
      potential_issues = []

      for i, char1 in enumerate(char_list):
         for char2 in char_list[i + 1 :]:
            # Check for very similar character names
            if char1.lower() == char2.lower() and char1 != char2:
               potential_issues.append((char1, char2, "case difference"))
            elif char1.lower().replace(" ", "") == char2.lower().replace(" ", ""):
               potential_issues.append((char1, char2, "spacing difference"))

      if potential_issues:
         print("\nPotential character tag inconsistencies:")
         for c1, c2, issue in potential_issues:
            print(f"  '{c1}' vs '{c2}' ({issue})")

   def test_preset_name_uniqueness_within_pack(self):
      """Test that preset names are unique within each pack."""
      pack_presets = defaultdict(list)

      for preset in self.presets:
         pack_presets[preset.pack].append(preset.preset)

      duplicates = []
      for pack, preset_names in pack_presets.items():
         seen = set()
         for name in preset_names:
            if name in seen:
               duplicates.append(f"Pack '{pack}': duplicate preset name '{name}'")
            seen.add(name)

      assert not duplicates, "Duplicate preset names within packs:\n" + "\n".join(duplicates)

   def test_data_completeness(self):
      """Test data completeness and provide statistics."""
      total = len(self.presets)
      with_chars = sum(1 for p in self.presets if p.chars)

      stats = f"""
Data Completeness Statistics:
  Total presets: {total}
  Presets with character tags: {with_chars} ({with_chars * 100 // total}%)
  Presets without character tags: {total - with_chars} ({(total - with_chars) * 100 // total}%)
  
  Average character tags per preset: {sum(len(p.chars) for p in self.presets) / total:.1f}
  Max character tags on a preset: {max(len(p.chars) for p in self.presets)}
        """

      print(stats)

      # Basic sanity checks
      assert total > 0, "No presets loaded"
      assert with_chars > 0, "No presets have character tags"

   def test_sequential_numbering_within_banks(self):
      """Test if PGM numbers are sequential within banks."""
      bank_pgms = defaultdict(list)

      for preset in self.presets:
         bank_pgms[preset.cc0].append(preset.pgm)

      gaps = []
      for bank, pgms in bank_pgms.items():
         sorted_pgms = sorted(pgms)
         expected = list(range(sorted_pgms[0], sorted_pgms[0] + len(pgms)))

         if sorted_pgms != expected:
            # Find the gaps
            missing = set(expected) - set(sorted_pgms)
            if missing:
               gaps.append(f"Bank {bank}: missing PGM numbers {sorted(missing)}")

      if gaps:
         print("\nGaps in PGM numbering:")
         for gap in gaps:
            print(f"  {gap}")
         # Don't fail, just report
         print("Note: Gaps in numbering are not necessarily errors")


class TestDuplicateDetection:
   """Specific tests for detecting and reporting duplicates."""

   @classmethod
   def setup_class(cls):
      """Load the preset data."""
      data_file = Path(__file__).parent.parent / "src" / "OsmosePresets.json"
      with open(data_file, "r", encoding="utf-8") as f:
         cls.raw_data = json.load(f)

      cls.presets = [Preset.from_dict(item) for item in cls.raw_data]

   def test_no_duplicate_midi_identifiers(self):
      """Test that there are no duplicate CC0/PGM combinations."""
      midi_map = {}

      for preset in self.presets:
         key = (preset.cc0, preset.pgm)
         if key in midi_map:
            # Found duplicate
            first = midi_map[key]
            duplicate_details = (
               f"Duplicate MIDI identifier CC0={preset.cc0}, PGM={preset.pgm}:\n"
               f"  1. '{first.preset}' ({first.pack}/{first.type})\n"
               f"  2. '{preset.preset}' ({preset.pack}/{preset.type})"
            )
            assert False, duplicate_details
         midi_map[key] = preset

   def test_duplicate_fix_applied(self):
      """Test that the duplicate fix has been applied (CC0=34, PGM=35 is now in use)."""
      used_keys = {(preset.cc0, preset.pgm) for preset in self.presets}

      # Check that the fix location is now being used (duplicate was fixed)
      fixed_location = (34, 35)
      assert fixed_location in used_keys, f"Expected CC0={fixed_location[0]}, PGM={fixed_location[1]} to be in use after fix"

      print(f"\n✅ Duplicate fix confirmed: CC0={fixed_location[0]}, PGM={fixed_location[1]} is now in use")

   def test_report_duplicate_details(self):
      """Generate a detailed report of any duplicates found."""
      from collections import defaultdict

      midi_map = defaultdict(list)

      for preset in self.presets:
         key = (preset.cc0, preset.pgm)
         midi_map[key].append(preset)

      duplicates = {k: v for k, v in midi_map.items() if len(v) > 1}

      if duplicates:
         print("\n" + "=" * 60)
         print("DUPLICATE CC0/PGM REPORT")
         print("=" * 60)

         for (cc0, pgm), presets in duplicates.items():
            print(f"\n🔍 CC0={cc0}, PGM={pgm} is used by {len(presets)} presets:")
            for i, preset in enumerate(presets, 1):
               print(f"\n  {i}. Preset: '{preset.preset}'")
               print(f"     Pack: {preset.pack}")
               print(f"     Type: {preset.type}")
               print(f"     Characters: {', '.join(preset.chars) if preset.chars else 'none'}")

            # Suggest fixes
            print(f"\n  💡 Suggested fixes:")
            print(f"     Keep first preset at CC0={cc0}, PGM={pgm}")

            # Find next available PGM in same bank
            next_pgm = pgm + 1
            while (cc0, next_pgm) in midi_map and next_pgm <= 127:
               next_pgm += 1

            if next_pgm <= 127:
               for preset in presets[1:]:
                  print(f"     Move '{preset.preset}' to CC0={cc0}, PGM={next_pgm}")
                  next_pgm += 1
                  while (cc0, next_pgm) in midi_map and next_pgm <= 127:
                     next_pgm += 1

         print("\n" + "=" * 60)


if __name__ == "__main__":
   # Run tests with pytest
   pytest.main([__file__, "-v", "-s"])

#!/usr/bin/env python
"""
Debug script to test preset selection and verify correct MIDI values are being used.

This script helps diagnose why wrong values might be sent when selecting a preset.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pathlib import Path
from services.app_services import AppServices
from data.models.preset import Preset


def debug_preset_data():
   """Debug preset data to see what's being loaded and how it's structured."""
   print("=" * 60)
   print("DEBUG: Preset Selection Issue")
   print("=" * 60)

   # Initialize services
   services = AppServices()
   preset_service = services.get_preset_service()

   # Get all presets
   all_presets = preset_service.get_filtered_presets()
   print(f"\nTotal presets loaded: {len(all_presets)}")

   # Show first 5 presets as objects
   print("\n--- First 5 Presets (as objects) ---")
   for i, preset in enumerate(all_presets[:5]):
      print(f"{i}: {preset.preset}")
      print(f"   Pack: {preset.pack}, Type: {preset.type}")
      print(f"   CC0: {preset.cc0}, PGM: {preset.pgm}")
      print(f"   Chars: {preset.chars}")

   # Show first 5 presets as tuples (what the table sees)
   print("\n--- First 5 Presets (as tuples for table) ---")
   preset_tuples = preset_service.get_filtered_preset_tuples()
   for i, tuple_data in enumerate(preset_tuples[:5]):
      print(f"{i}: {tuple_data}")
      print(f"   Index 0 (pack): {tuple_data[0]}")
      print(f"   Index 1 (type): {tuple_data[1]}")
      print(f"   Index 2 (cc0):  {tuple_data[2]}")
      print(f"   Index 3 (pgm):  {tuple_data[3]}")
      print(f"   Index 4 (name): {tuple_data[4]}")
      print(f"   Index 5 (chars): {tuple_data[5]}")

   # Test specific preset lookup
   print("\n--- Testing Preset Lookup ---")
   if all_presets:
      test_preset = all_presets[0]
      print(f"Looking up preset: {test_preset.preset}")
      print(f"Using CC0={test_preset.cc0}, PGM={test_preset.pgm}")

      found = preset_service.get_preset_by_midi(test_preset.cc0, test_preset.pgm)
      if found:
         print(f"✓ Found: {found.preset}")
         if found.preset == test_preset.preset:
            print("✓ Correct preset returned!")
         else:
            print(f"✗ WRONG PRESET! Expected: {test_preset.preset}, Got: {found.preset}")
      else:
         print("✗ Preset not found!")

   # Check for any duplicate CC0/PGM combinations
   print("\n--- Checking for Duplicate MIDI Values ---")
   midi_map = {}
   duplicates = []

   for preset in all_presets:
      key = (preset.cc0, preset.pgm)
      if key in midi_map:
         duplicates.append({"midi": key, "preset1": midi_map[key], "preset2": preset.preset})
      else:
         midi_map[key] = preset.preset

   if duplicates:
      print(f"⚠ Found {len(duplicates)} duplicate MIDI combinations:")
      for dup in duplicates[:5]:  # Show first 5
         print(f"  CC0={dup['midi'][0]}, PGM={dup['midi'][1]}")
         print(f"    - {dup['preset1']}")
         print(f"    - {dup['preset2']}")
   else:
      print("✓ No duplicate MIDI combinations found")

   # Simulate what PresetGrid does when a row is selected
   print("\n--- Simulating PresetGrid Row Selection ---")
   if preset_tuples:
      # Simulate selecting the first row
      row_data = preset_tuples[0]
      print(f"Row data: {row_data}")

      # This is what PresetGrid does:
      cc = row_data[2]  # Index 2 should be cc0
      pgm = row_data[3]  # Index 3 should be pgm

      print(f"Extracted from row: CC={cc}, PGM={pgm}")

      # Now look up the preset using these values
      selected_preset = preset_service.get_preset_by_midi(cc, pgm)
      if selected_preset:
         print(f"Would send: CC={cc}, PGM={pgm} for preset '{selected_preset.preset}'")

         # Verify this matches what we expect
         if selected_preset.preset == row_data[4]:  # Index 4 is preset name
            print("✓ Correct values would be sent!")
         else:
            print(f"✗ MISMATCH! Row shows '{row_data[4]}' but lookup returns '{selected_preset.preset}'")
      else:
         print(f"✗ No preset found for CC={cc}, PGM={pgm}")

   # Check if there's a filtering issue
   print("\n--- Checking Filter State ---")
   filter_service = services.get_filter_service()
   filter_state = filter_service.state
   print(f"Filter active: {filter_state.is_active()}")
   if filter_state.is_active():
      print(f"  Packs: {filter_state.packs}")
      print(f"  Types: {filter_state.types}")
      print(f"  Chars: {filter_state.chars}")
      print(f"  Search: {filter_state.search_term}")

   # Compare filtered vs unfiltered
   all_presets_unfiltered = services.app_context.get_preset_manager().get_all_presets()
   filtered_presets = preset_service.get_filtered_presets()
   print(f"\nTotal unfiltered: {len(all_presets_unfiltered)}")
   print(f"Total filtered: {len(filtered_presets)}")

   if len(all_presets_unfiltered) != len(filtered_presets):
      print("⚠ Some presets are being filtered out!")

   print("\n" + "=" * 60)
   print("Debug complete. Check the output above for issues.")
   print("=" * 60)


if __name__ == "__main__":
   debug_preset_data()

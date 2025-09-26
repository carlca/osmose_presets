#!/usr/bin/env python
"""
Simple test to verify preset selection is working correctly.
Run this to see what's happening with preset selection.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from services.app_services import AppServices


def main():
   print("Testing Preset Selection Values")
   print("=" * 60)

   # Initialize services
   services = AppServices()
   preset_service = services.get_preset_service()
   filter_service = services.get_filter_service()

   # Show initial filter state
   print("\nInitial filter state:")
   print(f"  Filters active: {filter_service.state.is_active()}")
   print(f"  Packs: {filter_service.state.packs}")
   print(f"  Types: {filter_service.state.types}")
   print(f"  Chars: {filter_service.state.chars}")

   # Get presets as tuples (what the table shows)
   preset_tuples = preset_service.get_filtered_preset_tuples()
   print(f"\nTotal presets in table: {len(preset_tuples)}")

   # Show first 5 presets as they appear in the table
   print("\nFirst 5 presets in table:")
   print("-" * 60)
   for i in range(min(5, len(preset_tuples))):
      row = preset_tuples[i]
      print(f"Row {i}:")
      print(f"  Pack:   {row[0]}")
      print(f"  Type:   {row[1]}")
      print(f"  CC0:    {row[2]} (index 2)")
      print(f"  PGM:    {row[3]} (index 3)")
      print(f"  Preset: {row[4]}")
      print(f"  Chars:  {row[5]}")

      # This is what PresetGrid does when you click this row:
      cc = row[2]
      pgm = row[3]
      print(f"  → Would send: CC0={cc}, PGM={pgm}")

      # Verify this is correct
      found = preset_service.get_preset_by_midi(cc, pgm)
      if found:
         if found.preset == row[4]:
            print(f"  ✓ Correct! Would select: '{found.preset}'")
         else:
            print(f"  ✗ ERROR! Row shows '{row[4]}' but would select '{found.preset}'")
      else:
         print(f"  ✗ ERROR! No preset found for CC0={cc}, PGM={pgm}")
      print()

   # Test with some filters applied
   print("\nTesting with filters...")
   print("-" * 60)

   # Get available packs
   packs = preset_service.get_available_packs()
   if packs:
      # Apply a pack filter
      test_pack = packs[0]
      filter_service.set_pack_filter({test_pack})
      print(f"Applied pack filter: {test_pack}")

      # Get filtered results
      filtered_tuples = preset_service.get_filtered_preset_tuples()
      print(f"Filtered results: {len(filtered_tuples)} presets")

      if filtered_tuples:
         # Check first filtered result
         row = filtered_tuples[0]
         print(f"\nFirst filtered preset:")
         print(f"  Pack:   {row[0]}")
         print(f"  Type:   {row[1]}")
         print(f"  CC0:    {row[2]}")
         print(f"  PGM:    {row[3]}")
         print(f"  Preset: {row[4]}")

         # Verify selection would work
         cc = row[2]
         pgm = row[3]
         found = preset_service.get_preset_by_midi(cc, pgm)
         if found and found.preset == row[4]:
            print(f"  ✓ Selection would work correctly!")
         else:
            print(f"  ✗ Selection would be WRONG!")

      # Clear filter
      filter_service.clear_filters()

   print("\n" + "=" * 60)
   print("Test complete. Check results above.")


if __name__ == "__main__":
   main()

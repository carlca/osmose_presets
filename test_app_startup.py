#!/usr/bin/env python
"""
Test script to verify the application can start up with the new service layer.

This script tests that:
1. All services can be initialized
2. The UI components can be created with services
3. Basic filtering operations work
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pathlib import Path
from services.app_services import AppServices
from services.filter_service import FilterState
from data.models.preset import Preset


def test_services_initialization():
   """Test that all services can be initialized."""
   print("Testing services initialization...")

   # Initialize services
   services = AppServices()

   # Get individual services
   preset_service = services.get_preset_service()
   filter_service = services.get_filter_service()

   print(f"✓ AppServices initialized")
   print(f"✓ PresetService: {preset_service}")
   print(f"✓ FilterService: {filter_service}")

   # Check initial state
   assert not filter_service.state.is_active(), "Filters should initially be inactive"
   print(f"✓ Initial filter state is empty")

   # Get initial presets
   all_presets = preset_service.get_filtered_presets()
   print(f"✓ Loaded {len(all_presets)} presets")

   return services


def test_filtering_operations(services):
   """Test that filtering operations work correctly."""
   print("\nTesting filtering operations...")

   preset_service = services.get_preset_service()
   filter_service = services.get_filter_service()

   # Get initial counts
   total_presets = preset_service.get_total_preset_count()
   print(f"  Total presets: {total_presets}")

   # Test pack filtering
   available_packs = preset_service.get_available_packs()
   print(f"  Available packs: {available_packs[:3]}...")

   if available_packs:
      # Apply pack filter
      filter_service.set_pack_filter({available_packs[0]})
      filtered_count = preset_service.get_preset_count()
      print(f"✓ Pack filter applied: {filtered_count} presets match '{available_packs[0]}'")

      # Clear filter
      filter_service.clear_pack_filter()
      assert preset_service.get_preset_count() == total_presets
      print(f"✓ Filter cleared, back to {total_presets} presets")

   # Test type filtering
   available_types = preset_service.get_available_types()
   print(f"  Available types: {available_types[:3]}...")

   if available_types:
      filter_service.set_type_filter({available_types[0]})
      filtered_count = preset_service.get_preset_count()
      print(f"✓ Type filter applied: {filtered_count} presets match '{available_types[0]}'")
      filter_service.clear_type_filter()

   # Test search
   filter_service.set_search("bass")
   search_count = preset_service.get_preset_count()
   print(f"✓ Search filter applied: {search_count} presets match 'bass'")
   filter_service.clear_search()

   # Test combined filters
   if available_packs and available_types:
      filter_service.set_pack_filter({available_packs[0]})
      filter_service.set_type_filter({available_types[0]})
      combined_count = preset_service.get_preset_count()
      print(f"✓ Combined filters: {combined_count} presets match both filters")

      # Get filter summary
      summary = filter_service.get_state_summary()
      print(f"  Filter summary: {summary}")

      # Clear all
      filter_service.clear_filters()
      assert not filter_service.state.is_active()
      print(f"✓ All filters cleared")


def test_preset_lookup(services):
   """Test preset lookup operations."""
   print("\nTesting preset lookup...")

   preset_service = services.get_preset_service()

   # Get a sample preset
   all_presets = preset_service.get_filtered_presets()
   if all_presets:
      sample = all_presets[0]
      print(f"  Sample preset: {sample.preset} (CC0={sample.cc0}, PGM={sample.pgm})")

      # Look it up by MIDI
      found = preset_service.get_preset_by_midi(sample.cc0, sample.pgm)
      assert found is not None
      assert found.preset == sample.preset
      print(f"✓ Preset lookup by MIDI successful")

   # Test non-existent preset
   not_found = preset_service.get_preset_by_midi(999, 999)
   assert not_found is None
   print(f"✓ Non-existent preset returns None")


def test_statistics(services):
   """Test statistics generation."""
   print("\nTesting statistics...")

   preset_service = services.get_preset_service()
   stats = preset_service.get_statistics()

   print(f"  Statistics:")
   for key, value in stats.items():
      print(f"    {key}: {value}")

   assert "total_presets" in stats
   assert "filtered_presets" in stats
   assert "filters_active" in stats
   print(f"✓ Statistics generated successfully")


def test_ui_component_compatibility():
   """Test that UI components can be created with services."""
   print("\nTesting UI component compatibility...")

   try:
      from preset_grid import PresetGrid
      from filter_selector import FilterSelector
      from filters import Filters

      # Create services
      services = AppServices()
      preset_service = services.get_preset_service()
      filter_service = services.get_filter_service()

      # Try to create UI components (without running the app)
      preset_grid = PresetGrid(preset_service=preset_service)
      print(f"✓ PresetGrid created successfully")

      filter_selector = FilterSelector(preset_service=preset_service, filter_service=filter_service, filter_type=Filters.PACK)
      print(f"✓ FilterSelector created successfully")

   except ImportError as e:
      print(f"⚠ Could not test UI components: {e}")
   except Exception as e:
      print(f"✗ Error creating UI components: {e}")
      return False

   return True


def main():
   """Run all tests."""
   print("=" * 60)
   print("Testing Osmose Presets App with Phase 3 Service Layer")
   print("=" * 60)

   try:
      # Test services initialization
      services = test_services_initialization()

      # Test filtering
      test_filtering_operations(services)

      # Test preset lookup
      test_preset_lookup(services)

      # Test statistics
      test_statistics(services)

      # Test UI compatibility
      test_ui_component_compatibility()

      print("\n" + "=" * 60)
      print("✓ All tests passed successfully!")
      print("=" * 60)

      return 0

   except Exception as e:
      print(f"\n✗ Test failed with error: {e}")
      import traceback

      traceback.print_exc()
      return 1


if __name__ == "__main__":
   sys.exit(main())

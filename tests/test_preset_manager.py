"""
Unit tests for the PresetDataManager class.

This module contains comprehensive tests for the data manager,
including loading, filtering, and error handling.
"""

import json
import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.preset_manager import PresetDataManager
from data.models.preset import Preset


class TestPresetDataManager:
   """Test suite for PresetDataManager."""

   @pytest.fixture
   def sample_preset_data(self) -> List[dict]:
      """Provide sample preset data for testing."""
      return [
         {"pack": "factory", "type": "bass", "cc0": 30, "pgm": 0, "preset": "Deep Bass", "chars": ["warm", "analog"]},
         {"pack": "factory", "type": "lead", "cc0": 30, "pgm": 1, "preset": "Bright Lead", "chars": ["bright", "digital"]},
         {"pack": "expansion_01", "type": "bass", "cc0": 30, "pgm": 2, "preset": "Sub Bass", "chars": ["deep", "analog"]},
         {"pack": "expansion_01", "type": "pads", "cc0": 30, "pgm": 3, "preset": "Warm Pad", "chars": ["warm", "soft", "UNASSIGNED"]},
      ]

   @pytest.fixture
   def test_file(self, tmp_path, sample_preset_data) -> Path:
      """Create a temporary test file with sample data."""
      test_file = tmp_path / "test_presets.json"
      test_file.write_text(json.dumps(sample_preset_data))
      return test_file

   @pytest.fixture
   def manager(self, test_file) -> PresetDataManager:
      """Create a PresetDataManager with test data."""
      return PresetDataManager(test_file)

   def test_initialization(self, test_file):
      """Test manager initialization."""
      manager = PresetDataManager(test_file)
      assert manager.file_path == test_file
      assert manager._loaded is False
      assert manager._presets == []

   def test_load_data(self, manager):
      """Test loading data from file."""
      manager.load_data()

      assert manager._loaded is True
      assert len(manager._presets) == 4
      assert all(isinstance(p, Preset) for p in manager._presets)

   def test_load_data_only_once(self, manager):
      """Test that load_data only loads once unless forced."""
      manager.load_data()
      presets_first = manager._presets

      manager.load_data()  # Should not reload
      assert manager._presets is presets_first  # Same object reference

   def test_get_all_presets(self, manager):
      """Test getting all presets."""
      presets = manager.get_all_presets()

      assert len(presets) == 4
      assert presets[0].preset == "Deep Bass"
      assert presets[1].preset == "Bright Lead"
      assert presets[2].preset == "Sub Bass"
      assert presets[3].preset == "Warm Pad"

   def test_get_all_presets_lazy_loads(self, manager):
      """Test that get_all_presets loads data if not loaded."""
      assert manager._loaded is False

      presets = manager.get_all_presets()

      assert manager._loaded is True
      assert len(presets) == 4

   def test_filter_by_pack(self, manager):
      """Test filtering by pack."""
      filtered = manager.get_filtered_presets(packs={"factory"})

      assert len(filtered) == 2
      assert all(p.pack == "factory" for p in filtered)
      assert filtered[0].preset == "Deep Bass"
      assert filtered[1].preset == "Bright Lead"

   def test_filter_by_type(self, manager):
      """Test filtering by type."""
      filtered = manager.get_filtered_presets(types={"bass"})

      assert len(filtered) == 2
      assert all(p.type == "bass" for p in filtered)
      assert filtered[0].preset == "Deep Bass"
      assert filtered[1].preset == "Sub Bass"

   def test_filter_by_chars(self, manager):
      """Test filtering by character tags."""
      filtered = manager.get_filtered_presets(chars={"warm"})

      assert len(filtered) == 2
      assert filtered[0].preset == "Deep Bass"
      assert filtered[1].preset == "Warm Pad"

   def test_filter_by_search(self, manager):
      """Test filtering by search term."""
      filtered = manager.get_filtered_presets(search_term="Bass")

      assert len(filtered) == 2
      assert filtered[0].preset == "Deep Bass"
      assert filtered[1].preset == "Sub Bass"

   def test_combined_filters(self, manager):
      """Test combining multiple filters."""
      filtered = manager.get_filtered_presets(packs={"factory"}, types={"bass"}, chars={"analog"})

      assert len(filtered) == 1
      assert filtered[0].preset == "Deep Bass"

   def test_no_filters_returns_all(self, manager):
      """Test that no filters returns all presets."""
      filtered = manager.get_filtered_presets()

      assert len(filtered) == 4

   def test_get_preset_by_midi(self, manager):
      """Test getting preset by MIDI values."""
      preset = manager.get_preset_by_midi(30, 0)
      assert preset is not None
      assert preset.preset == "Deep Bass"

      preset = manager.get_preset_by_midi(30, 3)
      assert preset is not None
      assert preset.preset == "Warm Pad"

      preset = manager.get_preset_by_midi(99, 99)
      assert preset is None

   def test_get_unique_packs(self, manager):
      """Test getting unique pack names."""
      packs = manager.get_unique_packs()

      assert packs == ["expansion_01", "factory"]  # Sorted

   def test_get_unique_types(self, manager):
      """Test getting unique preset types."""
      types = manager.get_unique_types()

      assert types == ["bass", "lead", "pads"]  # Sorted

   def test_get_unique_chars(self, manager):
      """Test getting unique character tags."""
      chars = manager.get_unique_chars()

      # UNASSIGNED should be at the end
      assert chars == ["analog", "bright", "deep", "digital", "soft", "warm", "UNASSIGNED"]

   def test_get_presets_as_tuples(self, manager):
      """Test getting presets as tuples for display."""
      tuples = manager.get_presets_as_tuples()

      assert len(tuples) == 4
      assert all(isinstance(t, tuple) for t in tuples)
      assert all(len(t) == 6 for t in tuples)

      # Check first tuple
      first = tuples[0]
      assert first[0] == "factory"  # pack
      assert first[1] == "bass"  # type
      assert first[2] == 30  # cc0
      assert first[3] == 0  # pgm
      assert first[4] == "Deep Bass"  # preset
      assert first[5] == "warm, analog"  # chars

   def test_get_preset_count(self, manager):
      """Test getting preset count."""
      count = manager.get_preset_count()
      assert count == 4

   def test_get_preset_max_widths(self, manager):
      """Test getting maximum field widths."""
      widths = manager.get_preset_max_widths()

      assert len(widths) == 6
      # Check that widths are reasonable
      assert all(w > 0 for w in widths)
      assert widths[4] >= len("Bright Lead")  # Longest preset name

   def test_reload(self, manager):
      """Test reloading data."""
      manager.load_data()
      assert manager._loaded is True

      manager.reload()
      assert manager._loaded is True
      assert len(manager._presets) == 4

   def test_get_metadata(self, manager):
      """Test getting metadata."""
      metadata = manager.get_metadata()

      assert metadata["total_presets"] == 4
      assert metadata["packs"] == ["expansion_01", "factory"]
      assert metadata["types"] == ["bass", "lead", "pads"]
      assert metadata["unique_chars"] == 7
      assert metadata["loaded"] is True
      assert str(manager.file_path) in metadata["file_path"]

   def test_file_not_found(self, tmp_path):
      """Test handling of missing file."""
      missing_file = tmp_path / "missing.json"
      manager = PresetDataManager(missing_file)

      manager.load_data()

      assert manager._loaded is True
      assert manager._presets == []
      assert manager.get_all_presets() == []

   def test_invalid_json(self, tmp_path):
      """Test handling of invalid JSON."""
      bad_file = tmp_path / "bad.json"
      bad_file.write_text("not valid json {]")

      manager = PresetDataManager(bad_file)
      manager.load_data()

      assert manager._loaded is True
      assert manager._presets == []

   def test_partial_load_with_bad_preset(self, tmp_path):
      """Test that one bad preset doesn't stop loading others."""
      test_data = [
         {"pack": "factory", "type": "bass", "cc0": 30, "pgm": 0, "preset": "Good Preset", "chars": ["warm"]},
         {
            "pack": "factory",
            "type": "bass",
            # Missing required field 'cc0'
            "pgm": 1,
            "preset": "Bad Preset",
            "chars": [],
         },
         {"pack": "factory", "type": "lead", "cc0": 30, "pgm": 2, "preset": "Another Good Preset", "chars": ["bright"]},
      ]

      test_file = tmp_path / "mixed.json"
      test_file.write_text(json.dumps(test_data))

      manager = PresetDataManager(test_file)
      manager.load_data()

      # Should load the two good presets
      assert len(manager._presets) == 2
      assert manager._presets[0].preset == "Good Preset"
      assert manager._presets[1].preset == "Another Good Preset"

   def test_repr(self, manager):
      """Test string representation."""
      manager.load_data()
      repr_str = repr(manager)

      assert "PresetDataManager" in repr_str
      assert "loaded=True" in repr_str
      assert "count=4" in repr_str


class TestPresetDataManagerIntegration:
   """Integration tests with real data structure."""

   @pytest.fixture
   def real_data_manager(self) -> PresetDataManager:
      """Create manager with real data file if it exists."""
      real_file = Path(__file__).parent.parent / "src" / "OsmosePresets.json"

      if not real_file.exists():
         pytest.skip("Real data file not found")

      return PresetDataManager(real_file)

   def test_load_real_data(self, real_data_manager):
      """Test loading the actual preset file."""
      real_data_manager.load_data()

      count = real_data_manager.get_preset_count()
      assert count > 0  # Should have some presets

      # Verify basic structure
      presets = real_data_manager.get_all_presets()
      assert all(isinstance(p, Preset) for p in presets)

      # Check metadata
      metadata = real_data_manager.get_metadata()
      assert metadata["total_presets"] == count
      assert len(metadata["packs"]) > 0
      assert len(metadata["types"]) > 0


if __name__ == "__main__":
   pytest.main([__file__, "-v"])

"""
Unit tests for the AppContext class.

This module tests the application context that manages
the lifecycle of the PresetDataManager.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import json
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.app_context import AppContext
from data.preset_manager import PresetDataManager


class TestAppContext:
   """Test suite for AppContext."""

   @pytest.fixture
   def sample_data(self) -> list:
      """Sample preset data for testing."""
      return [{"pack": "factory", "type": "bass", "cc0": 30, "pgm": 0, "preset": "Test Bass", "chars": ["warm"]}]

   @pytest.fixture
   def test_file(self, tmp_path, sample_data) -> Path:
      """Create a temporary test file."""
      test_file = tmp_path / "test_presets.json"
      test_file.write_text(json.dumps(sample_data))
      return test_file

   def test_initialization_with_file(self, test_file):
      """Test initialization with explicit file path."""
      context = AppContext(test_file)

      assert context.preset_file == test_file
      assert context._preset_manager is None  # Lazy initialization

   def test_initialization_without_file(self):
      """Test initialization with default file path."""
      context = AppContext()

      assert context.preset_file is not None
      assert context.preset_file.name == "OsmosePresets.json"
      assert context._preset_manager is None

   def test_get_preset_manager_lazy_init(self, test_file):
      """Test that preset manager is created on first access."""
      context = AppContext(test_file)

      # Not created yet
      assert context._preset_manager is None

      # First access creates it
      manager = context.get_preset_manager()
      assert manager is not None
      assert isinstance(manager, PresetDataManager)
      assert context._preset_manager is manager

      # Data should be loaded
      assert manager._loaded is True

   def test_get_preset_manager_singleton(self, test_file):
      """Test that same manager instance is returned."""
      context = AppContext(test_file)

      manager1 = context.get_preset_manager()
      manager2 = context.get_preset_manager()

      assert manager1 is manager2  # Same object

   def test_reload_data(self, test_file):
      """Test reloading data through context."""
      context = AppContext(test_file)

      # Get manager to initialize it
      manager = context.get_preset_manager()
      initial_presets = manager.get_all_presets()
      assert len(initial_presets) == 1

      # Reload
      context.reload_data()

      # Should still have same data (file hasn't changed)
      reloaded_presets = manager.get_all_presets()
      assert len(reloaded_presets) == 1
      assert manager._loaded is True

   def test_reload_data_not_initialized(self, test_file):
      """Test reload when manager not yet initialized."""
      context = AppContext(test_file)

      # Should not crash even if manager not initialized
      context.reload_data()

      assert context._preset_manager is None  # Still not initialized

   def test_get_metadata_uninitialized(self, test_file):
      """Test getting metadata before manager is initialized."""
      context = AppContext(test_file)

      metadata = context.get_metadata()

      assert metadata["preset_file"] == str(test_file)
      assert metadata["manager_initialized"] is False
      assert "total_presets" not in metadata  # Manager data not available

   def test_get_metadata_initialized(self, test_file):
      """Test getting metadata after manager is initialized."""
      context = AppContext(test_file)

      # Initialize manager
      manager = context.get_preset_manager()

      metadata = context.get_metadata()

      assert metadata["preset_file"] == str(test_file)
      assert metadata["manager_initialized"] is True
      assert metadata["total_presets"] == 1  # From manager
      assert metadata["loaded"] is True  # From manager

   def test_repr(self, test_file):
      """Test string representation."""
      context = AppContext(test_file)

      repr_str = repr(context)
      assert "AppContext" in repr_str
      assert "initialized=False" in repr_str

      # After initialization
      context.get_preset_manager()
      repr_str = repr(context)
      assert "initialized=True" in repr_str

   def test_integration_with_manager(self, test_file):
      """Test integration between context and manager."""
      context = AppContext(test_file)

      # Get manager through context
      manager = context.get_preset_manager()

      # Use manager methods
      presets = manager.get_all_presets()
      assert len(presets) == 1
      assert presets[0].preset == "Test Bass"

      # Filter through manager
      filtered = manager.get_filtered_presets(types={"bass"})
      assert len(filtered) == 1

   @patch("data.preset_manager.PresetDataManager.load_data")
   def test_manager_loads_on_creation(self, mock_load, test_file):
      """Test that manager loads data immediately when created."""
      context = AppContext(test_file)

      # Access manager
      manager = context.get_preset_manager()

      # Verify load_data was called
      mock_load.assert_called_once()


class TestAppContextWithMissingFile:
   """Test AppContext behavior with missing or invalid files."""

   def test_missing_file_handled_gracefully(self, tmp_path):
      """Test that missing file doesn't crash."""
      missing_file = tmp_path / "missing.json"
      context = AppContext(missing_file)

      # Should not crash
      manager = context.get_preset_manager()
      assert manager is not None

      # Should have empty data
      presets = manager.get_all_presets()
      assert presets == []

      # Metadata should reflect this
      metadata = context.get_metadata()
      assert metadata["total_presets"] == 0

   def test_invalid_file_handled_gracefully(self, tmp_path):
      """Test that invalid JSON doesn't crash."""
      bad_file = tmp_path / "bad.json"
      bad_file.write_text("not valid json")

      context = AppContext(bad_file)
      manager = context.get_preset_manager()

      # Should handle gracefully
      presets = manager.get_all_presets()
      assert presets == []


if __name__ == "__main__":
   pytest.main([__file__, "-v"])

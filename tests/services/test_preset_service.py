"""
Tests for the PresetService class.

This module contains comprehensive tests for the PresetService,
ensuring proper coordination between data layer and filter service.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
from src.services.preset_service import PresetService
from src.services.filter_service import FilterState
from src.data.models.preset import Preset


class TestPresetService:
   """Tests for the PresetService class."""

   @pytest.fixture
   def mock_preset_manager(self):
      """Create a mock PresetDataManager."""
      manager = Mock()
      manager.get_all_presets.return_value = []
      manager.get_filtered_presets.return_value = []
      manager.get_presets_as_tuples.return_value = []
      manager.get_unique_packs.return_value = ["factory", "user"]
      manager.get_unique_types.return_value = ["bass", "lead", "pad"]
      manager.get_unique_chars.return_value = ["warm", "bright", "dark"]
      manager.get_preset_count.return_value = 100
      manager.get_preset_max_widths.return_value = [10, 10, 3, 3, 20, 15]
      return manager

   @pytest.fixture
   def mock_filter_service(self):
      """Create a mock FilterService."""
      service = Mock()
      service.state = FilterState()
      service.add_listener = Mock()
      service.get_state_summary.return_value = "No filters active"
      return service

   @pytest.fixture
   def preset_service(self, mock_preset_manager, mock_filter_service):
      """Create a PresetService with mocked dependencies."""
      return PresetService(mock_preset_manager, mock_filter_service)

   def test_initialization(self, mock_preset_manager, mock_filter_service):
      """Test that PresetService initializes correctly."""
      service = PresetService(mock_preset_manager, mock_filter_service)

      assert service.preset_manager == mock_preset_manager
      assert service.filter_service == mock_filter_service
      # Should register as a listener to filter service
      mock_filter_service.add_listener.assert_called_once()

   def test_get_filtered_presets_no_filters(self, preset_service, mock_preset_manager):
      """Test getting presets when no filters are active."""
      mock_presets = [Mock(spec=Preset, preset="Preset 1"), Mock(spec=Preset, preset="Preset 2")]
      mock_preset_manager.get_filtered_presets.return_value = mock_presets

      result = preset_service.get_filtered_presets()

      assert result == mock_presets
      mock_preset_manager.get_filtered_presets.assert_called_once_with(packs=None, types=None, chars=None, search_term="")

   def test_get_filtered_presets_with_filters(self, preset_service, mock_preset_manager, mock_filter_service):
      """Test getting presets with active filters."""
      # Set up filter state
      mock_filter_service.state.packs = {"factory"}
      mock_filter_service.state.types = {"bass", "lead"}
      mock_filter_service.state.chars = {"warm"}
      mock_filter_service.state.search_term = "piano"

      mock_presets = [Mock(spec=Preset, preset="Filtered Preset")]
      mock_preset_manager.get_filtered_presets.return_value = mock_presets

      result = preset_service.get_filtered_presets()

      assert result == mock_presets
      mock_preset_manager.get_filtered_presets.assert_called_once_with(packs={"factory"}, types={"bass", "lead"}, chars={"warm"}, search_term="piano")

   def test_get_filtered_preset_tuples(self, preset_service, mock_preset_manager, mock_filter_service):
      """Test getting filtered presets as tuples for table display."""
      mock_filter_service.state.packs = {"factory"}
      mock_tuples = [("factory", "bass", 0, 0, "Bass 1", "warm, deep"), ("factory", "bass", 0, 1, "Bass 2", "bright")]
      mock_preset_manager.get_presets_as_tuples.return_value = mock_tuples

      result = preset_service.get_filtered_preset_tuples()

      assert result == mock_tuples
      mock_preset_manager.get_presets_as_tuples.assert_called_once_with(packs={"factory"}, types=None, chars=None, search_term="")

   def test_get_preset_by_midi_found(self, preset_service, mock_preset_manager):
      """Test getting a preset by MIDI values when found."""
      mock_preset = Mock(spec=Preset, preset="Test Preset", cc0=5, pgm=10)
      mock_preset_manager.get_preset_by_midi.return_value = mock_preset

      result = preset_service.get_preset_by_midi(5, 10)

      assert result == mock_preset
      mock_preset_manager.get_preset_by_midi.assert_called_once_with(5, 10)

   def test_get_preset_by_midi_not_found(self, preset_service, mock_preset_manager):
      """Test getting a preset by MIDI values when not found."""
      mock_preset_manager.get_preset_by_midi.return_value = None

      result = preset_service.get_preset_by_midi(99, 99)

      assert result is None
      mock_preset_manager.get_preset_by_midi.assert_called_once_with(99, 99)

   def test_get_available_packs(self, preset_service, mock_preset_manager):
      """Test getting available pack names."""
      result = preset_service.get_available_packs()

      assert result == ["factory", "user"]
      mock_preset_manager.get_unique_packs.assert_called_once()

   def test_get_available_types(self, preset_service, mock_preset_manager):
      """Test getting available preset types."""
      result = preset_service.get_available_types()

      assert result == ["bass", "lead", "pad"]
      mock_preset_manager.get_unique_types.assert_called_once()

   def test_get_available_chars(self, preset_service, mock_preset_manager):
      """Test getting available character tags."""
      result = preset_service.get_available_chars()

      assert result == ["warm", "bright", "dark"]
      mock_preset_manager.get_unique_chars.assert_called_once()

   def test_get_preset_count(self, preset_service, mock_preset_manager):
      """Test getting the count of filtered presets."""
      mock_preset_manager.get_filtered_presets.return_value = [Mock(spec=Preset), Mock(spec=Preset), Mock(spec=Preset)]

      result = preset_service.get_preset_count()

      assert result == 3

   def test_get_total_preset_count(self, preset_service, mock_preset_manager):
      """Test getting the total preset count."""
      result = preset_service.get_total_preset_count()

      assert result == 100
      mock_preset_manager.get_preset_count.assert_called_once()

   def test_reload_data(self, preset_service, mock_preset_manager):
      """Test reloading data."""
      listener = Mock()
      preset_service.add_listener(listener)

      preset_service.reload_data()

      mock_preset_manager.reload.assert_called_once()
      listener.assert_called_once()

   def test_add_listener(self, preset_service):
      """Test adding a listener."""
      listener1 = Mock()
      listener2 = Mock()

      preset_service.add_listener(listener1)
      preset_service.add_listener(listener2)

      # Trigger notification
      preset_service._notify_listeners()

      listener1.assert_called_once()
      listener2.assert_called_once()

   def test_add_duplicate_listener(self, preset_service):
      """Test that duplicate listeners aren't added."""
      listener = Mock()

      preset_service.add_listener(listener)
      preset_service.add_listener(listener)  # Try to add again

      preset_service._notify_listeners()

      # Should only be called once
      assert listener.call_count == 1

   def test_remove_listener(self, preset_service):
      """Test removing a listener."""
      listener1 = Mock()
      listener2 = Mock()

      preset_service.add_listener(listener1)
      preset_service.add_listener(listener2)
      preset_service.remove_listener(listener1)

      preset_service._notify_listeners()

      listener1.assert_not_called()
      listener2.assert_called_once()

   def test_filter_change_triggers_listeners(self, preset_service, mock_filter_service):
      """Test that filter changes trigger preset listeners."""
      # Get the filter change callback that was registered
      filter_callback = mock_filter_service.add_listener.call_args[0][0]

      # Add a preset listener
      preset_listener = Mock()
      preset_service.add_listener(preset_listener)

      # Simulate a filter change
      new_state = FilterState()
      new_state.packs = {"factory"}
      filter_callback(new_state)

      # Preset listener should be notified
      preset_listener.assert_called_once()

   def test_listener_exception_handling(self, preset_service):
      """Test that exception in one listener doesn't affect others."""
      bad_listener = Mock(side_effect=Exception("Test error"))
      good_listener = Mock()

      preset_service.add_listener(bad_listener)
      preset_service.add_listener(good_listener)

      preset_service._notify_listeners()

      # Both should be called despite the exception
      bad_listener.assert_called_once()
      good_listener.assert_called_once()

   def test_get_statistics(self, preset_service, mock_preset_manager, mock_filter_service):
      """Test getting statistics about the preset collection."""
      mock_preset_manager.get_all_presets.return_value = [Mock(spec=Preset)] * 100
      mock_preset_manager.get_filtered_presets.return_value = [Mock(spec=Preset)] * 50
      mock_filter_service.state.is_active = Mock(return_value=True)

      stats = preset_service.get_statistics()

      assert stats["total_presets"] == 100
      assert stats["filtered_presets"] == 50
      assert stats["unique_packs"] == 2
      assert stats["unique_types"] == 3
      assert stats["unique_chars"] == 3
      assert stats["filters_active"] is True
      assert stats["filter_summary"] == "No filters active"

   def test_export_filtered_presets(self, preset_service, mock_preset_manager, tmp_path):
      """Test exporting filtered presets to JSON."""
      # Create mock presets with to_dict method
      mock_preset1 = Mock(spec=Preset)
      mock_preset1.to_dict.return_value = {"preset": "Preset 1", "type": "bass"}
      mock_preset2 = Mock(spec=Preset)
      mock_preset2.to_dict.return_value = {"preset": "Preset 2", "type": "lead"}

      mock_preset_manager.get_filtered_presets.return_value = [mock_preset1, mock_preset2]

      output_file = tmp_path / "exported.json"
      count = preset_service.export_filtered_presets(output_file)

      assert count == 2
      assert output_file.exists()

      # Verify the JSON content
      import json

      with open(output_file, "r") as f:
         data = json.load(f)

      assert len(data) == 2
      assert data[0] == {"preset": "Preset 1", "type": "bass"}
      assert data[1] == {"preset": "Preset 2", "type": "lead"}

   def test_get_preset_field_widths(self, preset_service, mock_preset_manager):
      """Test getting preset field widths for table display."""
      result = preset_service.get_preset_field_widths()

      assert result == [10, 10, 3, 3, 20, 15]
      mock_preset_manager.get_preset_max_widths.assert_called_once()

   def test_repr(self, preset_service, mock_preset_manager):
      """Test string representation."""
      mock_preset_manager.get_all_presets.return_value = [Mock(spec=Preset)] * 100
      mock_preset_manager.get_filtered_presets.return_value = [Mock(spec=Preset)] * 50

      repr_str = repr(preset_service)

      assert "PresetService" in repr_str
      assert "total=100" in repr_str
      assert "filtered=50" in repr_str
      assert "listeners=0" in repr_str

"""
Tests for the AppServices container.

This module contains tests for the AppServices class that wires
together all application services.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.services.app_services import AppServices
from src.services.preset_service import PresetService
from src.services.filter_service import FilterService
from src.data.app_context import AppContext


class TestAppServices:
   """Tests for the AppServices container class."""

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_initialization(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test that AppServices initializes all services correctly."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_preset_manager = Mock()
      mock_app_context.get_preset_manager.return_value = mock_preset_manager
      mock_app_context_class.return_value = mock_app_context

      mock_filter_service = Mock(spec=FilterService)
      mock_filter_service_class.return_value = mock_filter_service

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service_class.return_value = mock_preset_service

      # Create AppServices
      preset_file = Path("/test/presets.json")
      app_services = AppServices(preset_file)

      # Verify initialization
      mock_app_context_class.assert_called_once_with(preset_file)
      mock_filter_service_class.assert_called_once()
      mock_preset_service_class.assert_called_once_with(mock_preset_manager, mock_filter_service)

      assert app_services.app_context == mock_app_context
      assert app_services.filter_service == mock_filter_service
      assert app_services.preset_service == mock_preset_service

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_initialization_with_default_preset_file(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test that AppServices uses default preset file when none provided."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_preset_manager = Mock()
      mock_app_context.get_preset_manager.return_value = mock_preset_manager
      mock_app_context_class.return_value = mock_app_context

      mock_filter_service = Mock(spec=FilterService)
      mock_filter_service_class.return_value = mock_filter_service

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service_class.return_value = mock_preset_service

      # Create AppServices without preset file
      app_services = AppServices()

      # Should be called with None (AppContext will handle the default)
      mock_app_context_class.assert_called_once_with(None)

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_get_preset_service(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test getting the preset service."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service_class.return_value = mock_preset_service

      app_services = AppServices()
      result = app_services.get_preset_service()

      assert result == mock_preset_service

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_get_filter_service(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test getting the filter service."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      mock_filter_service = Mock(spec=FilterService)
      mock_filter_service_class.return_value = mock_filter_service

      app_services = AppServices()
      result = app_services.get_filter_service()

      assert result == mock_filter_service

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_get_app_context(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test getting the app context."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      app_services = AppServices()
      result = app_services.get_app_context()

      assert result == mock_app_context

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_reload_data(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test reloading data."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service_class.return_value = mock_preset_service

      app_services = AppServices()
      app_services.reload_data()

      mock_preset_service.reload_data.assert_called_once()

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_shutdown(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test shutdown method."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      app_services = AppServices()

      # Should not raise any errors
      app_services.shutdown()

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_get_status(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test getting status of all services."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context.get_metadata.return_value = {"preset_file": "/test/presets.json", "total_presets": 100}
      mock_app_context_class.return_value = mock_app_context

      mock_filter_service = Mock(spec=FilterService)
      mock_filter_service.get_state_summary.return_value = "2 pack(s), 1 type(s)"
      mock_filter_service_class.return_value = mock_filter_service

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service.get_statistics.return_value = {"total_presets": 100, "filtered_presets": 50, "filters_active": True}
      mock_preset_service_class.return_value = mock_preset_service

      app_services = AppServices()
      status = app_services.get_status()

      assert status["app_context"] == {"preset_file": "/test/presets.json", "total_presets": 100}
      assert status["preset_service"] == {"total_presets": 100, "filtered_presets": 50, "filters_active": True}
      assert status["filter_service"] == "2 pack(s), 1 type(s)"
      assert status["services_ready"] is True

   @patch("src.services.app_services.AppContext")
   @patch("src.services.app_services.FilterService")
   @patch("src.services.app_services.PresetService")
   def test_repr(self, mock_preset_service_class, mock_filter_service_class, mock_app_context_class):
      """Test string representation."""
      # Set up mocks
      mock_app_context = Mock(spec=AppContext)
      mock_app_context.get_preset_manager.return_value = Mock()
      mock_app_context_class.return_value = mock_app_context

      mock_filter_service = Mock(spec=FilterService)
      mock_filter_state = Mock()
      mock_filter_state.is_active.return_value = True
      mock_filter_service.state = mock_filter_state
      mock_filter_service_class.return_value = mock_filter_service

      mock_preset_service = Mock(spec=PresetService)
      mock_preset_service.get_statistics.return_value = {"total_presets": 100}
      mock_preset_service_class.return_value = mock_preset_service

      app_services = AppServices()
      repr_str = repr(app_services)

      assert "AppServices" in repr_str
      assert "presets=100" in repr_str
      assert "filters=True" in repr_str


class TestAppServicesIntegration:
   """Integration tests for AppServices with real components."""

   def test_services_wiring(self, tmp_path):
      """Test that services are properly wired together."""
      # Create a minimal preset file
      preset_file = tmp_path / "test_presets.json"
      preset_file.write_text("""[
            {
                "pack": "factory",
                "type": "bass",
                "cc0": 0,
                "pgm": 0,
                "preset": "Test Bass",
                "chars": ["warm", "deep"]
            }
        ]""")

      # Create AppServices with real components
      app_services = AppServices(preset_file)

      # Verify services are wired correctly
      preset_service = app_services.get_preset_service()
      filter_service = app_services.get_filter_service()

      # Get initial presets
      presets = preset_service.get_filtered_presets()
      assert len(presets) == 1

      # Apply a filter
      filter_service.set_pack_filter({"user"})  # Non-existent pack

      # Should get no presets now
      presets = preset_service.get_filtered_presets()
      assert len(presets) == 0

      # Clear filter
      filter_service.clear_filters()

      # Should get the preset back
      presets = preset_service.get_filtered_presets()
      assert len(presets) == 1

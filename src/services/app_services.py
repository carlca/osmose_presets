"""
Application services container.

This module provides a container for all application services,
wiring them together and providing a single entry point for
the UI layer to access business logic.
"""

from pathlib import Path
from typing import Optional
from textual import log

from data.app_context import AppContext
from services.preset_service import PresetService
from services.filter_service import FilterService


class AppServices:
   """
   Container for all application services.

   This class acts as the main dependency injection container,
   creating and wiring together all services needed by the application.
   It provides a clean interface for UI components to access business logic.
   """

   def __init__(self, preset_file: Optional[Path] = None):
      """
      Initialize all application services.

      Args:
          preset_file: Path to the preset JSON file.
                      If None, uses default location.
      """
      log("Initializing application services")

      # Create data layer
      self.app_context = AppContext(preset_file)

      # Create services
      self.filter_service = FilterService()
      self.preset_service = PresetService(self.app_context.get_preset_manager(), self.filter_service)

      log("Application services initialized successfully")

   def get_preset_service(self) -> PresetService:
      """
      Get the preset service instance.

      Returns:
          The singleton PresetService instance
      """
      return self.preset_service

   def get_filter_service(self) -> FilterService:
      """
      Get the filter service instance.

      Returns:
          The singleton FilterService instance
      """
      return self.filter_service

   def get_app_context(self) -> AppContext:
      """
      Get the application context.

      Returns:
          The AppContext instance
      """
      return self.app_context

   def reload_data(self) -> None:
      """
      Force reload of all data.

      This method reloads preset data and resets any cached state.
      """
      log("Reloading all application data")
      self.preset_service.reload_data()

   def shutdown(self) -> None:
      """
      Perform cleanup when shutting down the application.

      This method can be called to cleanly shut down services
      and release any resources.
      """
      log("Shutting down application services")
      # Currently no cleanup needed, but this provides a hook for future needs
      pass

   def get_status(self) -> dict:
      """
      Get the current status of all services.

      Returns:
          Dictionary with status information for all services
      """
      return {
         "app_context": self.app_context.get_metadata(),
         "preset_service": self.preset_service.get_statistics(),
         "filter_service": self.filter_service.get_state_summary(),
         "services_ready": True,
      }

   def __repr__(self) -> str:
      """String representation for debugging."""
      stats = self.preset_service.get_statistics()
      return f"AppServices(presets={stats['total_presets']}, filters={self.filter_service.state.is_active()})"

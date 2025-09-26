"""
Application context for managing shared resources.

This module provides a simple context class that manages the
lifecycle of the data manager and makes it available to UI components.
"""

from pathlib import Path
from typing import Optional
from .preset_manager import PresetDataManager


class AppContext:
   """
   Application context to manage shared resources.

   This class acts as a simple dependency injection container,
   providing a single instance of the PresetDataManager to all
   components that need it.
   """

   def __init__(self, preset_file: Optional[Path] = None):
      """
      Initialize the application context.

      Args:
          preset_file: Path to the preset JSON file.
                      If None, uses default location.
      """
      if preset_file is None:
         # Default to OsmosePresets.json in the same directory
         preset_file = Path(__file__).parent.parent / "OsmosePresets.json"

      self.preset_file = preset_file
      self._preset_manager: Optional[PresetDataManager] = None

   def get_preset_manager(self) -> PresetDataManager:
      """
      Get the preset data manager instance.

      Creates the manager on first access (lazy initialization).

      Returns:
          The singleton PresetDataManager instance
      """
      if self._preset_manager is None:
         self._preset_manager = PresetDataManager(self.preset_file)
         # Load data immediately
         self._preset_manager.load_data()

      return self._preset_manager

   def reload_data(self) -> None:
      """
      Force reload of preset data.

      Useful for refreshing data after external changes.
      """
      if self._preset_manager:
         self._preset_manager.reload()

   def get_metadata(self) -> dict:
      """
      Get metadata about the application state.

      Returns:
          Dictionary with app metadata
      """
      metadata = {"preset_file": str(self.preset_file), "manager_initialized": self._preset_manager is not None}

      if self._preset_manager:
         metadata.update(self._preset_manager.get_metadata())

      return metadata

   def __repr__(self) -> str:
      """String representation for debugging."""
      return f"AppContext(preset_file={self.preset_file.name}, initialized={self._preset_manager is not None})"

"""
Preset service for managing preset operations.

This module provides the main business logic service that coordinates
between the data layer and the UI, handling preset filtering and selection.
"""

from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
from textual import log

from data.preset_manager import PresetDataManager
from data.models.preset import Preset
from services.filter_service import FilterService, FilterState


class PresetService:
   """
   Main service for preset operations.

   This service orchestrates the interaction between the data layer
   (PresetDataManager) and the filter service, providing a clean
   interface for UI components.
   """

   def __init__(self, preset_manager: PresetDataManager, filter_service: FilterService):
      """
      Initialize the preset service.

      Args:
          preset_manager: Data manager for preset operations
          filter_service: Service for managing filter state
      """
      self.preset_manager = preset_manager
      self.filter_service = filter_service

      # Listen to filter changes
      self.filter_service.add_listener(self._on_filter_change)

      # Listeners for preset changes
      self._listeners: List[Callable[[], None]] = []

      log("PresetService initialized")

   def get_filtered_presets(self) -> List[Preset]:
      """
      Get presets based on current filters.

      Returns:
          List of presets matching all active filters
      """
      state = self.filter_service.state
      
      log(f"get_filtered_presets - packs: {len(state.packs)}, types: {len(state.types)}, chars: {len(state.chars)}")

      # Only show presets if ALL filter categories have selections
      # If any category has nothing selected, return empty list
      if not state.packs or not state.types or not state.chars:
         log(f"No presets shown - empty filter(s): packs={bool(state.packs)}, types={bool(state.types)}, chars={bool(state.chars)}")
         return []

      # Convert sets to None if empty (PresetDataManager expects None for no filter)
      packs = state.packs if state.packs else None
      types = state.types if state.types else None
      chars = state.chars if state.chars else None

      presets = self.preset_manager.get_filtered_presets(packs=packs, types=types, chars=chars, search_term=state.search_term)

      log(f"Filtered presets: {len(presets)} results")
      return presets

   def get_filtered_preset_tuples(self) -> List[tuple]:
      """
      Get filtered presets as tuples for table display.

      Returns:
          List of preset tuples ready for table display
      """
      state = self.filter_service.state
      
      log(f"get_filtered_preset_tuples - packs: {len(state.packs)}, types: {len(state.types)}, chars: {len(state.chars)}")

      # Only show presets if ALL filter categories have selections
      # If any category has nothing selected, return empty list
      if not state.packs or not state.types or not state.chars:
         log(f"No preset tuples - empty filter(s): packs={bool(state.packs)}, types={bool(state.types)}, chars={bool(state.chars)}")
         return []

      # Convert sets to None if empty
      packs = state.packs if state.packs else None
      types = state.types if state.types else None
      chars = state.chars if state.chars else None

      return self.preset_manager.get_presets_as_tuples(packs=packs, types=types, chars=chars, search_term=state.search_term)

   def get_preset_by_midi(self, cc0: int, pgm: int) -> Optional[Preset]:
      """
      Get a specific preset by MIDI values.

      Args:
          cc0: MIDI CC0 (bank select) value
          pgm: MIDI program change value

      Returns:
          Preset if found, None otherwise
      """
      preset = self.preset_manager.get_preset_by_midi(cc0, pgm)
      if preset:
         log(f"Found preset: {preset.preset} (CC0={cc0}, PGM={pgm})")
      else:
         log(f"No preset found for CC0={cc0}, PGM={pgm}")
      return preset

   def get_available_packs(self) -> List[str]:
      """
      Get all available pack names.

      Returns:
          Sorted list of pack names
      """
      return self.preset_manager.get_unique_packs()

   def get_available_types(self) -> List[str]:
      """
      Get all available preset types.

      Returns:
          Sorted list of preset types
      """
      return self.preset_manager.get_unique_types()

   def get_available_chars(self) -> List[str]:
      """
      Get all available character tags.

      Returns:
          Sorted list of character tags
      """
      return self.preset_manager.get_unique_chars()

   def get_preset_count(self) -> int:
      """
      Get the number of presets matching current filters.

      Returns:
          Number of filtered presets
      """
      return len(self.get_filtered_presets())

   def get_total_preset_count(self) -> int:
      """
      Get the total number of presets in the system.

      Returns:
          Total number of presets
      """
      return self.preset_manager.get_preset_count()

   def reload_data(self) -> None:
      """
      Force reload of preset data from file.

      This method reloads the data and notifies all listeners.
      """
      log("Reloading preset data")
      self.preset_manager.reload()
      self._notify_listeners()

   def add_listener(self, callback: Callable[[], None]) -> None:
      """
      Add a callback for preset changes.

      Args:
          callback: Function to call when presets may have changed
      """
      if callback not in self._listeners:
         self._listeners.append(callback)
         log(f"Preset listener added (total: {len(self._listeners)})")

   def remove_listener(self, callback: Callable[[], None]) -> None:
      """
      Remove a previously added listener.

      Args:
          callback: The callback function to remove
      """
      if callback in self._listeners:
         self._listeners.remove(callback)
         log(f"Preset listener removed (remaining: {len(self._listeners)})")

   def _on_filter_change(self, filter_state: FilterState) -> None:
      """
      Handle filter changes.

      Args:
          filter_state: The new filter state
      """
      log(f"Filter changed: {filter_state}")
      # Notify listeners that presets may have changed
      self._notify_listeners()

   def _notify_listeners(self) -> None:
      """Notify all listeners of potential preset changes."""
      for callback in self._listeners[:]:  # Use slice to avoid issues if listeners modify the list
         try:
            callback()
         except Exception as e:
            log(f"Error in preset listener: {e}")

   def get_statistics(self) -> Dict[str, Any]:
      """
      Get statistics about the preset collection.

      Returns:
          Dictionary with various statistics
      """
      all_presets = self.preset_manager.get_all_presets()
      filtered_presets = self.get_filtered_presets()

      return {
         "total_presets": len(all_presets),
         "filtered_presets": len(filtered_presets),
         "unique_packs": len(self.get_available_packs()),
         "unique_types": len(self.get_available_types()),
         "unique_chars": len(self.get_available_chars()),
         "filters_active": self.filter_service.state.is_active(),
         "filter_summary": self.filter_service.get_state_summary(),
      }

   def export_filtered_presets(self, output_path: Path) -> int:
      """
      Export currently filtered presets to a JSON file.

      Args:
          output_path: Path where to save the exported presets

      Returns:
          Number of presets exported
      """
      import json

      presets = self.get_filtered_presets()
      preset_dicts = [p.to_dict() for p in presets]

      with open(output_path, "w", encoding="utf-8") as f:
         json.dump(preset_dicts, f, indent=2)

      log(f"Exported {len(presets)} presets to {output_path}")
      return len(presets)

   def get_preset_field_widths(self) -> List[int]:
      """
      Get maximum width for each preset field.

      This is useful for table column sizing.

      Returns:
          List of maximum widths for each field
      """
      return self.preset_manager.get_preset_max_widths()

   def __repr__(self) -> str:
      """String representation for debugging."""
      stats = self.get_statistics()
      return f"PresetService(total={stats['total_presets']}, filtered={stats['filtered_presets']}, listeners={len(self._listeners)})"

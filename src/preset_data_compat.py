"""
Compatibility adapter for migrating from static PresetData to PresetDataManager.

This module provides a drop-in replacement for the old PresetData class,
allowing gradual migration of UI components to the new architecture.
"""

from pathlib import Path
from typing import List, Optional
from textual import log
from data.app_context import AppContext
from data.preset_manager import PresetDataManager
from data.models.preset import Preset


# Create global app context for backward compatibility
_app_context: Optional[AppContext] = None


def _get_context() -> AppContext:
    """Get or create the global app context."""
    global _app_context
    if _app_context is None:
        # Initialize with default file location
        preset_file = Path(__file__).parent / "OsmosePresets.json"
        _app_context = AppContext(preset_file)
        log("Initialized compatibility app context")
    return _app_context


class PresetData:
   """
   Compatibility wrapper that mimics the old static PresetData class.

   This class provides the same interface as the original PresetData
   but delegates to the new PresetDataManager under the hood.

   NOTE: This is a transitional class. New code should use
   PresetDataManager directly through dependency injection.
   """

   # These class variables are maintained for compatibility
   # but are now populated from the manager
   cached_presets = []
   pack_filters = []
   type_filters = []
   char_filters = []
   search_term = ""

   @staticmethod
   def _get_manager() -> PresetDataManager:
      """Get the preset manager from the app context."""
      return _get_context().get_preset_manager()

   @staticmethod
   def load_from_json(file_path: str) -> List[Preset]:
      """
      Load presets from JSON file.

      Args:
         file_path: Path to JSON file

      Returns:
         List of loaded presets
      """
      # Update the global context with new file path
      global _app_context
      _app_context = AppContext(Path(file_path))

      manager = PresetData._get_manager()
      presets = manager.get_all_presets()

      # Update cached_presets for compatibility
      PresetData.cached_presets = presets

      return presets

   @staticmethod
   def evaluate_search(search_term: str, target: str) -> bool:
      """
      Evaluate search with AND/OR operators.

      Args:
         search_term: Search string with optional operators
         target: String to search in

      Returns:
         True if search matches
      """
      # Delegate to Preset model's search logic
      or_clauses = [clause.strip() for clause in search_term.split(" OR ")]
      and_results = (all(term.strip().lower() in target.lower() for term in clause.split(" AND ")) for clause in or_clauses)
      return any(and_results)

   @staticmethod
   def get_presets():
      """
      Get filtered presets based on current filters.

      Returns:
         List of filtered presets
      """
      # Only apply filters if all filter categories have selections
      # If any category has nothing selected, return empty list
      if not PresetData.pack_filters or not PresetData.type_filters or not PresetData.char_filters:
         return []

      manager = PresetData._get_manager()

      # Convert filters to sets for the manager
      packs = set(PresetData.pack_filters) if PresetData.pack_filters else None
      types = set(PresetData.type_filters) if PresetData.type_filters else None
      chars = set(PresetData.char_filters) if PresetData.char_filters else None

      return manager.get_filtered_presets(packs=packs, types=types, chars=chars, search_term=PresetData.search_term)

   @staticmethod
   def preset_to_tuple(preset: Preset) -> tuple:
      """
      Convert preset to tuple for display.

      Args:
         preset: Preset object

      Returns:
         Tuple representation
      """
      return preset.to_tuple()

   @staticmethod
   def get_presets_as_tuples():
      """
      Get filtered presets as tuples.

      Returns:
         List of preset tuples
      """
      presets = PresetData.get_presets()
      return [preset.to_tuple() for preset in presets]

   @staticmethod
   def get_all_presets():
      """
      Get all presets without filtering.

      Returns:
         List of all presets
      """
      manager = PresetData._get_manager()
      return manager.get_all_presets()

   @staticmethod
   def get_preset_max_widths() -> list:
      """
      Get maximum widths for each field.

      Returns:
         List of maximum widths
      """
      manager = PresetData._get_manager()
      return manager.get_preset_max_widths()

   @staticmethod
   def get_chars() -> list:
      """
      Get unique character tags.

      Returns:
         Sorted list of character tags
      """
      manager = PresetData._get_manager()
      return manager.get_unique_chars()

   @staticmethod
   def set_search_filter(search_term: str):
      """
      Set search filter.

      Args:
         search_term: Search string
      """
      PresetData.search_term = search_term

   @staticmethod
   def get_all_preset_names():
      """
      Get all preset names.

      Returns:
         List of preset names
      """
      manager = PresetData._get_manager()
      presets = manager.get_all_presets()
      return [p.preset for p in presets]

   @staticmethod
   def clear_pack_filters():
      """Clear pack filters."""
      PresetData.pack_filters.clear()

   @staticmethod
   def add_pack_filter(pack_filter):
      """
      Add pack filter(s).

      Args:
         pack_filter: String or list of pack names
      """
      if isinstance(pack_filter, str):
         PresetData.pack_filters.append(pack_filter)
      elif isinstance(pack_filter, list):
         PresetData.pack_filters.extend(pack_filter)
      else:
         raise TypeError("pack_filter must be a string or a list of strings")

   @staticmethod
   def clear_type_filters():
      """Clear type filters."""
      PresetData.type_filters.clear()

   @staticmethod
   def add_type_filter(type_filter):
      """
      Add type filter(s).

      Args:
         type_filter: String or list of type names
      """
      if isinstance(type_filter, str):
         PresetData.type_filters.append(type_filter)
      elif isinstance(type_filter, list):
         PresetData.type_filters.extend(type_filter)
      else:
         raise TypeError("type_filter must be a string or a list of strings")

   @staticmethod
   def clear_char_filters():
      """Clear character filters."""
      PresetData.char_filters.clear()

   @staticmethod
   def add_char_filter(char_filter):
      """
      Add character filter(s).

      Args:
         char_filter: String or list of character tags
      """
      if isinstance(char_filter, str):
         PresetData.char_filters.append(char_filter)
      elif isinstance(char_filter, list):
         PresetData.char_filters.extend(char_filter)
      else:
         raise TypeError("char_filter must be a string or a list of strings")

   @staticmethod
   def get_packs():
      """
      Get unique pack names.

      Returns:
         List of pack names
      """
      manager = PresetData._get_manager()
      return manager.get_unique_packs()

   @staticmethod
   def get_types(pack=""):
      """
      Get unique preset types.

      Args:
         pack: Optional pack filter (not used in new implementation)

      Returns:
         List of preset types
      """
      manager = PresetData._get_manager()

      if pack:
         # Filter by pack if specified
         presets = manager.get_filtered_presets(packs={pack})
         types = {p.type for p in presets}
         return sorted(types)
      else:
         return manager.get_unique_types()


# Initialize cached_presets on import for compatibility
# Initialize with presets on import for backward compatibility
if not PresetData.cached_presets:
    try:
        preset_file = Path(__file__).parent / "OsmosePresets.json"
        PresetData.cached_presets = PresetData.load_from_json(str(preset_file))
        log(f"Loaded {len(PresetData.cached_presets)} presets for compatibility")
    except Exception as e:
        log(f"Warning: Could not load presets on import: {e}")
        PresetData.cached_presets = []

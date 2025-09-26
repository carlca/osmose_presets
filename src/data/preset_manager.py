"""
Preset data manager for loading and filtering preset data.

This module provides a simple, testable manager class that replaces
the static PresetData class with proper dependency injection.
"""

from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import json
from dataclasses import fields
from textual import log
from .models.preset import Preset


class PresetDataManager:
   """
   Simple data manager for preset operations.

   Handles loading presets from JSON file and provides
   filtering capabilities without global state.
   """

   def __init__(self, file_path: Path):
      """
      Initialize the preset data manager.

      Args:
          file_path: Path to the JSON file containing preset data
      """
      self.file_path = file_path
      self._presets: List[Preset] = []
      self._loaded = False

   def load_data(self) -> None:
      """
      Load presets from JSON file.

      This method loads the data once and caches it in memory.
      Call reload() to force a fresh load from disk.
      """
      if self._loaded:
         return

      try:
         with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

         self._presets = []
         for i, item in enumerate(data):
            try:
               preset = Preset.from_dict(item)
               self._presets.append(preset)
            except Exception as e:
               log(f"Warning: Failed to load preset at index {i}: {e}")
               # Continue loading other presets

         self._loaded = True
         log(f"Loaded {len(self._presets)} presets from {self.file_path}")

      except FileNotFoundError:
         log(f"Error: Preset file not found: {self.file_path}")
         self._presets = []
         self._loaded = True  # Mark as loaded to avoid retrying
      except json.JSONDecodeError as e:
         log(f"Error: Invalid JSON in preset file: {e}")
         self._presets = []
         self._loaded = True
      except Exception as e:
         log(f"Error loading presets: {e}")
         self._presets = []
         self._loaded = True

   def get_all_presets(self) -> List[Preset]:
      """
      Get all presets.

      Returns:
          List of all loaded presets
      """
      if not self._loaded:
         self.load_data()
      return self._presets

   def get_filtered_presets(
      self, packs: Optional[Set[str]] = None, types: Optional[Set[str]] = None, chars: Optional[Set[str]] = None, search_term: str = ""
   ) -> List[Preset]:
      """
      Get filtered presets based on criteria.

      Args:
          packs: Set of pack names to filter by (None = no filter)
          types: Set of preset types to filter by (None = no filter)
          chars: Set of character tags to filter by (None = no filter)
          search_term: Search term for preset names (empty = no filter)

      Returns:
          List of presets matching all filter criteria
      """
      presets = self.get_all_presets()

      # Apply pack filter
      if packs:
         presets = [p for p in presets if p.pack in packs]

      # Apply type filter
      if types:
         presets = [p for p in presets if p.type in types]

      # Apply character filter (preset must have at least one matching char)
      if chars:
         presets = [p for p in presets if set(p.chars) & chars]

      # Apply search filter
      if search_term:
         presets = [p for p in presets if p.matches_search(search_term)]

      return presets

   def get_preset_by_midi(self, cc0: int, pgm: int) -> Optional[Preset]:
      """
      Get a specific preset by MIDI values.

      Args:
          cc0: MIDI CC0 (bank select) value
          pgm: MIDI program change value

      Returns:
          Preset if found, None otherwise
      """
      for preset in self.get_all_presets():
         if preset.cc0 == cc0 and preset.pgm == pgm:
            return preset
      return None

   def get_unique_packs(self) -> List[str]:
      """
      Get sorted list of unique pack names.

      Returns:
          Sorted list of pack names
      """
      packs = {p.pack for p in self.get_all_presets()}
      return sorted(packs)

   def get_unique_types(self) -> List[str]:
      """
      Get sorted list of unique preset types.

      Returns:
          Sorted list of preset types
      """
      types = {p.type for p in self.get_all_presets()}
      return sorted(types)

   def get_unique_chars(self) -> List[str]:
      """
      Get sorted list of unique character tags.

      Returns:
          Sorted list of character tags, with UNASSIGNED at the end if present
      """
      chars = set()
      for preset in self.get_all_presets():
         chars.update(preset.chars)

      # Sort chars, but put UNASSIGNED at the end if it exists
      sorted_chars = sorted(chars - {"UNASSIGNED"})
      if "UNASSIGNED" in chars:
         sorted_chars.append("UNASSIGNED")

      return sorted_chars

   def get_presets_as_tuples(
      self, packs: Optional[Set[str]] = None, types: Optional[Set[str]] = None, chars: Optional[Set[str]] = None, search_term: str = ""
   ) -> List[tuple]:
      """
      Get filtered presets as tuples for table display.

      This method combines filtering and tuple conversion for efficiency.

      Args:
          packs: Set of pack names to filter by (None = no filter)
          types: Set of preset types to filter by (None = no filter)
          chars: Set of character tags to filter by (None = no filter)
          search_term: Search term for preset names (empty = no filter)

      Returns:
          List of preset tuples (pack, type, cc0, pgm, preset, chars_display)
      """
      presets = self.get_filtered_presets(packs, types, chars, search_term)
      return [p.to_tuple() for p in presets]

   def get_preset_count(self) -> int:
      """
      Get the total number of presets.

      Returns:
          Number of loaded presets
      """
      return len(self.get_all_presets())

   def get_preset_max_widths(self) -> List[int]:
      """
      Get maximum width for each preset field.

      This is useful for table column sizing.

      Returns:
          List of maximum widths for each field
      """
      if not self.get_all_presets():
         return []

      # Initialize with field name lengths
      field_names = [f.name if f.name != "chars" else "character" for f in fields(Preset)]
      max_widths = [len(name) for name in field_names]

      # Check all presets for maximum widths
      for preset in self.get_all_presets():
         widths = preset.get_field_widths()
         for i, width in enumerate(widths):
            if width > max_widths[i]:
               max_widths[i] = width

      return max_widths

   def reload(self) -> None:
      """
      Force reload of data from file.

      This clears the cache and reloads from disk.
      """
      self._loaded = False
      self._presets = []
      self.load_data()

   def get_metadata(self) -> Dict[str, Any]:
      """
      Get metadata about the preset collection.

      Returns:
          Dictionary with metadata including counts and file info
      """
      presets = self.get_all_presets()

      return {
         "file_path": str(self.file_path),
         "total_presets": len(presets),
         "packs": self.get_unique_packs(),
         "types": self.get_unique_types(),
         "unique_chars": len(self.get_unique_chars()),
         "loaded": self._loaded,
      }

   def __repr__(self) -> str:
      """String representation for debugging."""
      return f"PresetDataManager(file={self.file_path.name}, loaded={self._loaded}, count={len(self._presets)})"

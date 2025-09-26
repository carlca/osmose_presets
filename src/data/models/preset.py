"""
Enhanced Preset model for the Osmose Presets application.

This module contains the core Preset data model with validation,
helper methods, and proper type hints.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Set
from enum import Enum


class PresetType(Enum):
   """Enumeration of available preset types."""

   BASS = "bass"
   BOWED = "bowed"
   BRASS = "brass"
   ELEC_PIANO = "elec piano"
   FLUTE_REEDS = "flute reeds"
   KEYS = "keys"
   LEAD = "lead"
   MALLETS = "mallets"
   ORGAN = "organ"
   PADS = "pads"
   PERC = "perc"
   PLUCKED = "plucked"
   SFX = "sfx"

   @classmethod
   def from_string(cls, value: str) -> Optional["PresetType"]:
      """
      Create PresetType from string value.

      Args:
          value: String representation of preset type

      Returns:
          PresetType enum or None if not found
      """
      for preset_type in cls:
         if preset_type.value == value.lower():
            return preset_type
      return None

   @classmethod
   def get_display_values(cls) -> List[str]:
      """Get list of all preset type display values."""
      return [preset_type.value for preset_type in cls]


@dataclass(frozen=True)  # Make immutable for safety
class Preset:
   """
   Immutable preset data model.

   Attributes:
       pack: The preset pack name
       type: The preset type (e.g., bass, lead, pads)
       cc0: MIDI CC0 (bank select) value (0-127)
       pgm: MIDI program change value (0-127)
       preset: The preset name
       chars: List of characteristic tags
   """

   pack: str
   type: str
   cc0: int
   pgm: int
   preset: str
   chars: List[str] = field(default_factory=list)

   def __post_init__(self):
      """Validate preset data after initialization."""
      # Validate MIDI values
      if not 0 <= self.cc0 <= 127:
         raise ValueError(f"Invalid CC0 value: {self.cc0}. Must be between 0 and 127.")
      if not 0 <= self.pgm <= 127:
         raise ValueError(f"Invalid program value: {self.pgm}. Must be between 0 and 127.")

      # Validate required string fields
      if not self.pack:
         raise ValueError("Pack name cannot be empty")
      if not self.type:
         raise ValueError("Preset type cannot be empty")
      if not self.preset:
         raise ValueError("Preset name cannot be empty")

   @property
   def preset_type_enum(self) -> Optional[PresetType]:
      """Get the PresetType enum for this preset's type."""
      return PresetType.from_string(self.type)

   @property
   def display_chars(self) -> str:
      """Get formatted string of characteristics for display."""
      return ", ".join(self.chars) if self.chars else ""

   @property
   def has_chars(self) -> bool:
      """Check if preset has any characteristics."""
      return len(self.chars) > 0

   @property
   def char_set(self) -> Set[str]:
      """Get characteristics as a set for efficient comparison."""
      return set(self.chars)

   def matches_search(self, search_term: str) -> bool:
      """
      Check if preset matches search term.

      Supports AND/OR operators where AND has higher precedence.

      Args:
          search_term: Search string with optional AND/OR operators

      Returns:
          True if preset matches search criteria
      """
      if not search_term:
         return True

      # Split by OR (lowest precedence)
      or_clauses = [clause.strip() for clause in search_term.split(" OR ")]

      # For each OR clause, check if all AND terms match
      for clause in or_clauses:
         and_terms = [term.strip() for term in clause.split(" AND ")]
         if all(self._matches_single_term(term) for term in and_terms):
            return True

      return False

   def _matches_single_term(self, term: str) -> bool:
      """
      Check if preset matches a single search term.

      Args:
          term: Single search term (no operators)

      Returns:
          True if term is found in preset name (case-insensitive)
      """
      term_lower = term.lower()
      return term_lower in self.preset.lower()

   def matches_pack_filter(self, packs: Set[str]) -> bool:
      """
      Check if preset matches pack filter.

      Args:
          packs: Set of pack names to match

      Returns:
          True if preset's pack is in the filter set or filter is empty
      """
      return not packs or self.pack in packs

   def matches_type_filter(self, types: Set[str]) -> bool:
      """
      Check if preset matches type filter.

      Args:
          types: Set of type names to match

      Returns:
          True if preset's type is in the filter set or filter is empty
      """
      return not types or self.type in types

   def matches_char_filter(self, chars: Set[str]) -> bool:
      """
      Check if preset matches character filter.

      Args:
          chars: Set of character tags to match

      Returns:
          True if preset has any of the filter chars or filter is empty
      """
      return not chars or bool(self.char_set & chars)

   def to_tuple(self) -> tuple:
      """
      Convert preset to tuple format for table display.

      Returns:
          Tuple of (pack, type, cc0, pgm, preset, chars_display)
      """
      return (self.pack, self.type, self.cc0, self.pgm, self.preset, self.display_chars)

   def to_dict(self) -> Dict[str, Any]:
      """
      Convert preset to dictionary for serialization.

      Returns:
          Dictionary representation of preset
      """
      return {
         "pack": self.pack,
         "type": self.type,
         "cc0": self.cc0,
         "pgm": self.pgm,
         "preset": self.preset,
         "chars": self.chars.copy(),  # Create a copy to maintain immutability
      }

   @classmethod
   def from_dict(cls, data: Dict[str, Any]) -> "Preset":
      """
      Create Preset instance from dictionary.

      Args:
          data: Dictionary containing preset data

      Returns:
          New Preset instance

      Raises:
          KeyError: If required fields are missing
          ValueError: If data validation fails
      """
      return cls(
         pack=data["pack"],
         type=data["type"],
         cc0=data["cc0"],
         pgm=data["pgm"],
         preset=data["preset"],
         chars=data.get("chars", []).copy(),  # Create a copy to maintain immutability
      )

   def get_field_widths(self) -> List[int]:
      """
      Get the display width of each field.

      Returns:
          List of character widths for each field
      """
      return [len(self.pack), len(self.type), len(str(self.cc0)), len(str(self.pgm)), len(self.preset), len(self.display_chars)]

   def __str__(self) -> str:
      """String representation for logging and debugging."""
      return f"Preset({self.pack}/{self.preset} - CC0:{self.cc0}, PGM:{self.pgm})"

   def __repr__(self) -> str:
      """Detailed representation for debugging."""
      return f"Preset(pack='{self.pack}', type='{self.type}', cc0={self.cc0}, pgm={self.pgm}, preset='{self.preset}', chars={self.chars!r})"

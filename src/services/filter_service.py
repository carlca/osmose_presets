"""
Filter service for managing application-wide filter state.

This module provides a centralized service for managing all filter state,
making it easy to coordinate filter changes across multiple UI components.
"""

from typing import Set, Optional, List, Callable
from dataclasses import dataclass, field
from textual import log


@dataclass
class FilterState:
   """Current filter selections."""

   packs: Set[str] = field(default_factory=set)
   types: Set[str] = field(default_factory=set)
   chars: Set[str] = field(default_factory=set)
   search_term: str = ""

   def clear(self):
      """Clear all filters."""
      self.packs.clear()
      self.types.clear()
      self.chars.clear()
      self.search_term = ""

   def is_active(self) -> bool:
      """Check if any filters are active."""
      return bool(self.packs or self.types or self.chars or self.search_term)

   def copy(self) -> "FilterState":
      """Create a deep copy of the filter state."""
      return FilterState(packs=self.packs.copy(), types=self.types.copy(), chars=self.chars.copy(), search_term=self.search_term)

   def __repr__(self) -> str:
      """String representation for debugging."""
      active_filters = []
      if self.packs:
         active_filters.append(f"packs={len(self.packs)}")
      if self.types:
         active_filters.append(f"types={len(self.types)}")
      if self.chars:
         active_filters.append(f"chars={len(self.chars)}")
      if self.search_term:
         active_filters.append(f"search='{self.search_term[:20]}...'")

      if active_filters:
         return f"FilterState({', '.join(active_filters)})"
      return "FilterState(empty)"


class FilterService:
   """
   Manages application-wide filter state.

   This service provides a centralized location for filter state management,
   allowing multiple UI components to stay synchronized without complex
   inter-component communication.
   """

   def __init__(self):
      """Initialize the filter service."""
      self.state = FilterState()
      self._listeners: List[Callable[[FilterState], None]] = []
      log("FilterService initialized")

   def set_pack_filter(self, packs: Set[str]) -> None:
      """
      Update pack filter.

      Args:
          packs: Set of pack names to filter by
      """
      if self.state.packs != packs:
         self.state.packs = packs.copy()
         log(f"Pack filter updated: {len(packs)} packs selected")
         self._notify_listeners()

   def set_type_filter(self, types: Set[str]) -> None:
      """
      Update type filter.

      Args:
          types: Set of preset types to filter by
      """
      if self.state.types != types:
         self.state.types = types.copy()
         log(f"Type filter updated: {len(types)} types selected")
         self._notify_listeners()

   def set_char_filter(self, chars: Set[str]) -> None:
      """
      Update character filter.

      Args:
          chars: Set of character tags to filter by
      """
      if self.state.chars != chars:
         self.state.chars = chars.copy()
         log(f"Character filter updated: {len(chars)} chars selected")
         self._notify_listeners()

   def set_search(self, search_term: str) -> None:
      """
      Update search term.

      Args:
          search_term: Search term for preset names
      """
      normalized_term = search_term.strip()
      if self.state.search_term != normalized_term:
         self.state.search_term = normalized_term
         log(f"Search term updated: '{normalized_term}'")
         self._notify_listeners()

   def toggle_pack(self, pack: str) -> None:
      """
      Toggle a single pack in the filter.

      Args:
          pack: Pack name to toggle
      """
      if pack in self.state.packs:
         self.state.packs.remove(pack)
      else:
         self.state.packs.add(pack)
      log(f"Pack '{pack}' toggled")
      self._notify_listeners()

   def toggle_type(self, type_name: str) -> None:
      """
      Toggle a single type in the filter.

      Args:
          type_name: Type name to toggle
      """
      if type_name in self.state.types:
         self.state.types.remove(type_name)
      else:
         self.state.types.add(type_name)
      log(f"Type '{type_name}' toggled")
      self._notify_listeners()

   def toggle_char(self, char: str) -> None:
      """
      Toggle a single character tag in the filter.

      Args:
          char: Character tag to toggle
      """
      if char in self.state.chars:
         self.state.chars.remove(char)
      else:
         self.state.chars.add(char)
      log(f"Character '{char}' toggled")
      self._notify_listeners()

   def clear_filters(self) -> None:
      """Clear all filters."""
      if self.state.is_active():
         self.state.clear()
         log("All filters cleared")
         self._notify_listeners()

   def clear_pack_filter(self) -> None:
      """Clear only the pack filter."""
      if self.state.packs:
         self.state.packs.clear()
         log("Pack filter cleared")
         self._notify_listeners()

   def clear_type_filter(self) -> None:
      """Clear only the type filter."""
      if self.state.types:
         self.state.types.clear()
         log("Type filter cleared")
         self._notify_listeners()

   def clear_char_filter(self) -> None:
      """Clear only the character filter."""
      if self.state.chars:
         self.state.chars.clear()
         log("Character filter cleared")
         self._notify_listeners()

   def clear_search(self) -> None:
      """Clear only the search term."""
      if self.state.search_term:
         self.state.search_term = ""
         log("Search term cleared")
         self._notify_listeners()

   def add_listener(self, callback: Callable[[FilterState], None]) -> None:
      """
      Add a callback for filter changes.

      Args:
          callback: Function to call when filters change.
                   Will receive the current FilterState as argument.
      """
      if callback not in self._listeners:
         self._listeners.append(callback)
         log(f"Filter listener added (total: {len(self._listeners)})")

   def remove_listener(self, callback: Callable[[FilterState], None]) -> None:
      """
      Remove a previously added listener.

      Args:
          callback: The callback function to remove
      """
      if callback in self._listeners:
         self._listeners.remove(callback)
         log(f"Filter listener removed (remaining: {len(self._listeners)})")

   def _notify_listeners(self) -> None:
      """Notify all listeners of filter change."""
      state_copy = self.state.copy()
      for callback in self._listeners:
         try:
            callback(state_copy)
         except Exception as e:
            log(f"Error in filter listener: {e}")

   def get_state_summary(self) -> str:
      """
      Get a human-readable summary of the current filter state.

      Returns:
          String describing the active filters
      """
      if not self.state.is_active():
         return "No filters active"

      parts = []
      if self.state.packs:
         parts.append(f"{len(self.state.packs)} pack(s)")
      if self.state.types:
         parts.append(f"{len(self.state.types)} type(s)")
      if self.state.chars:
         parts.append(f"{len(self.state.chars)} character(s)")
      if self.state.search_term:
         parts.append(f"search: '{self.state.search_term}'")

      return "Active filters: " + ", ".join(parts)

   def __repr__(self) -> str:
      """String representation for debugging."""
      return f"FilterService({self.state}, listeners={len(self._listeners)})"

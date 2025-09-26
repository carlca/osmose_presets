"""
Tests for the FilterService class.

This module contains comprehensive tests for the FilterService,
ensuring proper filter state management and listener notifications.
"""

import pytest
from unittest.mock import Mock, call
from src.services.filter_service import FilterService, FilterState


class TestFilterState:
   """Tests for the FilterState dataclass."""

   def test_initial_state_is_empty(self):
      """Test that FilterState initializes with empty filters."""
      state = FilterState()
      assert state.packs == set()
      assert state.types == set()
      assert state.chars == set()
      assert state.search_term == ""
      assert not state.is_active()

   def test_is_active_with_packs(self):
      """Test that is_active returns True when packs are set."""
      state = FilterState()
      state.packs = {"factory", "user"}
      assert state.is_active()

   def test_is_active_with_types(self):
      """Test that is_active returns True when types are set."""
      state = FilterState()
      state.types = {"bass", "lead"}
      assert state.is_active()

   def test_is_active_with_chars(self):
      """Test that is_active returns True when chars are set."""
      state = FilterState()
      state.chars = {"warm", "bright"}
      assert state.is_active()

   def test_is_active_with_search(self):
      """Test that is_active returns True when search term is set."""
      state = FilterState()
      state.search_term = "piano"
      assert state.is_active()

   def test_clear_resets_all_filters(self):
      """Test that clear() resets all filters to initial state."""
      state = FilterState()
      state.packs = {"factory"}
      state.types = {"bass"}
      state.chars = {"warm"}
      state.search_term = "test"

      state.clear()

      assert state.packs == set()
      assert state.types == set()
      assert state.chars == set()
      assert state.search_term == ""
      assert not state.is_active()

   def test_copy_creates_independent_copy(self):
      """Test that copy() creates an independent copy of the state."""
      state = FilterState()
      state.packs = {"factory"}
      state.types = {"bass"}

      copy = state.copy()

      # Modify original
      state.packs.add("user")
      state.types.clear()

      # Copy should be unchanged
      assert copy.packs == {"factory"}
      assert copy.types == {"bass"}


class TestFilterService:
   """Tests for the FilterService class."""

   def test_initial_state(self):
      """Test that FilterService initializes with empty state."""
      service = FilterService()
      assert not service.state.is_active()
      assert service.state.packs == set()
      assert service.state.types == set()
      assert service.state.chars == set()
      assert service.state.search_term == ""

   def test_set_pack_filter(self):
      """Test setting pack filter."""
      service = FilterService()
      service.set_pack_filter({"factory", "user"})

      assert service.state.packs == {"factory", "user"}

   def test_set_pack_filter_with_copy(self):
      """Test that set_pack_filter copies the input set."""
      service = FilterService()
      packs = {"factory", "user"}
      service.set_pack_filter(packs)

      # Modify original
      packs.add("custom")

      # Service state should be unchanged
      assert service.state.packs == {"factory", "user"}

   def test_set_type_filter(self):
      """Test setting type filter."""
      service = FilterService()
      service.set_type_filter({"bass", "lead"})

      assert service.state.types == {"bass", "lead"}

   def test_set_char_filter(self):
      """Test setting character filter."""
      service = FilterService()
      service.set_char_filter({"warm", "bright"})

      assert service.state.chars == {"warm", "bright"}

   def test_set_search(self):
      """Test setting search term."""
      service = FilterService()
      service.set_search("  piano  ")

      # Should be trimmed
      assert service.state.search_term == "piano"

   def test_toggle_pack(self):
      """Test toggling a pack in the filter."""
      service = FilterService()

      # Add a pack
      service.toggle_pack("factory")
      assert "factory" in service.state.packs

      # Remove the pack
      service.toggle_pack("factory")
      assert "factory" not in service.state.packs

   def test_toggle_type(self):
      """Test toggling a type in the filter."""
      service = FilterService()

      # Add a type
      service.toggle_type("bass")
      assert "bass" in service.state.types

      # Remove the type
      service.toggle_type("bass")
      assert "bass" not in service.state.types

   def test_toggle_char(self):
      """Test toggling a character tag in the filter."""
      service = FilterService()

      # Add a char
      service.toggle_char("warm")
      assert "warm" in service.state.chars

      # Remove the char
      service.toggle_char("warm")
      assert "warm" not in service.state.chars

   def test_clear_filters(self):
      """Test clearing all filters."""
      service = FilterService()
      service.set_pack_filter({"factory"})
      service.set_type_filter({"bass"})
      service.set_char_filter({"warm"})
      service.set_search("test")

      service.clear_filters()

      assert not service.state.is_active()
      assert service.state.packs == set()
      assert service.state.types == set()
      assert service.state.chars == set()
      assert service.state.search_term == ""

   def test_clear_pack_filter(self):
      """Test clearing only the pack filter."""
      service = FilterService()
      service.set_pack_filter({"factory"})
      service.set_type_filter({"bass"})

      service.clear_pack_filter()

      assert service.state.packs == set()
      assert service.state.types == {"bass"}  # Should be unchanged

   def test_clear_type_filter(self):
      """Test clearing only the type filter."""
      service = FilterService()
      service.set_pack_filter({"factory"})
      service.set_type_filter({"bass"})

      service.clear_type_filter()

      assert service.state.packs == {"factory"}  # Should be unchanged
      assert service.state.types == set()

   def test_clear_char_filter(self):
      """Test clearing only the character filter."""
      service = FilterService()
      service.set_char_filter({"warm"})
      service.set_type_filter({"bass"})

      service.clear_char_filter()

      assert service.state.chars == set()
      assert service.state.types == {"bass"}  # Should be unchanged

   def test_clear_search(self):
      """Test clearing only the search term."""
      service = FilterService()
      service.set_search("test")
      service.set_pack_filter({"factory"})

      service.clear_search()

      assert service.state.search_term == ""
      assert service.state.packs == {"factory"}  # Should be unchanged

   def test_listener_notification(self):
      """Test that listeners are notified on filter changes."""
      service = FilterService()
      listener = Mock()
      service.add_listener(listener)

      service.set_pack_filter({"factory"})

      listener.assert_called_once()
      # Check that a copy of the state was passed
      call_args = listener.call_args[0][0]
      assert isinstance(call_args, FilterState)
      assert call_args.packs == {"factory"}

   def test_multiple_listeners(self):
      """Test that multiple listeners are all notified."""
      service = FilterService()
      listener1 = Mock()
      listener2 = Mock()

      service.add_listener(listener1)
      service.add_listener(listener2)

      service.set_pack_filter({"factory"})

      assert listener1.call_count == 1
      assert listener2.call_count == 1

   def test_no_duplicate_listeners(self):
      """Test that the same listener isn't added twice."""
      service = FilterService()
      listener = Mock()

      service.add_listener(listener)
      service.add_listener(listener)  # Try to add again

      service.set_pack_filter({"factory"})

      # Should only be called once
      assert listener.call_count == 1

   def test_remove_listener(self):
      """Test removing a listener."""
      service = FilterService()
      listener1 = Mock()
      listener2 = Mock()

      service.add_listener(listener1)
      service.add_listener(listener2)
      service.remove_listener(listener1)

      service.set_pack_filter({"factory"})

      listener1.assert_not_called()
      listener2.assert_called_once()

   def test_no_notification_if_no_change(self):
      """Test that listeners aren't notified if filter doesn't actually change."""
      service = FilterService()
      listener = Mock()

      service.set_pack_filter({"factory"})
      service.add_listener(listener)
      service.set_pack_filter({"factory"})  # Same value

      listener.assert_not_called()

   def test_listener_exception_handling(self):
      """Test that exception in one listener doesn't affect others."""
      service = FilterService()

      bad_listener = Mock(side_effect=Exception("Test error"))
      good_listener = Mock()

      service.add_listener(bad_listener)
      service.add_listener(good_listener)

      service.set_pack_filter({"factory"})

      # Both should be called despite the exception
      bad_listener.assert_called_once()
      good_listener.assert_called_once()

   def test_get_state_summary_empty(self):
      """Test state summary when no filters are active."""
      service = FilterService()
      summary = service.get_state_summary()

      assert summary == "No filters active"

   def test_get_state_summary_with_filters(self):
      """Test state summary with various filters active."""
      service = FilterService()
      service.set_pack_filter({"factory", "user"})
      service.set_type_filter({"bass"})
      service.set_search("piano")

      summary = service.get_state_summary()

      assert "2 pack(s)" in summary
      assert "1 type(s)" in summary
      assert "search: 'piano'" in summary

   def test_clear_filters_no_notification_if_already_empty(self):
      """Test that clear_filters doesn't notify if filters are already empty."""
      service = FilterService()
      listener = Mock()
      service.add_listener(listener)

      service.clear_filters()

      listener.assert_not_called()

   def test_clear_specific_filter_no_notification_if_empty(self):
      """Test that clearing specific empty filters doesn't trigger notifications."""
      service = FilterService()
      listener = Mock()
      service.add_listener(listener)

      service.clear_pack_filter()
      service.clear_type_filter()
      service.clear_char_filter()
      service.clear_search()

      listener.assert_not_called()

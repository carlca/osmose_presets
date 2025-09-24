from textual.message import Message


class FilterSelectionChanged(Message):
   """Posted when the selection in a FilterSelector changes."""

   def __init__(self, filter_type: str, selected_filters: list[str]) -> None:
      self.filter_type = filter_type
      self.selected_filters = selected_filters
      super().__init__()


class SearchSubmitted(Message):
   """Posted when the user submits a search by pressing Enter in the search box."""

   def __init__(self, search_term: str) -> None:
      self.search_term = search_term
      super().__init__()


class RestorePreviousFocus(Message):
   """Posted when the user wants to restore focus to the previously focused widget."""
   pass

from textual.message import Message


class FilterSelectionChanged(Message):
   """posted when the selection in a FilterSelector changes"""

   def __init__(self, filter_type: str, selected_filters: list[str]) -> None:
      self.filter_type = filter_type
      self.selected_filters = selected_filters
      super().__init__()


class SearchSubmitted(Message):
   """posted when the user submits a search by pressing Enter in the search box"""

   def __init__(self, search_term: str) -> None:
      self.search_term = search_term
      super().__init__()


class RestorePreviousFocus(Message):
   """posted when the user wants to restore focus to the previously focused widget"""

   pass


class PresetSelected(Message):
   """posted when the user pressed <ENTER> on the PresetGrid"""

   def __init__(self, cc: int, pgm: int) -> None:
      # self.port = port
      self.cc = cc
      self.pgm = pgm
      super().__init__()

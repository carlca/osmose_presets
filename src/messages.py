from textual.message import Message
from textual.widget import Widget


class FilterSelectionChanged(Message):
   """Posted when the selection in a FilterSelector changes."""

   def __init__(self, filter_type: str, selected_filters: list[str]) -> None:
      self.filter_type = filter_type
      self.selected_filters = selected_filters
      super().__init__()

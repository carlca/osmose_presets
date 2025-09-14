from textual.message import Message
from textual.widget import Widget
from filters import Filters


class FocusNextContainer(Message):
   """Message to signal that focus should move to the next container."""

   def __init__(self, sender: Widget) -> None:
      self.sender = sender
      super().__init__()


class FocusPreviousContainer(Message):
   """Message to signal that focus should move to the previous container."""

   def __init__(self, sender: Widget) -> None:
      self.sender = sender
      super().__init__()


class FilterChanged(Message):
   """Posted when the selection in a FilterSelector changes."""

   def __init__(self, filter_type: "Filters", selected_filters: list[str]) -> None:
      self.filter_type = filter_type
      self.selected_filters = selected_filters
      super().__init__()

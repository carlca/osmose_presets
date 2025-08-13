from textual.message import Message
from textual.widget import Widget


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

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Button, Static
from textual import events
from textual.events import Focus as FocusEvent


class HeaderPanel(HorizontalGroup):
   def compose(self) -> ComposeResult:
      self.border_title = "MIDI input port"
      yield Button(" < ", classes="header-button bold-text", id="prev_port_button", flat=True)
      yield Button(" > ", classes="header-button bold-text", id="next_port_button", flat=True)
      yield Static("Osmose Port 2", classes="bold-text")

   def focus_first_button(self) -> None:
      """Focus the first button (prev port button)."""
      prev_button = self.query_one("#prev_port_button", Button)
      prev_button.focus()

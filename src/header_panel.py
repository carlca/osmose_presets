from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Static


class HeaderPanel(HorizontalGroup):
   def compose(self) -> ComposeResult:
      self.border_title = "MIDI input port"
      yield Static(" < ", classes="header-button bold-text", id="prev_port_button")
      yield Static(" > ", classes="header-button bold-text", id="next_port_button")
      yield Static("Osmose Port 2", classes="bold-text")

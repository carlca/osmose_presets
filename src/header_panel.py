
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Button, Static
from textual.events import Key
from textual import log
import mido
from helper_functions import Helper


class HeaderPanel(HorizontalGroup):
   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.ports = []
      self.current_port_index = 0
      self.port_display = None

   def on_mount(self) -> None:
      """Load MIDI ports when component is mounted."""
      try:
         self.ports = mido.get_input_names()
         if not self.ports:
            self.ports = ["No MIDI ports available"]
         log(self.ports)

         # Load saved MIDI port selection
         config = self.read_config()
         saved_port = config.get("selected_midi_port", "")

         # If there's a saved port and it exists in the current list of ports
         if saved_port and saved_port in self.ports:
            self.current_port_index = self.ports.index(saved_port)
            if self.port_display:
               self.port_display.update(self.get_current_port_name())
      except Exception as e:
         print(f"Error getting MIDI input ports: {e}")
         self.ports = ["Error loading MIDI ports"]

   def compose(self) -> ComposeResult:
      self.border_title = "MIDI input port"
      yield Button(" < ", classes="header-button bold-text", id="prev_port_button")
      yield Button(" > ", classes="header-button bold-text", id="next_port_button")
      self.port_display = Static(self.get_current_port_name(), classes="bold-text")
      yield self.port_display

   def get_current_port_name(self) -> str:
      """Get the name of the currently selected port."""
      if self.ports:
         return self.ports[self.current_port_index]
      return "No ports loaded"

   def read_config(self):
      """Read the config file."""
      return Helper.read_config()

   def save_selected_midi_port(self, port_name: str) -> None:
      """Save the selected MIDI port to the config file."""
      config = self.read_config()
      config["selected_midi_port"] = port_name
      Helper.write_config(config)

   def set_focus(self) -> None:
      """Focus the first button (prev port button)."""
      prev_button = self.query_one("#prev_port_button", Button)
      prev_button.focus()

   def on_button_pressed(self, event: Button.Pressed) -> None:
      """Handle button presses for port navigation."""
      # Only process port navigation if HeaderPanel is in focused state
      if "focused" in self.classes:
         if event.button.id == "next_port_button":
            self.next_port()
         elif event.button.id == "prev_port_button":
            self.prev_port()

   def next_port(self) -> None:
      """Select the next MIDI port."""
      if len(self.ports) > 1:
         self.current_port_index = (self.current_port_index + 1) % len(self.ports)
         if self.port_display:
            self.port_display.update(self.get_current_port_name())
            self.save_selected_midi_port(self.get_current_port_name())

   def prev_port(self) -> None:
      """Select the previous MIDI port."""
      if len(self.ports) > 1:
         self.current_port_index = (self.current_port_index - 1) % len(self.ports)
         if self.port_display:
            self.port_display.update(self.get_current_port_name())
            self.save_selected_midi_port(self.get_current_port_name())

   def on_key(self, event: Key) -> None:
      if event.character in ("<",",", ">","."):
         if event.character in ("<",","):
            self.prev_port()
         elif event.character in (">","."):
            self.next_port()
         event.stop()

from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Button, Static, Input
from textual.events import Key
from textual import log, on
import mido
from helper_functions import Helper
from messages import SearchSubmitted, RestorePreviousFocus


class MidiPortSelector(Container):
   """Left side container for MIDI port selection."""

   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.ports = []
      self.current_port_index = 0
      self.port_display = None
      self.midi_port_name = ""

   def on_mount(self) -> None:
      """Load MIDI ports when component is mounted."""
      try:
         self.ports = mido.get_input_names()
         if not self.ports:
            self.ports = ["No MIDI ports available"]

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
      with Horizontal(classes="midi-port-controls"):
         yield Button(" < ", classes="header-button bold-text", id="prev_port_button")
         yield Button(" > ", classes="header-button bold-text", id="next_port_button")
         self.port_display = Static(self.get_current_port_name(), classes="bold-text")
         yield self.port_display

   def get_current_port_name(self) -> str:
      """Get the name of the currently selected port."""
      if self.ports:
         self.midi_port_name = self.ports[self.current_port_index]
         return self.midi_port_name
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
      # Only process port navigation if this widget is in focused state
      if "focused" in self.classes:
         if event.button.id == "next_port_button":
            self.next_port()
         elif event.button.id == "prev_port_button":
            self.prev_port()
         event.stop()

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

   def on_click(self, event) -> None:
      """Handle click events to set focus state."""
      # Remove all other focused classes and add focus to this widget
      if self.app:
         self.app.remove_all_focused_border_titles()
         self.add_class("focused")
         self.set_focus()
      event.stop()

   def on_key(self, event: Key) -> None:
      """Handle key events for port navigation."""
      if "focused" in self.classes:
         if event.character in ("<", ",", ">", "."):
            if event.character in ("<", ","):
               self.prev_port()
            elif event.character in (">", "."):
               self.next_port()
            event.stop()


class SearchBox(Container):
   """Right side container for search functionality."""

   def compose(self) -> ComposeResult:
      self.border_title = "Search"
      yield Input(placeholder="Enter search term...", id="search-input")

   @on(Input.Submitted, "#search-input")
   def on_search_input_submitted(self, event: Input.Submitted) -> None:
      """Handle Enter key press in the search input."""
      search_term = event.value
      self.post_message(SearchSubmitted(search_term))

   def on_key(self, event: Key) -> None:
      """Handle key events in the search box."""
      if event.key == "escape":
         # Clear the search input field
         search_input = self.query_one("#search-input", Input)
         search_input.value = ""
         self.post_message(RestorePreviousFocus())
         self.post_message(SearchSubmitted(""))
         event.stop()


class HeaderPanel(Horizontal):
   """Main header panel containing both MIDI port selector and search box."""

   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.midi_selector = None

   def compose(self) -> ComposeResult:
      self.midi_selector = MidiPortSelector(id="midi-port-selector", classes="header-box")
      yield self.midi_selector
      yield SearchBox(id="search-box", classes="header-box")

   def set_focus(self) -> None:
      """Focus the midi port selector when header panel gets focus."""
      if self.midi_selector:
         self.midi_selector.set_focus()

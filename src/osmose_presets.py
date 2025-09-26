from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer
from textual import on
from textual import log
from preset_grid import PresetGrid
from header_panel import HeaderPanel
from filter_selector import FilterSelector
from filters import Filters
from messages import FilterSelectionChanged, SearchSubmitted, RestorePreviousFocus, PresetSelected
from midi_controller import MidiController
from services.app_services import AppServices


class Sidebar(VerticalScroll):
   def get_filter_selectors(self) -> list[FilterSelector]:
      return list(self.query(FilterSelector))

   @on(FilterSelectionChanged)
   def handle_filter_changed(self, message: FilterSelectionChanged) -> None:
      preset_grid = self.app.query_one("#preset-grid", PresetGrid)
      preset_grid.set_filter(message.filter_type, message.selected_filters)


class OsmosePresetsApp(App):
   TITLE = "Osmose Presets"

   CSS_PATH = "osmose_presets.tcss"

   def __init__(self):
      super().__init__()
      self.previous_focus_id = "#pack-container"
      # Initialize services (Stage 1 - just create them, don't use them yet)
      self.services = AppServices()

   BINDINGS = [
      ("q", "quit_app", "Quit"),
      ("1", "focus_midi_input_port", "MIDI input port"),
      ("2", "focus_pack_filter_selector", "pack"),
      ("3", "focus_type_filter_selector", "type"),
      ("4", "focus_char_filter_selector", "character"),
      ("5", "focus_preset_grid", "presets"),
      ("s", "focus_search_box", "Search"),
   ]

   def on_mount(self) -> None:
      self.focus_filter_selector("#pack-container")

   def compose(self) -> ComposeResult:
      yield Header()
      yield Footer()
      # The top-level container stacks the header and main area vertically
      with Vertical():
         yield HeaderPanel(id="header-panel")
         # The main container holds the two columns side-by-side
         with Horizontal(id="main-container"):
            # The left sidebar, which contains two sections
            with Sidebar(id="left-sidebar"):
               yield FilterSelector(Filters.PACK, True, id="pack-container")
               yield FilterSelector(Filters.TYPE, True, id="type-container")
               yield FilterSelector(Filters.CHAR, True, id="char-container")
            # The right-hand data viewer (scrollable and fills remaining horizontal space)
            with VerticalScroll(id="data-viewer"):
               yield PresetGrid(id="preset-grid")

   def action_quit_app(self) -> None:
      ### An action to quit the app.###
      print("q pressed")
      self.exit()

   def remove_all_focused_border_titles(self) -> None:
      # Store the current focused widget ID before removing focus
      for widget in self.query(".focused"):
         if widget.id and widget.id != "search-box":
            self.previous_focus_id = f"#{widget.id}"
         widget.remove_class("focused")

   def set_focus_to_one_border_title(self, id: str) -> None:
      widget = self.app.query_one(id)
      if widget:
         widget.add_class("focused")
         widget.set_focus()

   def action_focus_midi_input_port(self) -> None:
      self.remove_all_focused_border_titles()
      self.set_focus_to_one_border_title("#midi-port-selector")

   def action_focus_pack_filter_selector(self) -> None:
      self.focus_filter_selector("#pack-container")

   def action_focus_type_filter_selector(self) -> None:
      self.focus_filter_selector("#type-container")

   def action_focus_char_filter_selector(self) -> None:
      self.focus_filter_selector("#char-container")

   def focus_filter_selector(self, id: str) -> None:
      self.remove_all_focused_border_titles()
      self.set_focus_to_one_border_title(id)

   def action_focus_preset_grid(self) -> None:
      self.remove_all_focused_border_titles()
      self.set_focus_to_one_border_title("#preset-grid")

   def action_focus_search_box(self) -> None:
      # Store current focus before switching to search
      for widget in self.query(".focused"):
         if widget.id and widget.id != "search-box":
            self.previous_focus_id = f"#{widget.id}"
      self.remove_all_focused_border_titles()
      search_box = self.query_one("#search-box")
      if search_box:
         search_box.add_class("focused")
         search_input = search_box.query_one("#search-input")
         if search_input:
            search_input.focus()

   @on(SearchSubmitted)
   def handle_search_submitted(self, message: SearchSubmitted) -> None:
      """Handle search submission from the search box."""
      preset_grid = self.app.query_one("#preset-grid", PresetGrid)
      preset_grid.set_search_filter(message.search_term)
      self.remove_all_focused_border_titles()
      self.set_focus_to_one_border_title("#preset-grid")

   @on(RestorePreviousFocus)
   def handle_restore_focus(self, message: RestorePreviousFocus) -> None:
      """Handle request to restore focus to previous widget."""
      self.restore_previous_focus()

   def restore_previous_focus(self) -> None:
      """Restore focus to the previously focused widget."""
      self.remove_all_focused_border_titles()
      if self.previous_focus_id:
         try:
            widget = self.query_one(self.previous_focus_id)
            if widget:
               widget.add_class("focused")
               widget.set_focus()
         except Exception:
            # If the previous widget doesn't exist, default to pack filter
            self.set_focus_to_one_border_title("#pack-container")

   @on(PresetSelected)
   def preset_selected(self, message: PresetSelected) -> None:
      header_panel = self.app.query_one("#header-panel", HeaderPanel)
      MidiController.send_preset_change(header_panel.midi_selector.midi_port_name, message.cc, message.pgm)


if __name__ == "__main__":
   app = OsmosePresetsApp()
   app.run()

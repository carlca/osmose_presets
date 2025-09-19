from textual.app import App, ComposeResult  # , RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Header, Footer
from textual.message import Message  # <-- Import Message
from textual import on  # <-- Import on decorator
from textual import log
from preset_data import PresetData, Preset
from preset_grid import PresetGrid
from header_panel import HeaderPanel
from filter_selector import FilterSelector
from filters import Filters
from messages import FilterSelectionChanged


class Sidebar(Vertical):
   def get_filter_selectors(self) -> list[FilterSelector]:
      return list(self.query(FilterSelector))

   @on(FilterSelectionChanged)
   def handle_filter_changed(self, message: FilterSelectionChanged) -> None:
      preset_grid = self.app.query_one("#preset-grid", PresetGrid)
      preset_grid.set_filter(message.filter_type, message.selected_filters)

class OsmosePresetsApp(App):
   # Link to the CSS file
   CSS_PATH = "osmose_presets.tcss"
   BINDINGS = [
      ("q", "quit_app", "Quit"),
      ("1", "focus_midi_input_port", "MIDI input port"),
      ("2", "focus_pack_filter_selector", "pack"),
      ("3", "focus_type_filter_selector", "type"),
      ("4", "focus_preset_grid", "presets")
   ]

   def compose(self) -> ComposeResult:
      """create the layout and widgets for the app"""
      yield Header()
      yield Footer()
      # The top-level container stacks the header and main area vertically
      with Vertical():
         yield HeaderPanel(id="header-panel")
         # The main container holds the two columns side-by-side
         with Horizontal(id="main-container"):
            # The left sidebar, which contains two sections
            with Sidebar(id="left-sidebar"):
               yield FilterSelector(Filters.PACK, id="pack-container")
               yield FilterSelector(Filters.TYPE, id="type-container")
            # The right-hand data viewer (scrollable and fills remaining horizontal space)
            with VerticalScroll(id="data-viewer"):
               yield PresetGrid(id="preset-grid")

   def action_quit_app(self) -> None:
      ### An action to quit the app.###
      print("q pressed")
      self.exit()

   def action_focus_pack_filter_selector(self) -> None:
      self.focus_filter_selector("#pack-container")

   def action_focus_type_filter_selector(self) -> None:
      self.focus_filter_selector("#type-container")

   def focus_filter_selector(self, id: str) -> None:
      filter = self.app.query_one(id)
      if filter:
         filter.set_focus()

   def action_focus_preset_grid(self) -> None:
      grid = self.app.query_one("#preset-grid")
      if grid:
         log("grid.set_focus()")
         grid.set_focus()

if __name__ == "__main__":
   app = OsmosePresetsApp()
   app.run()

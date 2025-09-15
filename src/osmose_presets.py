from textual.app import App, ComposeResult  # , RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Header, Footer
from textual.message import Message  # <-- Import Message
from textual import on  # <-- Import on decorator
from textual import log
from preset_data import PresetData
from header_panel import HeaderPanel
from filter_selector import FilterSelector
from filters import Filters
from messages import FilterSelectionChanged, FocusNextContainer, FocusPreviousContainer


class Sidebar(Vertical):
   def get_filter_selectors(self) -> list[FilterSelector]:
      """Returns a list of the FilterSelector children."""
      return list(self.query(FilterSelector))

   @on(FilterSelectionChanged)
   def handle_filter_changed(self, message: FilterSelectionChanged) -> None:
      """ handle a change in the filter selection  """
      log(message.filter_type)
      log(message.selected_filters)

   @on(FocusNextContainer)
   def handle_focus_next(self, message: FocusNextContainer) -> None:
      """ handle request to focus the next container """
      selectors = self.get_filter_selectors()
      try:
         current_index = selectors.index(message.sender)
         next_index = (current_index + 1) % len(selectors)
         selectors[next_index].focus_first()
      except ValueError:
         pass  # Sender not found in this container

   @on(FocusPreviousContainer)
   def handle_focus_previous(self, message: FocusPreviousContainer) -> None:
      """ handle request to focus the previous container """
      selectors = self.get_filter_selectors()
      try:
         current_index = selectors.index(message.sender)
         next_index = (current_index - 1 + len(selectors)) % len(selectors)
         selectors[next_index].focus_last()
      except ValueError:
         pass  # Sender not found in this container


class OsmosePresetsApp(App):
   # Link to the CSS file
   CSS_PATH = "osmose_presets.tcss"
   BINDINGS = [
      ("d", "toggle_dark", "Toggle dark mode"),
      ("q", "quit_app", "Quit"),
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
               for i in range(30):
                  yield Static(f"Data Item #{i + 1}")

   def action_toggle_dark(self) -> None:
      ### an action to toggle dark mode ###
      self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

   def action_quit_app(self) -> None:
      ### An action to quit the app.###
      print("q pressed")
      self.exit()


if __name__ == "__main__":
   app = OsmosePresetsApp()
   app.run()

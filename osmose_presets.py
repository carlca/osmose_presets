from textual.app import App, ComposeResult  # , RenderResult
from textual.containers import Horizontal, Vertical, HorizontalGroup, VerticalScroll
from textual.widgets import Button, Static, Checkbox, Placeholder, Header, Footer

# from textual.reactive import reactive
# from textual.widget import Widget
from preset_data import PresetData
from filters import Filters


class HeaderPanel(HorizontalGroup):
   def compose(self) -> ComposeResult:
      # Create the widget first
      # header_label = Static("MIDI Input Port")
      # # Set its width directly
      # header_label.styles.width = 30
      # Now, yield the widget
      # yield header_label
      yield Static("MIDI Input Port", classes="plain-text")
      # yield Button("<", id="prev_port_button")
      # yield Button(">", id="next_port_button")
      # The NEW lines using Static widgets
      yield Static(" < ", classes="header-button bold-text", id="prev_port_button")
      yield Static(" > ", classes="header-button bold-text", id="next_port_button")
      yield Static("Osmose Port 2", classes="bold-text")


class FilterSelector(Vertical):
   def __init__(self, filter, **kwargs):
      super().__init__(**kwargs)
      self.filter = filter

   def compose(self) -> ComposeResult:
      yield Static("pack" if self.filter == Filters.PACK else "type")
      yield Checkbox("all", classes="compact")
      filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()
      for filter in filter_names:
         yield Checkbox(filter, classes="compact")


class OsmosePresetsApp(App):
   """
   A Textual app demonstrating a two-column layout with a fixed sidebar
   and a flexible content area.
   """

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
            with Vertical(id="left-sidebar"):
               yield FilterSelector(Filters.PACK, id="pack-container")
               yield FilterSelector(Filters.TYPE, id="type-container")
            # The right-hand data viewer (scrollable and fills remaining horizontal space)
            with VerticalScroll(id="data-viewer"):
               for i in range(30):
                  yield Placeholder(f"Data Item #{i + 1}")

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

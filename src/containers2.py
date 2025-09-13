from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static, Checkbox


class ContainerApp(App):
   """A simple app to play with containers."""

   CSS_PATH = "containers2.tcss"

   def compose(self) -> ComposeResult:
      # The main vertical layout for the whole app
      with Vertical(id="app-container"):
         # The top bar for the port selector
         with Horizontal(id="port-selector"):
            yield Button("MIDI Input Port")
            yield Static("Osmose Port 2")

         # A vertical container for the main content area
         with Vertical(id="main-content"):
            # The "pack" section
            with Vertical(id="pack-container"):
               yield Static("pack")
               yield Checkbox("all", classes="compact")
               yield Checkbox("factory", classes="compact")
               yield Checkbox("expansion_01", classes="compact")

            # The "type" section, which will fill remaining space
            with Vertical(id="type-container"):
               yield Static("type")
               yield Checkbox("all", classes="compact")
               yield Checkbox("bass", classes="compact")
               yield Checkbox("bowed", classes="compact")
               yield Checkbox("brass", classes="compact")
               yield Checkbox("elec piano", classes="compact")
               yield Checkbox("flute reeds", classes="compact")
               yield Checkbox("keys", classes="compact")
               yield Checkbox("lead", classes="compact")
               yield Checkbox("mallets", classes="compact")
               yield Checkbox("organ", classes="compact")
               yield Checkbox("pads", classes="compact")
               yield Checkbox("perc", classes="compact")
               yield Checkbox("plucked", classes="compact")
               yield Checkbox("sfx", classes="compact")


if __name__ == "__main__":
   app = ContainerApp()
   app.run()

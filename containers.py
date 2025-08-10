from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Placeholder, Static, Button, Checkbox


class ContainerApp(App):
   ### simple app to play with containers ###
   CSS_PATH = "containers.tcss"

   def compose(self) -> ComposeResult:
      with Vertical():  # app
         with Horizontal():  # port selector
            yield Button("MIDI Input Port")
            yield Static("Osmose Port 2")
         with Horizontal():  # filter selectors
            with Vertical():  # pack filter selector
               with Vertical():  # pack filter header a
                  yield Static("pack")
                  with Vertical():  # pack filter all + variable number of packs
                     yield Checkbox("all", classes="compact")
                     yield Checkbox("factory", classes="compact")
                     yield Checkbox("expansion_01", classes="compact")
               with Vertical():  # type filter selectot
                  yield Static("type")
                  with Vertical():  # type filter all + variable number of packs
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

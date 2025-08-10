from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox, Static


class CompactCheckboxApp(App):
   """A simple app to show a 1-cell high checkbox."""

   # Embed the TCSS directly into the app
   CSS = """
    Screen {
        align: center middle;
    }

    #default-checkbox {
        /* Default height for comparison */
        margin-bottom: 1;
    }

    #compact-checkbox {
        height: 1; /* This is the key property */
        border: none; /* Optional: removes the border for a cleaner look */
    }
    """

   def compose(self) -> ComposeResult:
      yield Vertical(
         Static("Default Checkbox:"),
         Checkbox("Default", id="default-checkbox"),
         Static("\nCompact Checkbox (height: 1):"),
         Checkbox("Compact", id="compact-checkbox"),
      )


if __name__ == "__main__":
   app = CompactCheckboxApp()
   app.run()

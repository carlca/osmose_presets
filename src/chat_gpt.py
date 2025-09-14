from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
   def compose(self) -> ComposeResult:
      table = DataTable()
      # Add columns with specific alignment
      table.add_column("Left Aligned", key="left", width=20, align="left")
      table.add_column("Centered", key="center", width=20, align="center")
      table.add_column("Right Aligned", key="right", width=20, align="right")

      # Add some rows
      table.add_row("Apple", "Banana", "Cherry")
      table.add_row("Dog", "Elephant", "Fox")

      yield table


if __name__ == "__main__":
   TableApp().run()

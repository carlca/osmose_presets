from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, DataTable


class TestDataTableApp(App):
    TITLE = "DataTable Focus Test"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal():
            with Vertical():
                yield DataTable(id="small-table")
            with Vertical():
                yield DataTable(id="large-table")

    def on_mount(self) -> None:
        # Populate small table with 10 rows
        small_table = self.query_one("#small-table", DataTable)
        small_table.add_column("ID")
        small_table.add_column("Name")
        small_table.add_column("Value")

        for i in range(10):
            small_table.add_row(str(i), f"Item {i}", f"Value {i}")

        # Populate large table with 1000 rows
        large_table = self.query_one("#large-table", DataTable)
        large_table.add_column("ID")
        large_table.add_column("Name")
        large_table.add_column("Value")

        for i in range(1000):
            large_table.add_row(str(i), f"Item {i}", f"Value {i}")

        # Set up table properties
        for table in self.query(DataTable):
            table.zebra_stripes = True
            table.cursor_type = "row"


if __name__ == "__main__":
    app = TestDataTableApp()
    app.run()

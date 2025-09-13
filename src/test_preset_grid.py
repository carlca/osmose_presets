from textual.app import App, ComposeResult
from textual.widgets import DataTable
from textual import log
from preset_data import PresetData, Preset
from dataclasses import fields

# ROWS = [
#    (4, "Joseph Schooling", "Singapore", 50.39),
#    (2, "Michael Phelps", "United States", 51.14),
#    (5, "Chad le Clos", "South Africa", 51.14),
#    (6, "László Cseh", "Hungary", 51.14),
#    (3, "Li Zhuhao", "China", 51.26),
#    (8, "Mehdy Metella", "France", 51.58),
#    (7, "Tom Shields", "United States", 51.73),
#    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
#    (10, "Darren Burns", "Scotland", 51.84),
# ]


class TableApp(App):
   def compose(self) -> ComposeResult:
      yield DataTable()

   def on_mount(self) -> None:
      PresetData.clear_pack_filters()
      PresetData.add_pack_filter("factory")
      PresetData.clear_type_filters()
      PresetData.add_type_filter("keys")
      PresetData.add_type_filter("pads")
      PresetData.add_type_filter("perc")
      # presets = PresetData.get_presets()
      # log(presets)

      table = self.query_one(DataTable)
      table.add_columns(*[f.name for f in fields(Preset)])
      # table.add_rows(ROWS[1:])
      table.add_rows(PresetData.get_presets_as_tuples())

app = TableApp()
if __name__ == "__main__":
   app.run()

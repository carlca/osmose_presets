from textual.app import App, ComposeResult
from aligned_data_table import AlignedDataTable
from preset_data import PresetData, Preset
from dataclasses import fields


class TableApp(App):
   def compose(self) -> ComposeResult:
      yield AlignedDataTable()

   def on_mount(self) -> None:
      PresetData.clear_pack_filters()
      PresetData.add_pack_filter("factory")
      PresetData.add_pack_filter("expansion_01")
      PresetData.clear_type_filters()
      PresetData.add_type_filter("keys")
      PresetData.add_type_filter("pads")
      PresetData.add_type_filter("perc")

      table = self.query_one(AlignedDataTable)
      table.zebra_stripes = True
      table.cursor_type = "row"

      for f in fields(Preset):
         table.add_column(f.name, justify="left" if f.type not in [int, float] else "right")

      table.add_rows(PresetData.get_presets_as_tuples())


app = TableApp()
if __name__ == "__main__":
   app.run()

from textual.app import ComposeResult
from textual.containers import Vertical
from textual import log
from textual import events
from textual.events import Key
from dataclasses import fields
from osmose_presets.aligned_data_table import AlignedDataTable
from osmose_presets.preset_data import PresetData, Preset
from osmose_presets.messages import PresetSelected


class PresetGrid(Vertical):
   def on_mount(self) -> None:
      self.table = self.query_one(AlignedDataTable)
      self.table.zebra_stripes = True
      self.table.cursor_type = "row"
      self.table.show_cursor = True
      self.table.cursor_blink = False
      widths = PresetData.get_preset_max_widths()
      for i, f in enumerate(fields(Preset)):
         width = widths[i] if i < len(widths) else None
         name = f.name if f.name != "chars" else "character"
         self.table.add_column(
            name,
            justify="left" if f.type not in [int, float] else "right",
            width=width,
         )

   def compose(self) -> ComposeResult:
      self.border_title = "presets"
      yield AlignedDataTable()

   def set_filter(self, filter_type: str, selected_filters: list[str]):
      self.table.clear(columns=False)
      match filter_type:
         case "pack":
            PresetData.clear_pack_filters()
            PresetData.add_pack_filter(selected_filters)
         case "type":
            PresetData.clear_type_filters()
            PresetData.add_type_filter(selected_filters)
         case "char":
            PresetData.clear_char_filters()
            PresetData.add_char_filter(selected_filters)
         case _:
            log("set_filter case not matched")
      self.table.add_rows(PresetData.get_presets_as_tuples())

   def set_search_filter(self, search_term: str):
      PresetData.set_search_filter(search_term)
      self.table.clear(columns=False)
      self.table.add_rows(PresetData.get_presets_as_tuples())

   # def on_key(self, event: Key) -> None:
   #    """ handle key events in the preset grid """
   #    if event.key == "enter":
   #       self.post_message(PresetSelected())

   def on_aligned_data_table_clicked(self, event: events.Event) -> None:
      self.app.remove_all_focused_border_titles()
      self.add_class("focused")
      event.stop()

   def on_data_table_row_selected(self, event: AlignedDataTable.RowSelected) -> None:
      row = event.data_table.get_row(event.row_key)
      cc = row[2]
      pgm = row[3]
      self.post_message(PresetSelected(cc, pgm))

   def set_focus(self) -> None:
      self.table.focus()

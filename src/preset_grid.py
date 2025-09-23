from textual.app import ComposeResult
from textual.containers import Vertical
from textual import log
from textual import events
from aligned_data_table import AlignedDataTable
from preset_data import PresetData, Preset
from dataclasses import fields


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
         self.table.add_column(f.name, justify="left" if f.type not in [int, float] else "right", width=width)

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
      log(PresetData.get_preset_max_widths())

   def on_aligned_data_table_clicked(self, event: events.Event) -> None:
      self.app.remove_all_focused_border_titles()
      self.add_class("focused")
      event.stop()

   def set_focus(self) -> None:
      self.table.focus()

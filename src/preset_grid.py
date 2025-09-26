from textual.app import ComposeResult
from textual.containers import Vertical
from textual import log
from textual import events
from textual.events import Key
from aligned_data_table import AlignedDataTable
from data.models.preset import Preset
from dataclasses import fields
from messages import PresetSelected


class PresetGrid(Vertical):
   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.preset_service = None
      self.filter_service = None

   def on_mount(self) -> None:
      self.table = self.query_one(AlignedDataTable)
      self.table.zebra_stripes = True
      self.table.cursor_type = "row"
      self.table.show_cursor = True
      self.table.cursor_blink = False
      # Get services from app
      self.preset_service = self.app.services.get_preset_service()
      self.filter_service = self.app.services.get_filter_service()
      widths = self.preset_service.get_preset_field_widths()
      for i, f in enumerate(fields(Preset)):
         width = widths[i] if i < len(widths) else None
         name = f.name if f.name != "chars" else "character"
         self.table.add_column(name, justify="left" if f.type not in [int, float] else "right", width=width)

      # Register as a listener to preset service
      self.preset_service.add_listener(self.refresh_from_service)

      # Initialize with all filters selected
      all_packs = set(self.preset_service.get_available_packs())
      all_types = set(self.preset_service.get_available_types())
      all_chars = set(self.preset_service.get_available_chars())
      self.filter_service.set_pack_filter(all_packs)
      self.filter_service.set_type_filter(all_types)
      self.filter_service.set_char_filter(all_chars)

      # Initial load
      self.refresh_from_service()

   def compose(self) -> ComposeResult:
      self.border_title = "presets"
      yield AlignedDataTable()

   def refresh_from_service(self) -> None:
      """Refresh display when preset service notifies us of changes."""
      if not self.preset_service:
         return

      preset_tuples = self.preset_service.get_filtered_preset_tuples()

      self.table.clear(columns=False)
      self.table.add_rows(preset_tuples)
      log(f"PresetGrid refreshed: {len(preset_tuples)} presets")

   def set_filter(self, filter_type: str, selected_filters: list[str]):
      # This method is now just a bridge to the service
      if not self.filter_service:
         return

      selected = set(selected_filters)

      match filter_type:
         case "pack":
            self.filter_service.set_pack_filter(selected)
         case "type":
            self.filter_service.set_type_filter(selected)
         case "char":
            self.filter_service.set_char_filter(selected)
         case _:
            log("set_filter case not matched")

   def set_search_filter(self, search_term: str):
      if self.filter_service:
         self.filter_service.set_search(search_term)

   def on_aligned_data_table_clicked(self, event: events.Event) -> None:
      self.app.remove_all_focused_border_titles()
      self.add_class("focused")
      event.stop()

   def on_data_table_row_selected(self, event: AlignedDataTable.RowSelected) -> None:
      row = event.data_table.get_row(event.row_key)
      log(f"PresetGrid.on_row_selected: row={row}")
      cc = row[2]
      pgm = row[3]
      log(f"PresetGrid.on_row_selected: Sending CC={cc}, PGM={pgm}")
      self.post_message(PresetSelected(cc, pgm))

   def set_focus(self) -> None:
      self.table.focus()

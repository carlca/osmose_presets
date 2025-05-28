import flet as ft

from preset_data import PresetData
from ports_dialog import PortsDialog
from helper_functions import Helper
from preset_grid import PresetGrid
from filters import Filters
from filter_selector import FilterSelector
from midi_controller import MidiController


def read_selected_midi_port():
   config = Helper.read_config()
   return config.get("selected_midi_port", "")


def save_selected_midi_port(port):
   config = Helper.read_config()
   config["selected_midi_port"] = port
   Helper.write_config(config)


def main(page: ft.Page):
   page.theme_mode = ft.ThemeMode.DARK
   page.window.width = 1530
   page.window.height = 982
   page.window.center()
   page.vertical_alignment = "center"
   page.horizontal_alignment = "center"
   page.title = "Osmose Presets"
   PresetData.clear_pack_filters()
   PresetData.clear_type_filters()
   page.selected_midi_port = read_selected_midi_port()

   def show_dialog(e):
      page.selected_midi_port = read_selected_midi_port()
      ports_dialog = PortsDialog(
         page,
         selected_port=page.selected_midi_port,
         width=Helper.get_ports_dialog_width,
         height=250,
         title=ft.Text("Select MIDI Input Port")
      )  # fmt: skip
      ports_dialog.set_on_port_selected(port_selected)
      ports_dialog

   def handle_filter_changed(filter_type, selected_filters):
      match filter_type:
         case Filters.PACK:
            PresetData.clear_pack_filters()
            if selected_filters:
               PresetData.add_pack_filter(selected_filters)
         case Filters.TYPE:
            PresetData.clear_type_filters()
            if selected_filters:
               PresetData.add_type_filter(selected_filters)
      preset_grid.build_content()
      preset_grid.update()
      page.update()

   def port_selected(port):
      save_selected_midi_port(port)
      selected_midi_port_text.value = f"{port}"
      page.selected_midi_port = port
      page.update()

   def handle_preset_clicked(preset, cc, pgm):
      MidiController.send_preset_change(page.selected_midi_port, cc, pgm)
      print(f"Preset clicked! Preset: {preset}, CC: {cc}, PGM: {pgm}")

   selected_midi_port_text = ft.Text(value=f"{page.selected_midi_port}", color="#808080", size=24)

   pack_filter = FilterSelector(page, Filters.PACK, height=200)
   type_filter = FilterSelector(page, Filters.TYPE, expand=True)
   preset_grid = PresetGrid(on_preset_clicked=handle_preset_clicked)

   pack_filter.set_on_filter_changed(handle_filter_changed)
   type_filter.set_on_filter_changed(handle_filter_changed)

   page.add(
      ft.Row([ft.Container(content=ft.FilledButton(" MIDI Input Port ", color="#101010", on_click=show_dialog), padding=5), selected_midi_port_text]),
      ft.Row([ft.Column([pack_filter, type_filter], width=200), ft.Column([preset_grid])], expand=True),
   )
   page.on_event = handle_filter_changed
   page.update()


ft.app(target=main)

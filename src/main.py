import flet as ft
from preset_data import PresetData
from ports_dialog import PortsDialog
from helper_functions import Helper
from preset_grid import PresetGrid
from filters import Filters
from filter_selector import FilterSelector

# -------------------------------------------------------------------------------------------------

def main(page: ft.Page):
  page.theme_mode = ft.ThemeMode.DARK
  page.window.width = 1430
  page.window.height = 982
  page.window.center()
  page.vertical_alignment = "center"
  page.horizontal_alignment = "center"
  page.title = "Osmose Presets"
  PresetData.clear_pack_filters()
  PresetData.clear_type_filters()

  # -----------------------------------------------------------------------------------------------

  def show_dialog(e):
    ports_dialog = PortsDialog(page, width=Helper.get_ports_dialog_width, height=250, title=ft.Text("Select MIDI Input Port"))  # fmt: skip
    ports_dialog.set_on_port_selected(port_selected)
    ports_dialog

  # -----------------------------------------------------------------------------------------------

  def handle_filter_changed(filter_type, selected_filters):
    # print(f"Filter changed event received for {filter_type} with selected filters: {selected_filters}")
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

  # -----------------------------------------------------------------------------------------------

  def port_selected(port):
    print(f"port: {port} - selected!")

  # -----------------------------------------------------------------------------------------------

  pack_filter = FilterSelector(page, Filters.PACK, height=200)
  type_filter = FilterSelector(page, Filters.TYPE, expand=True)
  preset_grid = PresetGrid()

  pack_filter.set_on_filter_changed(handle_filter_changed)
  type_filter.set_on_filter_changed(handle_filter_changed)

  page.add(
    ft.Row(
      [
        ft.Container(
          content=ft.FilledButton(
            " MIDI Input Port ", color="#101010", on_click=show_dialog,
          ),
          padding=5,
        )
      ]
    ),
    ft.Row(
      [
        ft.Column(
          [
            pack_filter,
            type_filter,
          ],
          width=200,
        ),
        ft.Column(
          [
            preset_grid,
          ],
        ),
      ],
      expand=True,
    )
  )
  page.on_event = handle_filter_changed
  page.update()


ft.app(target=main)

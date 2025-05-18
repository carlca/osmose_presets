import flet as ft
from ports_dialog import PortsDialog
# import consts as c
from helper_functions import Helper
# from preset_data import PresetData
from preset_grid import PresetGrid
from filters import Filters
# from pack_selector import PackSelector
# from type_selector import TypeSelector
from filter_selector import FilterSelector

# ----------------------------------------------------------------------------------------------------

def main(page: ft.Page):
  page.window.width = 1430
  page.window.height = 975
  page.window.center()
  page.vertical_alignment = "center"
  page.horizontal_alignment = "center"
  page.title = "Osmose Presets"

  # ----------------------------------------------------------------------------------------------------

  def show_dialog(e):
    PortsDialog(page, width=Helper.get_ports_dialog_width, height=250, title=ft.Text("Select MIDI Input Port"))  # fmt: skip

  # ----------------------------------------------------------------------------------------------------

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
            FilterSelector(page, Filters.PACK, height=200),
            FilterSelector(page, Filters.TYPE, expand=True),
          ],
          width=200,
        ),
        ft.Column(
          [
            PresetGrid()
          ],
        ),
      ],
      expand=True,
    )
  )
  page.update()


ft.app(target=main)

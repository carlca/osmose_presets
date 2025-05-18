import flet as ft
from ports_dialog import PortsDialog
import consts as c
from helper_functions import Helper
from preset_data import PresetData
from preset_grid import PresetGrid
from filters import Filters
# from pack_selector import PackSelector
# from type_selector import TypeSelector
from filter_selector import FilterSelector

DEBUG_PAGE_SIZE = False

# ----------------------------------------------------------------------------------------------------

def page_resized(e, page):
  page.title = f"Osmose Presets - {page.window.width} x {page.window.height}"
  page.update()

# ----------------------------------------------------------------------------------------------------

def main(page: ft.Page):
  page.window.width = 1400
  page.window.height = 960
  page.window.center()
  page.vertical_alignment = "center"
  page.horizontal_alignment = "center"
  if DEBUG_PAGE_SIZE:
    page.on_resized = page_resized(page)

  page.title = "Osmose Presets"

  # ----------------------------------------------------------------------------------------------------

  def show_dialog(e):
    longest = Helper.get_longest_port_length()
    excess = max(0, longest - c.DEFAULT_PORT_NAME_LENGTH) * c.PIXELS_PER_CHAR
    dlg_width = c.BASE_DIALOG_WIDTH + excess
    dlg = PortsDialog(width=dlg_width, height=250, title=ft.Text("Select MIDI Input Port"))  # fmt: skip
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  # ----------------------------------------------------------------------------------------------------

  page.add(
    ft.Row(
      [
        ft.Column(
          [
            ft.Text("   pack", color="#808080", size=24),
            FilterSelector(page, Filters.PACK),
            ft.Text("   type", color="#808080", size=24),
            FilterSelector(page, Filters.TYPE),
          ],
          width=200,
        ),
        ft.Column(
          [
            ft.Container(
              content=ft.FilledButton(
                " Select MIDI Input Port ", color="#101010", on_click=show_dialog,
              ),
              padding=5,
            ),
            PresetGrid()
          ],
        ),
      ],
      expand=True,
    )
  )

  # PresetData.add_pack_filter("factory")
  # PresetData.add_type_filter(["organ", "mallets"])

  # print("")
  # print(PresetData.get_packs())

  print("")
  pack = "expansion_01"
  print(pack)
  print(PresetData.get_types(pack))

  # print("")
  # pack = "factory"
  # print(pack)
  # print(PresetData.get_types(pack))

  # presets = PresetData.get_presets()
  # if presets:
  #   for preset in presets:
  #     print(preset)

  # print(Helper.get_longest_pack_and_type_length())

  page.update()


ft.app(target=main)

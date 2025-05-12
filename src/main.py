import flet as ft
from ports_dialog import PortsDialog
import consts as c
import helper_functions
from preset_data import PresetData

def main(page: ft.Page):

  def show_dialog(e):
    longest = helper_functions.get_longest_port_width()
    excess = max(0, longest - c.DEFAULT_PORT_NAME_LENGTH) * c.PIXELS_PER_CHAR
    dlg_width = c.BASE_DIALOG_WIDTH + excess
    dlg = PortsDialog(width=dlg_width, height=250, title=ft.Text("Select MIDI Input Port"))  # fmt: skip
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  page.title = "Osmose Presets"
  page.add(ft.Text("Main application content"))
  page.add(ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog))
  page.update()

  presets = PresetData.presets()
  if presets:
    for preset in presets:
      print(preset)

  print("")
  print(PresetData.get_packs())

  print("")
  pack = "expansion_01"
  print(pack)
  print(PresetData.get_types(pack))

  print("")
  pack = "factory"
  print(pack)
  print(PresetData.get_types(pack))

  print("")
  pack = ""
  print(pack)
  print(PresetData.get_types(pack))


ft.app(target=main)

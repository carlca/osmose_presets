import flet as ft
from ports_dialog import PortsDialog
from consts import *
from helper_functions import *

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def main(page: ft.Page):

  def show_dialog(e):
    longest = get_longest_port_width()
    excess = max(0, longest - DEFAULT_PORT_NAME_LENGTH) * PIXELS_PER_CHAR
    dlg_width = BASE_DIALOG_WIDTH + excess
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

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

ft.app(target=main)

import flet as ft
from ports_dialog import open_ports_dialog

def main(page: ft.Page):
  page.title = "Osmose Presets"
  page.add(ft.Text("Main application content"))

  ports_button = open_ports_dialog(page)
  page.add(ports_button)

ft.app(target=main)

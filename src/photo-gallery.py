import flet as ft
import helper_functions
from preset_data import PresetData


def main(page: ft.Page):
  page.title = "Scrolling Photo Gallery with Fixed Header"
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 50
  page.window.width = 1400
  page.window.height = 1000
  page.window.center()
  page.update()

  PresetData.add_pack_filter("factory")
  PresetData.add_type_filter(["organ", "mallets"])
  presets = PresetData.get_presets()
  pack_width = helper_functions.get_longest_pack_width() * 12 + 20
  type_width = helper_functions.get_longest_type_width() * 12 + 20

  column_count = 6

  header_row = ft.Row(
    controls=[
      ft.Text("bank", width=pack_width, color="#808080", size=20),
      ft.Text("type", width=type_width, color="#808080", size=20),
      ft.Text("preset", width=200, color="#808080", size=20),
      ft.Text("cc", width=50, color="#808080", size=20),
      ft.Text("pgm", width=50, color="#808080", size=20),
      ft.Text("  other", width=150, color="#808080", size=20),
    ]
  )

  # Data Rows (Scrolling in ListView)
  data_rows = []
  for preset in presets:
    data_rows.append(
      ft.Row(
        controls=[
          ft.Text(preset.pack, width=pack_width),
          ft.Text(preset.type, width=type_width),
          ft.Text(preset.preset, width=200),
          ft.Text(preset.cc0, width=60),
          ft.Text(preset.pgm, width=60),
          ft.Text("Other values", width=150),
        ]
      )
    )

  # ListView for Scrolling Data
  list_view = ft.ListView(
    expand=1,
    spacing=5,
    controls=data_rows,
  )

  # Combine Header and ListView
  page.add(header_row, list_view)
  page.update()


ft.app(main)

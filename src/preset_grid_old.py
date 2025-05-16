import flet as ft
from helper_functions import Helper
from preset_data import PresetData


def main(page: ft.Page):
  page.title = "Presets"
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 50
  page.window.width = 1400
  page.window.height = 1000
  page.window.center()
  page.update()

  PresetData.add_pack_filter("factory")
  PresetData.add_type_filter(["organ", "mallets"])

  presets = PresetData.get_presets()
  pack_width = Helper.get_longest_pack_length() * 12 + 20
  type_width = Helper.get_longest_type_length() * 12 + 20
  preset_width = Helper.get_longest_preset_length() * 12 + 20
  characters_string_width = Helper.get_longest_characters_length() * 12 + 20

  column_count = 6

  header_row = ft.Row(
    controls=[
      ft.Text("bank", width=pack_width, color="#808080", size=20),
      ft.Text("type", width=type_width, color="#808080", size=20),
      ft.Text("preset", width=preset_width, color="#808080", size=20),
      ft.Text("cc", width=50, color="#808080", size=20),
      ft.Text("pgm", width=50, color="#808080", size=20),
      ft.Text("   characters", width=characters_string_width, color="#808080", size=20),
    ]
  )

  data_rows = []
  for i, preset in enumerate(presets):
    bg_color = (
        "#232323" if i % 2 == 0 else None
    )
    characters_string = Helper.get_character_list(preset)

    data_rows.append(
      ft.Container(
        content=ft.Row(
          controls=[
            ft.Text(preset.pack, width=pack_width),
            ft.Text(preset.type, width=type_width),
            ft.Text(preset.preset, width=preset_width),
            ft.Text(preset.cc0, width=60),
            ft.Text(preset.pgm, width=60),
            ft.Text(characters_string, width=characters_string_width),
          ],
        ),
        bgcolor=bg_color,
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

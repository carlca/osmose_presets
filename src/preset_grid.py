import flet as ft
from preset_data import PresetData
from helper_functions import Helper
from spacer import Spacer

# ----------------------------------------------------------------------------------------------------

class PresetGrid(ft.Container):
  def __init__(self):
    super().__init__()
    self.controls = []
    self.expand = True
    self.build_content()

  def build_content(self):
    self.presets = PresetData.get_presets()

    pack_width = Helper.get_longest_pack_length() * 12
    type_width = Helper.get_longest_type_length() * 12
    preset_width = Helper.get_longest_preset_length() * 12
    characters_string_width = Helper.get_longest_characters_length() * 12

    header_row = ft.Row(
      controls=[
        ft.Text("bank", width=pack_width, color="#808080", size=24),
        ft.Text("type", width=type_width, color="#808080", size=24),
        ft.Text("preset", width=preset_width, color="#808080", size=24),
        ft.Text("cc", width=50, color="#808080", size=24),
        ft.Text("pgm", width=70, color="#808080", size=24),
        ft.Text("characters", width=characters_string_width, color="#808080", size=24),
      ],
    )

    header_column = ft.Column(height=45)
    header_column.controls.append(header_row)

    items_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=800)
    for row, preset in enumerate(self.presets):
      bg_color = (
          "#333333" if row % 2 == 0 else None
      )
      items_column.controls.append(
        ft.Container(
          content=ft.Row(
            [
              ft.Text(preset.pack, width=pack_width),
              ft.Text(preset.type, width=type_width),
              ft.Text(preset.preset, width=preset_width),
              ft.Text(str(preset.cc0), width=20, text_align=ft.TextAlign.RIGHT),
              ft.Text(str(preset.pgm), width=64, text_align=ft.TextAlign.RIGHT),
              ft.Text("      "),
              ft.Text(",".join(preset.characters), width=characters_string_width),
            ]
          ),
          height=31,
          # width=1700,
          padding=5,
          border_radius=5,
          bgcolor=bg_color,
        )
      )

    grid_container = ft.Container(
      content=ft.Column(
        [
          header_column,
          # Spacer(0.1),
          items_column,
        ]
      ),
      bgcolor="#232323",
      padding=10,
      border_radius= ft.border_radius.all(20),
      width=1200,
    )

    self.content = grid_container

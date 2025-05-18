import flet as ft
from preset_data import PresetData
from helper_functions import Helper

# ----------------------------------------------------------------------------------------------------

class PresetGrid(ft.Container):
  def __init__(self):
    super().__init__()
    self.controls = []
    self.expand = True
    print("about to build_content")
    self.build_content()

  def build_content(self):
    self.presets = PresetData.get_presets()

    pack_width = Helper.get_longest_pack_length() * 12
    type_width = Helper.get_longest_type_length() * 12
    preset_width = Helper.get_longest_preset_length() * 12
    characters_string_width = Helper.get_longest_characters_length() * 12

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

    # self.header = ft.Column(width=1700, height=40)
    # self.header.controls.append(header_row)
    header_column = ft.Column(width=1700, height=40)
    header_column.controls.append(header_row)

    # self.items = ft.Column(width=1700, scroll=ft.ScrollMode.ALWAYS, height=300)
    # self.items = ft.Column(width=1700, scroll=ft.ScrollMode.ALWAYS, height=850)
    items_column = ft.Column(width=1700, scroll=ft.ScrollMode.ALWAYS, height=850)
    for preset in self.presets:
      items_column.controls.append(
        ft.Container(
          content=ft.Row(
            [
              ft.Text(preset.pack, width=pack_width),
              ft.Text(preset.type, width=type_width),
              ft.Text(preset.preset, width=preset_width),
              ft.Text(str(preset.cc0), width=50),
              ft.Text(str(preset.pgm), width=50),
              ft.Text(",".join(preset.characters), width=characters_string_width),
            ]
          ),
          width=1700,
          padding=5,
          border_radius=5,
        )
      )

    grid_container = ft.Container(
      content=ft.Column(
        [
          header_column,
          items_column,
        ]
      ),
      bgcolor="#232323",
      padding=10,
      border_radius= ft.border_radius.all(20),
    )

    self.content = grid_container

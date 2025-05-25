import flet as ft
from preset_data import PresetData
from helper_functions import Helper
from sortable_header import SortableHeader


class PresetGrid(ft.Container):
   def __init__(self, on_preset_clicked=None):
      super().__init__()
      self.controls = []
      self.expand = True
      self.on_preset_clicked = on_preset_clicked
      self.build_content()

   def header_clicked(self, header_instance: SortableHeader): # Add 'header_instance'
      print(f"Header '{header_instance.column_name_actual} {header_instance.state}' was clicked.")
      pass

   def build_content(self):
      self.presets = PresetData.get_presets()

      pack_width = Helper.get_longest_pack_length() * 12
      type_width = Helper.get_longest_type_length() * 12
      preset_width = Helper.get_longest_preset_length() * 12
      characters_width = Helper.get_longest_characters_length() * 12 - 310

      self.bank_header = SortableHeader("bank", pack_width, self.header_clicked)
      self.type_header = SortableHeader("type", type_width, self.header_clicked)
      self.preset_header = SortableHeader("preset", preset_width, self.header_clicked)
      self.cc_header = SortableHeader("cc", 70, self.header_clicked)
      self.pgm_header = SortableHeader("pgm", 90, self.header_clicked)
      self.characters_header = SortableHeader(
         "characters", characters_width, self.header_clicked
      )

      header_row = ft.Row(
         controls=[
            self.bank_header,
            self.type_header,
            self.preset_header,
            self.cc_header,
            self.pgm_header,
            self.characters_header,
         ]
      )

      header_column = ft.Column(height=45, spacing=9)
      header_column.controls.append(header_row)

      items_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=810)
      for row, preset in enumerate(self.presets):
         bg_color = "#555555" if row % 2 == 0 else "#333333"

         def preset_clicked(e, preset=preset.preset, cc=preset.cc0, pgm=preset.pgm):
            if self.on_preset_clicked:
               self.on_preset_clicked(preset, cc, pgm)

         def hover_color(e):
            e.control.content.color = (
               ft.Colors.GREEN if e.data == "true" else ft.Colors.WHITE
            )
            e.control.content.update()

         def spacer(n):
            return " " * n

         items_column.controls.append(
            ft.Container(
               content=ft.Row(
                  [
                     ft.Text(spacer(1) + preset.pack, width=pack_width),
                     ft.Text(spacer(1) + preset.type, width=type_width),
                     ft.TextButton(
                        content=ft.Text(
                           spacer(1) + preset.preset,
                           width=preset_width,
                           color=ft.Colors.WHITE,
                        ),
                        data=preset,
                        on_click=preset_clicked,
                        on_hover=hover_color,
                        style=ft.ButtonStyle(
                           mouse_cursor={ft.ControlState.HOVERED: ft.MouseCursor.CLICK},
                           padding=0,
                           overlay_color=ft.Colors.TRANSPARENT,
                        ),
                        disabled=False,
                     ),
                     ft.Text(
                        spacer(2) + str(preset.cc0),
                        width=28,
                        text_align=ft.TextAlign.RIGHT,
                     ),
                     ft.Text(
                        spacer(5) + str(preset.pgm),
                        width=80,
                        text_align=ft.TextAlign.RIGHT,
                     ),
                     ft.Text("      "),
                     ft.Text(
                        spacer(5) + ",".join(preset.characters), width=characters_width
                     ),
                  ]
               ),
               height=31,
               padding=5,
               border_radius=5,
               bgcolor=bg_color,
            )
         )

      grid_container = ft.Container(
         content=ft.Column([header_column, items_column]),
         bgcolor="#232323",
         padding=10,
         border_radius=ft.border_radius.all(16),
         width=1300,
      )

      self.content = grid_container

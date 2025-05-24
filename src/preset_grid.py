import flet as ft
from preset_data import PresetData
from helper_functions import Helper

# -------------------------------------------------------------------------------------------------


class PresetGrid(ft.Container):
   def __init__(self, on_preset_clicked=None):
      super().__init__()
      self.controls = []
      self.expand = True
      self.on_preset_clicked = on_preset_clicked
      self.build_content()

   # ----------------------------------------------------------------------------------------------

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
            ft.Text(
               "characters", width=characters_string_width, color="#808080", size=24
            ),
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

         items_column.controls.append(
            ft.Container(
               content=ft.Row(
                  [
                     ft.Text(preset.pack, width=pack_width),
                     ft.Text(preset.type, width=type_width),
                     ft.TextButton(
                        content=ft.Text(
                           preset.preset, width=preset_width, color=ft.Colors.WHITE
                        ),
                        data=preset,
                        on_click=preset_clicked,
                        on_hover=hover_color,
                        style=ft.ButtonStyle(
                           mouse_cursor={
                              ft.ControlState.HOVERED: ft.MouseCursor.CLICK
                           },
                           padding=0,
                           overlay_color=ft.Colors.TRANSPARENT,
                        ),
                        disabled=False,
                     ),
                     ft.Text(str(preset.cc0), width=20, text_align=ft.TextAlign.RIGHT),
                     ft.Text(str(preset.pgm), width=64, text_align=ft.TextAlign.RIGHT),
                     ft.Text("      "),
                     ft.Text(
                        ",".join(preset.characters), width=characters_string_width
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
         width=1200,
      )

      self.content = grid_container


# import flet as ft
# from preset_data import PresetData
# from helper_functions import Helper

# # -------------------------------------------------------------------------------------------------


# class PresetGrid(ft.Container):
#    def __init__(self, on_preset_clicked=None):
#       super().__init__()
#       self.controls = []
#       self.expand = True
#       self.on_preset_clicked = on_preset_clicked
#       self.build_content()

#    # ----------------------------------------------------------------------------------------------

#    def build_content(self):
#       self.presets = PresetData.get_presets()

#       pack_width = Helper.get_longest_pack_length() * 12
#       type_width = Helper.get_longest_type_length() * 12
#       preset_width = Helper.get_longest_preset_length() * 12
#       characters_string_width = Helper.get_longest_characters_length() * 12

#       header_row = ft.Row(
#          controls=[
#             ft.Text("bank", width=pack_width, color="#808080", size=24),
#             ft.Text("type", width=type_width, color="#808080", size=24),
#             ft.Text("preset", width=preset_width, color="#808080", size=24),
#             ft.Text("cc", width=50, color="#808080", size=24),
#             ft.Text("pgm", width=70, color="#808080", size=24),
#             ft.Text(
#                "characters", width=characters_string_width, color="#808080", size=24
#             ),
#          ]
#       )

#       header_column = ft.Column(height=45, spacing=9)
#       header_column.controls.append(header_row)

#       items_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=810)
#       for row, preset in enumerate(self.presets):
#          bg_color = "#555555" if row % 2 == 0 else "#333333"

#          def preset_clicked(e, cc=preset.cc0, pgm=preset.pgm):
#             if self.on_preset_clicked:
#                self.on_preset_clicked(cc, pgm)

#          def hover_color(e):
#             e.control.color = ft.Colors.YELLOW if e.data == "true" else ft.Colors.WHITE
#             e.control.update()

#          items_column.controls.append(
#             ft.Container(
#                content=ft.Row(
#                   [
#                      ft.Text(preset.pack, width=pack_width),
#                      ft.Text(preset.type, width=type_width),
#                      ft.TextButton(
#                         content=ft.Text(preset.preset, width=preset_width),
#                         data=preset,
#                         on_click=preset_clicked,
#                         on_hover=hover_color,
#                         style=ft.ButtonStyle(
#                            mouse_cursor={
#                               ft.ControlState.HOVERED: ft.MouseCursor.CLICK
#                            },
#                            padding=0,
#                            overlay_color=ft.Colors.TRANSPARENT,
#                         ),
#                         disabled=False,
#                      ),
#                      ft.Text(str(preset.cc0), width=20, text_align=ft.TextAlign.RIGHT),
#                      ft.Text(str(preset.pgm), width=64, text_align=ft.TextAlign.RIGHT),
#                      ft.Text("      "),
#                      ft.Text(
#                         ",".join(preset.characters), width=characters_string_width
#                      ),
#                   ]
#                ),
#                height=31,
#                padding=5,
#                border_radius=5,
#                bgcolor=bg_color,
#             )
#          )

#       grid_container = ft.Container(
#          content=ft.Column([header_column, items_column]),
#          bgcolor="#232323",
#          padding=10,
#          border_radius=ft.border_radius.all(16),
#          width=1200,
#       )

#       self.content = grid_container

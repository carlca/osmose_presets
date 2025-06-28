import flet as ft
from preset_data import PresetData
from helper_functions import Helper
from sortable_header import SortableHeader, SortState


class PresetGrid(ft.Container):
   def __init__(self, on_preset_clicked=None):
      super().__init__()
      self.controls = []
      self.headers = []
      self.expand = True
      self.on_preset_clicked = on_preset_clicked

      self.pack_width = Helper.get_longest_pack_length() * 12
      self.type_width = Helper.get_longest_type_length() * 12
      self.preset_width = Helper.get_longest_preset_length() * 12
      self.characters_width = Helper.get_longest_characters_length() * 12 - 310

      self.pack_header = SortableHeader("pack", self.pack_width, self.header_clicked)
      self.type_header = SortableHeader("type", self.type_width, self.header_clicked)
      self.preset_header = SortableHeader("preset", self.preset_width, self.header_clicked)
      self.cc_header = SortableHeader("cc0", 80, self.header_clicked)
      self.pgm_header = SortableHeader("pgm", 90, self.header_clicked)
      self.characters_header = SortableHeader("characters", self.characters_width, self.header_clicked)

      self.headers.extend([self.pack_header, self.type_header, self.preset_header, self.cc_header, self.pgm_header, self.characters_header])

      self.header_row = ft.Row(controls=self.headers)
      self.header_column = ft.Column([self.header_row], height=45, spacing=9)

      self.items_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=810)

      self.grid_container = ft.Container(
         content=ft.Column([self.header_column, self.items_column]),
         bgcolor="#232323",
         padding=10,
         border_radius=ft.BorderRadius.all(16),
         width=1300
      )
      self.content = self.grid_container
      self.update_preset_items_display()

   def header_clicked(self, header_instance: SortableHeader):  # Add 'header_instance'
      sort_criteria = []
      for header in self.headers:
         sort_criteria.append((header.column_name_actual, header.state == SortState.ASCENDING))
      PresetData.set_sort_criteria(sort_criteria)
      self.update_preset_items_display()

      self.update()
      if self.page:
         self.page.update()
      print(f"Header '{header_instance.column_name_actual} {header_instance.state}' was clicked.")

   def update_preset_items_display(self):
      """
      Fetches (filtered and sorted) presets and updates only the items_column.
      """
      self.presets = PresetData.get_presets()

      self.items_column.controls.clear()

      pack_width = self.pack_header.width
      type_width = self.type_header.width
      preset_width = self.preset_header.width
      cc_width = 28
      pgm_width = 90
      characters_width = self.characters_header.width

      for row, preset_item in enumerate(self.presets):
         bg_color = "#555555" if row % 2 == 0 else "#333333"

         def preset_clicked_closure(e, p_name=preset_item.preset, p_cc=preset_item.cc0, p_pgm=preset_item.pgm):
            if self.on_preset_clicked:
               self.on_preset_clicked(p_name, p_cc, p_pgm)

         def hover_color_closure(e):
            # This assumes TextButton content is a Text control
            if hasattr(e.control, 'content') and isinstance(e.control.content, ft.Text):
                e.control.content.color = ft.Colors.GREEN if e.data == "true" else ft.Colors.WHITE
                e.control.content.update()

         def spacer_local(n):
            return " " * n

         self.items_column.controls.append(
            ft.Container(
               content=ft.Row(
                  [
                     ft.Text(spacer_local(1) + preset_item.pack, width=pack_width),
                     ft.Text(spacer_local(1) + preset_item.type, width=type_width),
                     ft.TextButton(
                        content=ft.Text(spacer_local(1) + preset_item.preset, width=preset_width, color=ft.Colors.WHITE),
                        data=preset_item,
                        on_click=preset_clicked_closure,
                        on_hover=hover_color_closure,
                        style=ft.ButtonStyle(mouse_cursor={ft.ControlState.HOVERED: ft.MouseCursor.CLICK}, padding=0, overlay_color=ft.Colors.TRANSPARENT),
                        disabled=False,
                     ),
                     ft.Text(spacer_local(2) + str(preset_item.cc0), width=cc_width, text_align=ft.TextAlign.RIGHT),
                     ft.Text(spacer_local(5) + str(preset_item.pgm), width=pgm_width, text_align=ft.TextAlign.RIGHT),
                     ft.Text("      "),
                     ft.Text(spacer_local(5) + ",".join(preset_item.characters), width=characters_width),
                  ]
               ),
               height=31,
               padding=5,
               border_radius=5,
               bgcolor=bg_color,
            )
         )

      if self.items_column.page:
         self.items_column.update()

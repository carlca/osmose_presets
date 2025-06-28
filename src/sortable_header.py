import flet as ft
from enum import Enum, auto


class SortState(Enum):
   # NONE = auto()
   DESCENDING = auto()
   ASCENDING = auto()


class SortableHeader(ft.TextButton):
   state: SortState

   def __init__(self, column_name: str, width: int, on_click_handler, height: int = 40):
      super().__init__()

      self.column_name_actual = str(column_name)
      self.on_click_handler = on_click_handler
      self.state = SortState.ASCENDING

      self.column_name_display = ft.Text(
         value=self.column_name_actual, text_align=ft.TextAlign.LEFT, color="#808080", size=24, overflow=ft.TextOverflow.ELLIPSIS, expand=True
      )

      self.sort_icon_display = ft.Text(value="", color="#808080", size=16)

      self.width = width
      self.height = height
      self.on_click = self._internal_clicked
      self.style = ft.ButtonStyle(
         overlay_color=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
         mouse_cursor={ft.ControlState.HOVERED: ft.MouseCursor.CLICK},
         padding=ft.Padding.symmetric(horizontal=8),
         shape=ft.RoundedRectangleBorder(radius=8),
      )
      self.content = ft.Row(
         controls=[self.column_name_display, self.sort_icon_display],
         vertical_alignment=ft.CrossAxisAlignment.CENTER,
         alignment=ft.MainAxisAlignment.START,
         spacing=4,
         expand=True,
      )
      self.update_text()

   def _internal_clicked(self, e):
      match self.state:
         case SortState.ASCENDING:
            self.state = SortState.DESCENDING
         case SortState.DESCENDING:
            self.state = SortState.ASCENDING
      self.update_text()
      if self.on_click_handler:
         self.on_click_handler(self)

   def update_text(self):
      match self.state:
         # case SortState.NONE:
         #    icon_char = ""
         case SortState.DESCENDING:
            icon_char = "▲"
         case SortState.ASCENDING:
            icon_char = "▼"
      self.sort_icon_display.value = icon_char
      if self.page:
         self.update()

   def get_state(self):
      return self.state

   def reset_state(self):
      self.state = SortState.ASCENDING
      self.update_text()

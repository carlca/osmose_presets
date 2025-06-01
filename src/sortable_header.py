import flet as ft
from enum import Enum, auto


class SortState(Enum):
   NONE = auto()
   DESCENDING = auto()
   ASCENDING = auto()


class SortableHeader(ft.TextButton):
   state: SortState

   def __init__(self, column_name: str, width: int, on_click_handler, height: int = 40):
      super().__init__()

      self.column_name_actual = str(column_name)
      self.on_click_handler = on_click_handler
      self.state = SortState.NONE

      self.column_name_display = ft.Text(
         value=self.column_name_actual, text_align=ft.TextAlign.LEFT, color="#808080", size=24, overflow=ft.TextOverflow.ELLIPSIS, expand=True
      )

      self.sort_icon_display = ft.Text(value="", color="#808080", size=16)

      self.width = width
      self.height = height
      self.on_click = self._internal_clicked  # Use a prefixed internal handler
      self.style = ft.ButtonStyle(
         overlay_color=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),  # Subtle hover
         mouse_cursor={ft.ControlState.HOVERED: ft.MouseCursor.CLICK},
         padding=ft.padding.symmetric(horizontal=8),  # Add some horizontal padding
         shape=ft.RoundedRectangleBorder(radius=8),
      )
      self.content = ft.Row(
         controls=[self.column_name_display, self.sort_icon_display],
         vertical_alignment=ft.CrossAxisAlignment.CENTER,
         alignment=ft.MainAxisAlignment.START,
         spacing=4,
         expand=True,
      )
      # No need to call update_text() at init if icon is initially empty and text is set

   def _internal_clicked(self, e):
      match self.state:
         case SortState.NONE:
            self.state = SortState.ASCENDING
         case SortState.ASCENDING:
            self.state = SortState.DESCENDING
         case SortState.DESCENDING:
            self.state = SortState.NONE
      self.update_text()
      if self.on_click_handler:
         self.on_click_handler(self)

   def update_text(self):
      match self.state:
         case SortState.NONE:
            icon_char = ""
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
      self.state = None
      self.update_text()


# Example Usage (Optional - for testing)
def main(page: ft.Page):
   page.title = "Sortable Header Test"
   page.vertical_alignment = ft.MainAxisAlignment.CENTER
   page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

   def on_header_click(header_instance: SortableHeader):
      print(f"Header '{header_instance.column_name_actual}' clicked. New state: {header_instance.get_state()}")
      # In a real scenario, you'd also tell other headers to reset their state
      # if you want only one column to be sorted at a time.
      for h in headers:
         if h is not header_instance:
            h.reset_state()

   header1 = SortableHeader(column_name="Name", width=150, on_click_handler=on_header_click)
   header2 = SortableHeader(column_name="Age", width=100, on_click_handler=on_header_click)
   header3 = SortableHeader(column_name="Very Long Column Name Indeed", width=200, on_click_handler=on_header_click)

   headers = [header1, header2, header3]

   page.add(ft.Row(controls=headers, alignment=ft.MainAxisAlignment.CENTER))


if __name__ == "__main__":
   ft.app(target=main)

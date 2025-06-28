import flet as ft
from preset_data import PresetData
from helper_functions import Helper
from filters import Filters
from spacer import Spacer


class FilterSelector(ft.Container):
   def __init__(self, filter, height=None, expand=False):
      super().__init__()
      self.height = height
      self.expand = expand
      self.filter = filter
      self.filter_checkboxes = []
      self.on_filter_changed_callback = None
      self.content = self.__content()

   def set_on_filter_changed(self, callback):
      self.on_filter_changed_callback = callback

   def get_selected_filters(self):
      selected_filters = []
      for checkbox in self.filter_checkboxes[1:]:
         if checkbox.value:
            selected_filters.append(checkbox.label)
      return selected_filters

   def __content(self):
      filter_selector_container = self.create_filter_column()
      return filter_selector_container

   def create_filter_column(self):
      self.filter_checkboxes.clear()

      filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()

      def update_filter_checkboxes(e):
         if e.control == self.filter_checkboxes[0]:
            # Set all other checkboxes to match the "all" state
            for checkbox in self.filter_checkboxes[1:]:
               checkbox.value = self.filter_checkboxes[0].value
         else:
            # Check if all individual boxes are checked to update "all"
            all_checked = all(checkbox.value for checkbox in self.filter_checkboxes[1:])
            self.filter_checkboxes[0].value = all_checked

         # Use self.update() for UserControl, which is more efficient than page.update()
         self.page.update()
         self.update()
         if self.on_filter_changed_callback:
            selected_filters = self.get_selected_filters()
            self.on_filter_changed_callback(self.filter, selected_filters)

      all_filters_checkbox = ft.Checkbox(label="all", value=False, on_change=update_filter_checkboxes)
      self.filter_checkboxes.append(all_filters_checkbox)

      for filter_name in filter_names:
         self.filter_checkboxes.append(ft.Checkbox(label=filter_name, value=False, on_change=update_filter_checkboxes))

      width = Helper.get_longest_pack_and_type_length() * 12 + 20
      filter_text = "pack" if self.filter == Filters.PACK else "type"
      inner_filter_header = ft.Container(content=ft.Text(f" {filter_text}", color="#808080", size=24), height=35 if self.filter == Filters.PACK else 30)

      inner_filter_column = ft.Container(content=ft.Column(spacing=5, controls=self.filter_checkboxes, width=width, scroll=ft.ScrollMode.AUTO))

      filter_column = ft.Container(
         ft.Column([inner_filter_header, Spacer(-1.0), inner_filter_column]), padding=10, bgcolor="#232323", border_radius=ft.BorderRadius.all(16)
      )

      return filter_column

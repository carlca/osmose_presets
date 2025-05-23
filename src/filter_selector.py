import flet as ft
from preset_data import PresetData
from helper_functions import Helper
from filters import Filters
from spacer import Spacer

# -------------------------------------------------------------------------------------------------

class FilterSelector(ft.Container):

  def __init__(self, page, filter, height=None, expand=False):
    super().__init__()
    self.controls = []
    self.height = height
    self.expand = expand
    self.filter = filter
    self.page = page
    self.filter_checkboxes = []  # Initialize here
    self.build_content()
    self.on_filter_changed_callback = None

  def set_on_filter_changed(self, callback):
    self.on_filter_changed_callback = callback

  def get_selected_filters(self):
    selected_filters = []
    # Skip the "all" checkbox (index 0)
    for checkbox in self.filter_checkboxes[1:]:
      if checkbox.value:
        selected_filters.append(checkbox.label)
    return selected_filters

  # -----------------------------------------------------------------------------------------------

  def build_content(self):
    filter_selector_container = self.create_filter_column()
    self.content = filter_selector_container

  # -----------------------------------------------------------------------------------------------

  def create_filter_column(self):
    filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()

    # ---------------------------------------------------------------------------------------------

    def update_filter_checkboxes(e):
      if e.control == self.filter_checkboxes[0]:
        for checkbox in self.filter_checkboxes[1:]:
          checkbox.value = self.filter_checkboxes[0].value
      else:
        all_checked = True
        for checkbox in self.filter_checkboxes[1:]:
          if not checkbox.value:
            all_checked = False
            break
        self.filter_checkboxes[0].value = all_checked
      self.page.update()
      if self.on_filter_changed_callback:
        selected_filters = self.get_selected_filters()
        self.on_filter_changed_callback(self.filter, selected_filters)

      # ---------------------------------------------------------------------------------------------

    all_filters_checkbox = ft.Checkbox(
      label="all", value=False, on_change=update_filter_checkboxes
    )
    self.filter_checkboxes.append(all_filters_checkbox)

    for filter_name in filter_names:
      self.filter_checkboxes.append(
        ft.Checkbox(label=filter_name, value=False, on_change=update_filter_checkboxes)
      )

    width = Helper.get_longest_pack_and_type_length() * 12 + 20
    filter_text = "pack" if self.filter == Filters.PACK else "type"
    inner_filter_header = ft.Container(
      content=ft.Text(f" {filter_text}", color="#808080", size=24),
      height=35 if self.filter == Filters.PACK else 30
    )

    inner_filter_column = ft.Container(
      content=ft.Column(
        spacing=9,
        controls=self.filter_checkboxes,
        width=width,
        scroll=ft.ScrollMode.AUTO),
    )

    filter_column = ft.Container(
      ft.Column(
        [
          inner_filter_header,
          Spacer(-1.0),
          inner_filter_column,
        ]
      ),
      padding=10,
      bgcolor="#232323",
      border_radius= ft.border_radius.all(16)
    )

    return filter_column

    # ---------------------------------------------------------------------------------------------


# import flet as ft
# from preset_data import PresetData
# from helper_functions import Helper
# from filters import Filters
# from spacer import Spacer

# # -------------------------------------------------------------------------------------------------

# class FilterSelector(ft.Container):

#   def __init__(self, page, filter, height=None, expand=False):
#     super().__init__()
#     self.controls = []
#     self.height = height
#     self.expand = expand
#     self.filter = filter
#     self.build_content()
#     self.on_filter_changed_callback = None
#     self.filter_checkboxes = []

#   # -----------------------------------------------------------------------------------------------

#   def set_on_filter_changed(self, callback):
#     self.on_filter_changed_callback = callback

#   # -----------------------------------------------------------------------------------------------

#   def get_selected_filters(self):
#     selected_filters = []
#     # Skip the "all" checkbox (index 0)
#     for checkbox in self.filter_checkboxes[1:]:
#       if checkbox.value:
#         selected_filters.append(checkbox.label)
#     return selected_filters

#   # -----------------------------------------------------------------------------------------------

#   def build_content(self):
#     filter_selector_container = self.create_filter_column()
#     self.content = filter_selector_container

#   # -----------------------------------------------------------------------------------------------

#   def create_filter_column(self):
#     filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()
#     filter_checkboxes = []
#     self.filter_checkboxes = filter_checkboxes  # Store for later access

#     # ---------------------------------------------------------------------------------------------

#     def update_filter_checkboxes(e):
#       if e.control == filter_checkboxes[0]:
#         for checkbox in filter_checkboxes[1:]:
#           checkbox.value = filter_checkboxes[0].value
#       else:
#         all_checked = True
#         for checkbox in filter_checkboxes[1:]:
#           if not checkbox.value:
#             all_checked = False
#             break
#         filter_checkboxes[0].value = all_checked
#       self.page.update()
#       if self.on_filter_changed_callback:
#         selected_filters = self.get_selected_filters()
#         self.on_filter_changed_callback(self.filter, selected_filters)

#       # ---------------------------------------------------------------------------------------------

#     all_filters_checkbox = ft.Checkbox(
#       label="all", value=False, on_change=update_filter_checkboxes
#     )
#     filter_checkboxes.append(all_filters_checkbox)

#     for filter_name in filter_names:
#       filter_checkboxes.append(
#         ft.Checkbox(label=filter_name, value=False, on_change=update_filter_checkboxes)
#       )

#     width = Helper.get_longest_pack_and_type_length() * 12 + 20
#     filter_text = "pack" if self.filter == Filters.PACK else "type"
#     inner_filter_header = ft.Container(
#       content=ft.Text(f" {filter_text}", color="#808080", size=24),
#       height=35 if self.filter == Filters.PACK else 30
#     )

#     inner_filter_column = ft.Container(
#       content=ft.Column(
#         spacing=9,
#         controls=filter_checkboxes,
#         width=width,
#         scroll=ft.ScrollMode.AUTO),
#     )

#     filter_column = ft.Container(
#       ft.Column(
#         [
#           inner_filter_header,
#           Spacer(-1.0),
#           inner_filter_column,
#         ]
#       ),
#       padding=10,
#       bgcolor="#232323",
#       border_radius= ft.border_radius.all(16)
#     )

#     return filter_column

#     # ---------------------------------------------------------------------------------------------

import flet as ft
from ports_dialog import PortsDialog
import consts as c
import helper_functions
from preset_data import PresetData

DEBUG_PAGE_SIZE = False

# ----------------------------------------------------------------------------------------------------

def page_resized(e, page):
  page.title = f"Osmose Presets - {page.window.width} x {page.window.height}"
  page.update()

# ----------------------------------------------------------------------------------------------------

def main(page: ft.Page):
  page.window.width = 1400
  page.window.height = 1000
  page.window.center()
  page.vertical_alignment = "center"
  page.horizontal_alignment = "center"
  if DEBUG_PAGE_SIZE:
    page.on_resized = page_resized(page)

  page.title = "Osmose Presets"

  # ----------------------------------------------------------------------------------------------------

  def show_dialog(e):
    longest = helper_functions.get_longest_port_width()
    excess = max(0, longest - c.DEFAULT_PORT_NAME_LENGTH) * c.PIXELS_PER_CHAR
    dlg_width = c.BASE_DIALOG_WIDTH + excess
    dlg = PortsDialog(width=dlg_width, height=250, title=ft.Text("Select MIDI Input Port"))  # fmt: skip
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  # ----------------------------------------------------------------------------------------------------

  def create_pack_column():
    pack_names = PresetData.get_packs()
    pack_checkboxes = []

    def update_pack_checkboxes(e):
      if e.control == pack_checkboxes[0]:
        for checkbox in pack_checkboxes[1:]:
          checkbox.value = pack_checkboxes[0].value
      else:
        all_checked = True
        for checkbox in pack_checkboxes[1:]:
          if not checkbox.value:
            all_checked = False
            break
        pack_checkboxes[0].value = all_checked
      page.update()

    all_packs_checkbox = ft.Checkbox(
      label="all", value=False, on_change=update_pack_checkboxes
    )
    pack_checkboxes.append(all_packs_checkbox)

    for pack_name in pack_names:
      pack_checkboxes.append(
        ft.Checkbox(label=pack_name, value=False, on_change=update_pack_checkboxes)
      )

    width = helper_functions.get_longest_pack_and_type_length() * 12 + 20

    inner_pack_column = ft.Container(
      content=ft.Column(controls=pack_checkboxes, width=width, scroll=ft.ScrollMode.AUTO),
      bgcolor="#232323",
      padding=10,
      border_radius= ft.border_radius.all(20)
    )

    pack_column = ft.Container(
      inner_pack_column,
      padding=10
    )

    return pack_column

  # ----------------------------------------------------------------------------------------------------

  def create_type_column():
    type_names = PresetData.get_types()
    type_checkboxes = []

    def update_type_checkboxes(e):
      if e.control == type_checkboxes[0]:
        for checkbox in type_checkboxes[1:]:
          checkbox.value = type_checkboxes[0].value
      else:
        all_checked = True
        for checkbox in type_checkboxes[1:]:
          if not checkbox.value:
            all_checked = False
            break
        type_checkboxes[0].value = all_checked
      page.update()

    all_types_checkbox = ft.Checkbox(
      label="all", value=False, on_change=update_type_checkboxes
    )
    type_checkboxes.append(all_types_checkbox)

    for type_name in type_names:
      type_checkboxes.append(
        ft.Checkbox(label=type_name, value=False, on_change=update_type_checkboxes)
      )

    width = helper_functions.get_longest_pack_and_type_length() * 12 + 20

    inner_type_column = ft.Container(
      content=ft.Column(controls=type_checkboxes, width=width, scroll=ft.ScrollMode.AUTO),
      bgcolor="#232323",
      padding=10,
      border_radius= ft.border_radius.all(20)
    )

    type_column = ft.Container(
      inner_type_column,
      padding=10
    )

    return type_column

  # ----------------------------------------------------------------------------------------------------

  page.add(
    ft.Row(
      [
        ft.Column(
          [
            ft.Text("   pack", color="#808080", size=24),
            create_pack_column(),
            ft.Text("   type", color="#808080", size=24),
            create_type_column(),
          ],
          width=200,
        ),
        ft.Column(
          [
            ft.FilledButton(
              " Select MIDI Input Port ", color="#101010", on_click=show_dialog,
            )
          ],
          expand=True,
        ),
      ],
      expand=True,
    )
  )

  PresetData.add_pack_filter("factory")
  PresetData.add_type_filter(["organ", "mallets"])

  print("")
  print(PresetData.get_packs())

  print("")
  pack = "expansion_01"
  print(pack)
  print(PresetData.get_types(pack))

  print("")
  pack = "factory"
  print(pack)
  print(PresetData.get_types(pack))

  presets = PresetData.get_presets()
  if presets:
    for preset in presets:
      print(preset)

  print(helper_functions.get_longest_pack_and_type_length())

  page.update()


ft.app(target=main)

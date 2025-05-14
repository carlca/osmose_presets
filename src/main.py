import flet as ft
from ports_dialog import PortsDialog
import consts as c
import helper_functions
from preset_data import PresetData

def main(page: ft.Page):

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

    page.title = "Osmose Presets"

    # Pack Selection Checkboxes
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

    all_packs_checkbox = ft.Checkbox(label="all", value=False, on_change=update_pack_checkboxes)
    pack_checkboxes.append(all_packs_checkbox)

    for pack_name in pack_names:
        pack_checkboxes.append(ft.Checkbox(label=pack_name, value=False, on_change=update_pack_checkboxes))

    pack_column = ft.Column(controls=pack_checkboxes, width=300, scroll=ft.ScrollMode.AUTO)

    # Type Selection Checkboxes
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

    all_types_checkbox = ft.Checkbox(label="all", value=False, on_change=update_type_checkboxes)
    type_checkboxes.append(all_types_checkbox)


    for type_name in type_names:
        type_checkboxes.append(ft.Checkbox(label=type_name, value=False, on_change=update_type_checkboxes))

    type_column = ft.Column(controls=type_checkboxes, width=300, scroll=ft.ScrollMode.AUTO)


    # Layout
    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Packs", color="#808080", size=24),
                        pack_column,
                        ft.Text("Type", color="#808080", size=24),
                        type_column,
                    ],
                    width=300,  # Adjust width as needed
                ),
                ft.Column(
                    [
                        ft.ElevatedButton("Select MIDI Input Port", color="#808080", on_click=show_dialog),
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

    presets = PresetData.presets()
    if presets:
        for preset in presets:
            print(preset)

    page.update()


ft.app(target=main)

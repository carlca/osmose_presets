import flet as ft
import mido

class PortsDialog(ft.AlertDialog):
  def __init__(self, modal: bool = True):
    super().__init__(modal=modal)
    self.text = ft.Text("Available MIDI Ports")
    self.actions = [
      ft.TextButton("OK", on_click=self.close_dlg),
    ]
    try:
      self.input_ports = mido.get_input_names()
      print(f"PortsDialog: Found ports: {self.input_ports}") # Debugging
    except Exception as e:
      self.input_ports = [str(e)]
      print(f"PortsDialog: Error getting ports: {e}") # Debugging

    if self.input_ports:
      port_texts = [ft.Text(port) for port in self.input_ports]
      self.content = ft.Column([self.text] + port_texts)
      print("PortsDialog: Ports added to content") # Debugging
    else:
      self.content = ft.Column([self.text, ft.Text("No ports found")])
      print("PortsDialog: No ports found added to content") # Debugging

  def close_dlg(self, e):
    self.open = False
    self.page.update()


def open_ports_dialog(page: ft.Page):

  def show_dialog(e):
    dlg = PortsDialog()
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    page.update()
    print('Ports dialog should be displayed')
    page.update()

  button = ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog)
  return button

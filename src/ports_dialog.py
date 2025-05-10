import flet as ft
import mido
from consts import *
from helper_functions import *

class PortsDialog(ft.AlertDialog):
  def set_defaults(self):
    self.ports_per_page = 5
    self.curr_page = 0
    self.port_texts = []

  def create_radio_group(self):
    return ft.RadioGroup(content=ft.Column([]), on_change=self.handle_radio_change)

  def create_nav_buttons(self):
    prev_button = ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS, on_click=self.prev_page_handler, disabled=True)  # fmt: skip
    next_button = ft.IconButton(icon=ft.Icons.ARROW_FORWARD_IOS, on_click=self.next_page_handler, disabled=True)  # fmt: skip
    return (prev_button, next_button)

  def create_nav_row(self):
    return ft.Row([self.prev_button, self.next_button])

  def create_ports_row(self):
    return ft.Row([self.radio_group], alignment=ft.MainAxisAlignment.START)

  def create_action_buttons(self):
    ok_button = ft.TextButton("OK", on_click=self.ok_handler, disabled=True)
    cancel_button = ft.TextButton("Cancel", on_click=self.close_dlg)
    return (ok_button, cancel_button)

  def create_content_container(self, width, height):
    return ft.Container(width=width, height=height)

  def __init__(self, modal: bool = True, width: int = 400, height: int = 200, title=""):
    super().__init__(modal=modal)
    self.ports = get_input_ports()
    if DEBUG_LAYOUT:
      self.ports.append(TEXT_26)
      self.ports.append(TEXT_50)
    self.title = title
    self.set_defaults()
    self.radio_group = self.create_radio_group()
    self.prev_button, self.next_button = self.create_nav_buttons()
    self.button_row = self.create_nav_row()
    self.ports_row = self.create_ports_row()
    self.ok_button, self.cancel_button = self.create_action_buttons()
    self.actions = [self.ok_button, self.cancel_button]
    self.content_container = self.create_content_container(width, height)

    if self.ports:
      self.port_texts = [ft.Text(port) for port in self.ports]
      self.total_pages = (len(self.ports) + self.ports_per_page - 1) // self.ports_per_page # fmt: skip
      if self.total_pages > 1:
        self.next_button.disabled = False
      self.content_container.content = ft.Column([self.button_row, self.ports_row])
      self.content = self.content_container
    else:
      no_ports_text = ft.Text("No ports found")
      self.content_container.content = ft.Column([no_ports_text])
      self.content = self.content_container

  def handle_radio_change(self, e):
    self.ok_button.disabled = False
    self.ok_button.update()

  def ok_handler(self, e):
    print(f"Selected port: {self.radio_group.value}")  # Example
    self.close_dlg(e)  # Then close

  def update_ports(self, first_run=False):
    start = self.curr_page * self.ports_per_page
    end = min(start + self.ports_per_page, len(self.port_texts))
    ports = self.port_texts[start:end]
    radio_array = []
    for port in ports:
      radio_array.append(ft.Radio(value=port.value, label=port.value))
    self.radio_group.content = ft.Column(controls=radio_array, horizontal_alignment=ft.CrossAxisAlignment.START)  # fmt: skip
    if not first_run:
      self.update()

  def prev_page_handler(self, e):
    if self.curr_page > 0:
      self.curr_page -= 1
      self.next_button.disabled = False
      if self.curr_page == 0:
        self.prev_button.disabled = True
      self.update_ports()

  def next_page_handler(self, e):
    if self.curr_page < self.total_pages - 1:
      self.curr_page += 1
      self.prev_button.disabled = False
      if self.curr_page == self.total_pages - 1:
        self.next_button.disabled = True
      self.update_ports()

  def close_dlg(self, e):
    self.open = False
    self.page.update()

def open_ports_dialog(page: ft.Page):
  def show_dialog(e):
    longest = get_longest_port_width()
    excess = max(0, longest - DEFAULT_PORT_NAME_LENGTH) * PIXELS_PER_CHAR
    dlg_width = BASE_DIALOG_WIDTH + excess
    dlg = PortsDialog(width=dlg_width, height=250, title=ft.Text("Select MIDI Input Port")) # fmt: skip
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  button = ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog)
  return button

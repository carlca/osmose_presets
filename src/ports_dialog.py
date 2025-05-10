import flet as ft
import consts as c
import helper_functions

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

  def create_content_container(self, width: int, height: int):
    return ft.Container(width=width, height=height)

  def get_total_pages(self):
    return (len(self.ports) + self.ports_per_page - 1) // self.ports_per_page  # fmt: skip

  def display_ports(self):
    self.port_texts = [ft.Text(port) for port in self.ports]
    self.total_pages = self.get_total_pages()
    self.next_button.disabled = self.total_pages == 1
    self.content_container.content = ft.Column([self.button_row, self.ports_row])
    self.content = self.content_container

  def display_no_ports_warning(self):
    no_ports_text = ft.Text("No ports found")
    self.content_container.content = ft.Column([no_ports_text])
    self.content = self.content_container

  def __init__(self, modal: bool = True, width: int = 400, height: int = 200, title = ""):
    super().__init__(modal=modal)
    self.ports = helper_functions.get_input_ports()
    if c.DEBUG_LAYOUT:
      self.ports.append(c.TEXT_26)
      self.ports.append(c.TEXT_50)
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
      self.display_ports()
    else:
      self.display_no_ports_warning()

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
    self.change_page(c.BACKWARDS)

  def next_page_handler(self, e):
    self.change_page(c.FORWARDS)

  def change_page(self, direction: int):
    new_page = self.curr_page + direction
    if 0 <= new_page < self.total_pages:
      self.curr_page = new_page
      self.prev_button.disabled = (self.curr_page == 0)
      self.next_button.disabled = (self.curr_page == self.total_pages - 1)
      self.update_ports()

  def close_dlg(self, e):
    self.open = False
    self.page.update()

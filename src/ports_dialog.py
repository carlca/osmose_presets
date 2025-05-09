import flet as ft
import mido


class PortsDialog(ft.AlertDialog):
  def __init__(
    self, modal: bool = True, width: int = 400, height: int = 200,
    title = "",
  ):
    super().__init__(modal=modal)
    self.title = title

    self.ports_per_page = 5
    self.current_page = 0
    self.input_ports = []
    self.port_texts = []
    self.radio_group = ft.RadioGroup(
        content=ft.Column([]),
        on_change=self.handle_radio_change  # Add on_change handler
    )

    self.prev_button = ft.IconButton(icon = ft.Icons.ARROW_BACK_IOS, on_click = self.prev_page_handler, disabled = True)
    self.next_button = ft.IconButton(icon = ft.Icons.ARROW_FORWARD_IOS, on_click = self.next_page_handler, disabled = True)

    self.button_row = ft.Row([self.prev_button, self.next_button])
    self.ports_row = ft.Row(
      [
        self.radio_group,
      ],
      alignment=ft.MainAxisAlignment.START,
    )

    # Define OK and Cancel buttons
    self.ok_button = ft.TextButton("OK", on_click=self.ok_handler, disabled=True) # disabled initially
    self.cancel_button = ft.TextButton("Cancel", on_click=self.close_dlg)
    self.actions = [self.ok_button, self.cancel_button] # Add both to actions

    self.input_ports = get_input_ports()

    self.content_container = ft.Container(width=width, height=height)

    if self.input_ports:
      self.port_texts = [ft.Text(port) for port in self.input_ports]
      self.total_pages = (
        len(self.input_ports) + self.ports_per_page - 1
      ) // self.ports_per_page
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
    print(f"Selected port: {self.radio_group.value}") # Example
    self.close_dlg(e) # Then close

  def update_ports(self, first_run=False):
    start_index = self.current_page * self.ports_per_page
    end_index = min(start_index + self.ports_per_page, len(self.port_texts))
    current_ports = self.port_texts[start_index:end_index]
    radio_array = []
    for port in current_ports:
      radio_array.append(ft.Radio(value=port.value, label=port.value))
    self.radio_group.content = ft.Column(
        controls=radio_array,
        horizontal_alignment=ft.CrossAxisAlignment.START
    )
    if not first_run:
      self.update()

  def prev_page_handler(self, e):
    if self.current_page > 0:
      self.current_page -= 1
      self.next_button.disabled = False
      if self.current_page == 0:
        self.prev_button.disabled = True
      self.update_ports()

  def next_page_handler(self, e):
    if self.current_page < self.total_pages - 1:
      self.current_page += 1
      self.prev_button.disabled = False
      if self.current_page == self.total_pages - 1:
        self.next_button.disabled = True
      self.update_ports()

  def close_dlg(self, e):
    self.open = False
    self.page.update()

def get_input_ports():
  try:
    return mido.get_input_names()
  except Exception as e:
    return [str(e)]

def get_longest_port_width():
  ports = get_input_ports()
  max = 0
  for port in ports:
    if len(port) > max:
      max = len(port)
  return max

def open_ports_dialog(page: ft.Page):
  def show_dialog(e):
    # dlg_width = max(1076, get_longest_port_width() + 20)
    dlg_width = get_longest_port_width() + 20
    dlg = PortsDialog(width=dlg_width, height=250, title=ft.Text("Select MIDI Input Port"))
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  button = ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog)
  return button

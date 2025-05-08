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

    try:
      self.input_ports = mido.get_input_names()
    except Exception as e:
      self.input_ports = [str(e)]

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
    self.ok_button.update() # Update the button itself
    # Or, if the button is part of self.actions and self.actions is dynamic,
    # you might need to update self.actions_alignment or the dialog (self.update())

  def ok_handler(self, e):
    # Here you would typically get the selected value from self.radio_group.value
    # and do something with it before closing.
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


def open_ports_dialog(page: ft.Page):
  def show_dialog(e):
    dlg = PortsDialog(width=400, height=250, title=ft.Text("Select MIDI Input Port"))
    dlg.page = page
    page.overlay.append(dlg)
    dlg.open = True
    dlg.update_ports(True)
    page.update()

  button = ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog)
  return button


# import flet as ft
# import mido


# class PortsDialog(ft.AlertDialog):
#   def __init__(
#     self, modal: bool = True, width: int = 400, height: int = 200,
#     title = "",
#   ):
#     super().__init__(modal=modal)
#     self.title = title # Assign the title parameter to self.title

#     self.ports_per_page = 5
#     self.current_page = 0
#     self.input_ports = []
#     self.port_texts = []
#     self.radio_group = ft.RadioGroup(content=ft.Column([]))

#     self.prev_button = ft.IconButton(icon = ft.Icons.ARROW_BACK_IOS, on_click = self.prev_page_handler, disabled = True)
#     self.next_button = ft.IconButton(icon = ft.Icons.ARROW_FORWARD_IOS, on_click = self.next_page_handler, disabled = True)

#     # self.title_text = (ft.Text("Select MIDI Input Port", size=20),) # You might not need this if self.title is used
#     # self.title_row = ft.Row([self.title_text]) # You might not need this if self.title is used
#     self.button_row = ft.Row([self.prev_button, self.next_button])
#     self.ports_row = ft.Row(
#       [
#         self.radio_group,
#       ],
#       alignment=ft.MainAxisAlignment.START,
#     )

#     self.actions = [ft.TextButton("OK", on_click=self.close_dlg)]

#     try:
#       self.input_ports = mido.get_input_names()
#     except Exception as e:
#       self.input_ports = [str(e)]

#     self.content_container = ft.Container(width=width, height=height)

#     if self.input_ports:
#       self.port_texts = [ft.Text(port) for port in self.input_ports]
#       self.total_pages = (
#         len(self.input_ports) + self.ports_per_page - 1
#       ) // self.ports_per_page
#       if self.total_pages > 1:
#         self.next_button.disabled = False
#       self.content_container.content = ft.Column([self.button_row, self.ports_row])
#       self.content = self.content_container
#     else:
#       no_ports_text = ft.Text("No ports found")
#       # If self.title is set, AlertDialog handles it.
#       # So, the content for "no ports" might just be the message.
#       self.content_container.content = ft.Column([no_ports_text])
#       self.content = self.content_container

#   def update_ports(self, first_run=False):
#     start_index = self.current_page * self.ports_per_page
#     end_index = min(start_index + self.ports_per_page, len(self.port_texts))
#     current_ports = self.port_texts[start_index:end_index]
#     radio_array = []
#     for port in current_ports:
#       radio_array.append(ft.Radio(value=port.value, label=port.value))
#     self.radio_group.content = ft.Column(
#         controls=radio_array,
#         horizontal_alignment=ft.CrossAxisAlignment.START
#     )
#     if not first_run:
#       self.update()

#   def prev_page_handler(self, e):
#     if self.current_page > 0:
#       self.current_page -= 1
#       self.next_button.disabled = False
#       if self.current_page == 0:
#         self.prev_button.disabled = True
#       self.update_ports()

#   def next_page_handler(self, e):
#     if self.current_page < self.total_pages - 1:
#       self.current_page += 1
#       self.prev_button.disabled = False
#       if self.current_page == self.total_pages - 1:
#         self.next_button.disabled = True
#       self.update_ports()

#   def close_dlg(self, e):
#     self.open = False
#     self.page.update()


# def open_ports_dialog(page: ft.Page):
#   def show_dialog(e):
#     # The title is now passed to PortsDialog and handled there
#     dlg = PortsDialog(width=400, height=250, title=ft.Text("Select MIDI Input Port"))
#     dlg.page = page
#     page.overlay.append(dlg)
#     dlg.open = True
#     dlg.update_ports(True)
#     page.update()

#   button = ft.ElevatedButton("Open Ports Dialog", on_click=show_dialog)
#   return button

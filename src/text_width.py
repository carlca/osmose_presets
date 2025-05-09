import flet as ft

import random
import string


def get_random_string(length: int) -> str:
  all_chars = string.ascii_letters  # + string.digits
  rand_chars = random.choices(all_chars, k=length)
  # Join the chosen characters into a string
  return "".join(rand_chars)


def main(page: ft.Page):
  page.title = "AlertDialog examples"

  text_array = []

  for i in range(10):
    s = get_random_string(30).capitalize()

    text = ft.Text(s)
    text_array.append(text)

  page.add(ft.Column(text_array))

  page.update()

  # width = text.actual_width
  # count = len(text)
  # avg_width = width / count
  # print(f"avg_width: {avg_width}")

  # page.overlay.remove(text)
  # page.update()


ft.app(main)

# radio_array = []
# for port in current_ports:
#   radio_array.append(ft.Radio(value=port.value, label=port.value))
# self.radio_group.content = ft.Column(
#     controls=radio_array,
#     horizontal_alignment=ft.CrossAxisAlignment.START
# )
# if not first_run:
#   self.update()

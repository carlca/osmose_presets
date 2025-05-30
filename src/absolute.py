import flet as ft

def main(page: ft.Page):
   page.window.width = 800
   page.window.height = 600
   page.window.center()

   page.add(
      Positioned([
         [ft.TextField(multiline = True, min_lines = 20), [0, 0]],
         [ft.Button(text = "I am a quantum robot"), [70, 50]]
      ])
   )

ft.app(main)

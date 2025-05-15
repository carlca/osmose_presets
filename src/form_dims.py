import flet as ft


def main(page: ft.Page):
  page.window.width = 200  # window's width is 200 px
  page.window.height = 200  # window's height is 200 px
  page.window.resizable = False  # window is not resizable
  page.update()


ft.app(target=main)

import flet as ft


class Spacer(ft.Container):
   def __init__(self, height):
      super().__init__()
      self.height = height

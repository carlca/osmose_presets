import flet as ft
from preset_data import PresetData

def main(page: ft.Page):
  page.title = "GridView Example"
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 50
  # page.update()

  images = ft.GridView(
    expand=1,
    runs_count=1,
    max_extent=150,
    child_aspect_ratio=1.0,
    spacing=5,
    run_spacing=5,
  )

  page.add(images)

  for type in PresetData.get_types():
    images.controls.append(
      ft.Text(type)
    )

  page.update()


ft.app(main)

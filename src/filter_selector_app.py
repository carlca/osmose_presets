from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox
from textual import log


class FilterSelector(Vertical):
   def __init__(self):
      super().__init__()
      self.all_updating = False

   def compose(self) -> ComposeResult:
      self.border_title = "pack"
      yield Checkbox("all", id="check_all", classes="compact bold-text")
      filter_names = ["factory", "expansion_01"]
      for f_name in filter_names:
         safe_id = f"check_{f_name.lower().replace(' ', '_')}"
         yield Checkbox(f_name, id=safe_id, classes="compact bold-text")

   def get_other_checkboxes(self) -> list[Checkbox]:
      return [cb for cb in self.query(Checkbox) if cb.id != "check_all"]

   def all_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box_value = event.value
      other_checkboxes = self.get_other_checkboxes()
      all_box = self.query_one("#check_all", Checkbox)
      with all_box.prevent(Checkbox.Changed):
         if all_box_value != all(cb.value for cb in other_checkboxes):
            for checkbox in other_checkboxes:
               checkbox.value = all_box_value
               self.filter_changed(checkbox)

   def other_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box = self.query_one("#check_all", Checkbox)
      all_are_checked = all(cb.value for cb in self.get_other_checkboxes())
      if all_box.value != all_are_checked:
         all_box.value = all_are_checked
      self.filter_changed(event.checkbox)

   def filter_changed(self, checkbox) -> None:
      log(f"{checkbox.label} - {checkbox.value}")

   def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
      if event.checkbox.id == "check_all":
         self.all_checkbox_changed(event)
      else:
         self.other_checkbox_changed(event)

   def focus_first(self) -> None:
      """Sets focus on the first checkbox in this container."""
      checkboxes = self.query(Checkbox)
      if checkboxes:
         checkboxes[0].focus()

   def focus_last(self) -> None:
      """Sets focus on the last checkbox in this container."""
      checkboxes = self.query(Checkbox)
      if checkboxes:
         checkboxes[-1].focus()


class FilterSelectorApp(App):
   # Link to the CSS file
   # CSS_PATH = "osmose_presets.tcss"
   BINDINGS = [
      ("d", "toggle_dark", "Toggle dark mode"),
      ("q", "quit_app", "Quit"),
   ]

   def compose(self) -> ComposeResult:
      """create the layout and widgets for the app"""
      yield FilterSelector()

   def action_toggle_dark(self) -> None:
      ### an action to toggle dark mode ###
      self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

   def action_quit_app(self) -> None:
      ### An action to quit the app.###
      print("q pressed")
      self.exit()


if __name__ == "__main__":
   app = FilterSelectorApp()
   app.run()

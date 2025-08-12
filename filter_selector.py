from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox
from textual.events import Key
from preset_data import PresetData
from filters import Filters


class FilterSelector(Vertical):
   def __init__(self, filter, **kwargs):
      super().__init__(**kwargs)
      self.filter = filter
      # NO _updating flag is needed in this new version.

   def compose(self) -> ComposeResult:
      filter_name = "pack" if self.filter == Filters.PACK else "type"
      self.border_title = filter_name
      yield Checkbox("all", id="check_all", classes="compact bold-text")
      filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()
      for f_name in filter_names:
         safe_id = f"check_{f_name.lower().replace(' ', '_')}"
         yield Checkbox(f_name, id=safe_id, classes="compact bold-text")

   def get_other_checkboxes(self) -> list[Checkbox]:
      """Gets all checkboxes in this group except for the 'all' checkbox."""
      return [cb for cb in self.query(Checkbox) if cb.id != "check_all"]

   def all_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box_value = event.value
      other_checkboxes = self.get_other_checkboxes()
      if all_box_value != all(cb.value for cb in other_checkboxes):
         for checkbox in other_checkboxes:
            checkbox.value = all_box_value

   def other_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box = self.query_one("#check_all", Checkbox)
      all_are_checked = all(cb.value for cb in self.get_other_checkboxes())
      if all_box.value != all_are_checked:
         all_box.value = all_are_checked

   def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
      """ a state-aware handler that prevents chain reactions without locks """
      if event.checkbox.id == "check_all":
         self.all_checkbox_changed(event)
      else:
         self.other_checkbox_changed(event)

   def on_key(self, event: Key) -> None:
      """Handle up and down arrow key presses to navigate checkboxes."""
      if event.key not in ("up", "down"):
         return
      all_checkboxes = list(self.query(Checkbox))
      if not all_checkboxes:
         return
      try:
         focused_widget = self.app.focused
         current_index = all_checkboxes.index(focused_widget)
      except ValueError:
         # If focus is not on a known checkbox, default to the first one.
         all_checkboxes[0].focus()
         event.stop()
         return
      if event.key == "down":
         next_index = (current_index + 1) % len(all_checkboxes)
      else:  # event.key == "up"
         next_index = (current_index - 1 + len(all_checkboxes)) % len(all_checkboxes)
      all_checkboxes[next_index].focus()
      # Stop the event from propagating further (e.g., to scroll the container).
      event.stop()

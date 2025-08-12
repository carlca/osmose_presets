from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox
from preset_data import PresetData
from filters import Filters


class FilterSelector(Vertical):
   def __init__(self, filter, **kwargs):
      super().__init__(**kwargs)
      self.filter = filter
      self._updating = False

   def compose(self) -> ComposeResult:
      filter_name = "pack" if self.filter == Filters.PACK else "type"
      self.border_title = filter_name
      yield Checkbox("all", id="check_all", classes="compact bold-text")
      filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()
      for f_name in filter_names:
         safe_id = f"check_{f_name.lower().replace(' ', '_')}"
         yield Checkbox(f_name, id=safe_id, classes="compact bold-text")

   def get_other_checkboxes(self) -> list[Checkbox]:
      return [cb for cb in self.query(Checkbox) if cb.id != "check_all"]

   def all_checkbox_changed(self, event: Checkbox.Changed) -> None:
      new_value = event.value
      try:
         self._updating = True
         other_checkboxes = self.get_other_checkboxes()
         for checkbox in other_checkboxes:
            checkbox.value = new_value
      finally:
         self._updating = False

   def other_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box = self.query_one("#check_all", Checkbox)
      if not event.value:
         try:
            self._updating = True
            all_box.value = False
         finally:
            self._updating = False
      else:
         other_checkboxes = self.get_other_checkboxes()
         all_checked = all(cb.value for cb in other_checkboxes)
         try:
            self._updating = True
            all_box.value = all_checked
         finally:
            self._updating = False

   def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
      """Called when the value of any checkbox changes."""
      if self._updating:
         return
      # Logic for the 'all' checkbox
      if event.checkbox.id == "check_all":
         self.all_checkbox_changed(event)
      else:
         self.other_checkbox_changed(event)

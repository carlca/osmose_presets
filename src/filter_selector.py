from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Checkbox
from textual.events import Key
from textual import log
from preset_data import PresetData
from filters import Filters
from messages import FilterSelectionChanged


class FilterSelector(Vertical):
   def __init__(self, filter, **kwargs):
      super().__init__(**kwargs)
      self.filter = filter
      self.all_updating = False

   def get_filter(self) -> str:
      return "pack" if self.filter == Filters.PACK else "type"

   def compose(self) -> ComposeResult:
      self.border_title = self.get_filter()
      yield Checkbox("all", id="check_all", classes="compact bold-text")
      filter_names = PresetData.get_packs() if self.filter == Filters.PACK else PresetData.get_types()
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

   def other_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box = self.query_one("#check_all", Checkbox)
      all_are_checked = all(cb.value for cb in self.get_other_checkboxes())
      if all_box.value != all_are_checked:
         with all_box.prevent(Checkbox.Changed):
            all_box.value = all_are_checked

   def get_selected_filters(self) -> list[str]:
      """ return a list of labels for all checked checkboxes except 'all' """
      selected = []
      for checkbox in self.query(Checkbox):
         if checkbox.id != "check_all" and checkbox.value:
            selected.append(str(checkbox.label))
      return selected

   def filter_selection_changed(self, filter_type: str, selected_filters: list[str]) -> None:
      self.post_message(FilterSelectionChanged(filter_type, selected_filters))

   def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
      if event.checkbox.id == "check_all":
         self.all_checkbox_changed(event)
      else:
         self.other_checkbox_changed(event)
      self.filter_selection_changed(self.get_filter(), self.get_selected_filters())

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

   def on_key(self, event: Key) -> None:
      """Handle up/down arrow keys, posting messages at boundaries."""
      if event.key not in ("up", "down"):
         return

      all_checkboxes = list(self.query(Checkbox))
      if not all_checkboxes:
         return

      try:
         focused_widget = self.app.focused
         current_index = all_checkboxes.index(focused_widget)
      except ValueError:
         all_checkboxes[0].focus()
         event.stop()
         return

      if event.key == "down":
         if current_index == len(all_checkboxes) - 1:
            all_checkboxes[0].focus()
         else:
            all_checkboxes[current_index + 1].focus()

      else:
         if current_index == 0:
            all_checkboxes[len(all_checkboxes) - 1].focus()
         else:
            all_checkboxes[current_index - 1].focus()

      event.stop()

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
      self.current_index = 0

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

   def set_focus(self) -> None:
      checkboxes = self.query(Checkbox)
      if checkboxes and 0 <= self.current_index < len(checkboxes):
         checkboxes[self.current_index].focus()
      else:
         # If current_index is invalid, focus the first checkbox and reset current_index
         if checkboxes:
            checkboxes[0].focus()
            self.current_index = 0

   def on_key(self, event: Key) -> None:

      def process_down_key(checkboxes):
         if self.current_index == len(checkboxes) - 1:
            checkboxes[0].focus()
            self.current_index = 0
         else:
            checkboxes[self.current_index + 1].focus()
            self.current_index = self.current_index + 1

      def process_up_key(checkboxes):
         if self.current_index == 0:
            last_index = len(checkboxes) - 1
            checkboxes[last_index].focus()
            self.current_index = last_index
         else:
            checkboxes[self.current_index - 1].focus()
            self.current_index = self.current_index - 1

      checkboxes = list(self.query(Checkbox))
      if event.key in ("up", "down"):
         if event.key == "down":
            process_down_key(checkboxes)
         else:
            process_up_key(checkboxes)
         event.stop()

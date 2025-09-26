from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Checkbox
from textual import events
from textual.events import Key
from textual import log
from filters import Filters
from messages import FilterSelectionChanged


class MockCheckboxChanged:
   def __init__(self, checkbox, value):
      self.checkbox = checkbox
      self.value = value


class FilterSelector(VerticalScroll):
   def __init__(self, filter, select_all=False, **kwargs):
      super().__init__(**kwargs)
      self.filter = filter
      self.select_all = select_all
      self.all_updating = False
      self.current_index = 0
      self.filter_service = None
      self.preset_service = None

   def on_mount(self) -> None:
      # Get services from app (if not already set in compose)
      if not self.filter_service:
         self.filter_service = self.app.services.get_filter_service()
      if not self.preset_service:
         self.preset_service = self.app.services.get_preset_service()
      # If select_all is True, simulate user checking all boxes
      if self.select_all:
         # Create a mock event for the "all" checkbox
         all_box = self.query_one("#check_all", Checkbox)
         # Manually trigger the change behavior
         self.all_checkbox_changed(MockCheckboxChanged(all_box, True))
         self.filter_selection_changed(self.get_filter(), self.get_selected_filters())

   def get_filter(self) -> str:
      match self.filter:
         case Filters.PACK:
            return "pack"
         case Filters.TYPE:
            return "type"
         case Filters.CHAR:
            return "char"
         case _:
            return "undefined"

   def get_filter_names(self) -> list[str]:
      # Get service if not already available (compose runs before on_mount)
      if not self.preset_service and hasattr(self, "app"):
         self.preset_service = self.app.services.get_preset_service()
      if not self.preset_service:
         return []
      match self.filter:
         case Filters.PACK:
            return self.preset_service.get_available_packs()
         case Filters.TYPE:
            return self.preset_service.get_available_types()
         case Filters.CHAR:
            return self.preset_service.get_available_chars()
         case _:
            return []

   def compose(self) -> ComposeResult:
      title = self.get_filter()
      if title == "char":
         title = "character"
      self.border_title = title
      yield Checkbox("all", id="check_all", classes="compact bold-text", value=self.select_all)
      filter_names = self.get_filter_names()
      for f_name in filter_names:
         safe_id = f"check_{f_name.lower().replace(' ', '_')}"
         yield Checkbox(f_name, id=safe_id, classes="compact bold-text", value=self.select_all)

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
      # Don't update filter service here - let on_checkboxf.update_filter_service()

   def other_checkbox_changed(self, event: Checkbox.Changed) -> None:
      all_box = self.query_one("#check_all", Checkbox)
      all_are_checked = all(cb.value for cb in self.get_other_checkboxes())
      if all_box.value != all_are_checked:
         with all_box.prevent(Checkbox.Changed):
            all_box.value = all_are_checked

   def get_selected_filters(self) -> list[str]:
      """return a list of labels for all checked checkboxes except 'all'"""
      selected = []
      for checkbox in self.query(Checkbox):
         if checkbox.id != "check_all" and checkbox.value:
            selected.append(str(checkbox.label))
      return selected

   def update_service_filters(self) -> None:
      """Update the filter service based on current selections."""
      if not self.filter_service:
         return
      
      selected = set(self.get_selected_filters())
      log(f"FilterSelector.update_service_filters - {self.get_filter()}: {len(selected)} items selected")
      match self.filter:
         case Filters.PACK:
            self.filter_service.set_pack_filter(selected)
            log(f"Updated pack filter with {selected}")
         case Filters.TYPE:
            self.filter_service.set_type_filter(selected)
            log(f"Updated type filter with {selected}")
         case Filters.CHAR:
            self.filter_service.set_char_filter(selected)
            log(f"Updated char filter with {selected}")

   def filter_selection_changed(self, filter_type: str, selected_filters: list[str]) -> None:
      # Update the service
      self.update_service_filters()
      # Still send the message for compatibility
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

   def on_click(self, event: events.Click) -> None:
      self.app.remove_all_focused_border_titles()
      self.add_class("focused")
      # Don't stop the event, so child widgets can still process it

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

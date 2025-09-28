from textual.widgets import DataTable
from textual.widgets._data_table import RowRenderables, default_cell_formatter, _EMPTY_TEXT
from textual.message import Message
from textual.events import Click
from textual.events import MouseDown
from rich.console import RenderableType
from rich.text import Text
from typing import Literal
from itertools import zip_longest


class AlignedDataTableClicked(Message):
   """Posted when the AlignedDataTable is clicked."""

   pass


class AlignedDataTable(DataTable):
   """A DataTable subclass that supports column alignment for both headers and cells."""

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self._column_alignments = {}

   def add_column(
      self,
      label: str,
      *,
      width=None,
      key=None,
      default=None,
      justify: Literal["left", "center", "right"] = "left",
   ) -> str:
      """Add a column to the table with optional alignment for label and data cells.

      Args:
         label: The label to show atop the column.
         width: Width of the column in cells or None to fit content.
         key: A key which uniquely identifies this column.
         default: The default value to insert into pre-existing rows.
         justify: Horizontal alignment of the column label and cells.

      Returns:
         The column key (auto-generated if not provided).
      """
      # Create a Text object for the label with the specified alignment.
      aligned_label = Text.from_markup(label, justify=justify)
      column_key = super().add_column(aligned_label, width=width, key=key, default=default)
      self._column_alignments[column_key] = justify
      return column_key

   def _compute_row_renderables(self, row_index: int) -> RowRenderables:
      """Override to apply column alignment during cell formatting."""
      ordered_columns = self.ordered_columns
      if row_index == -1:
         # Header row
         header_row: list[RenderableType] = [column.label for column in ordered_columns]
         return RowRenderables(None, header_row)

      ordered_row = self.get_row_at(row_index)
      row_key = self._row_locations.get_key(row_index)
      if row_key is None:
         return RowRenderables(None, [])

      row_metadata = self.rows.get(row_key)
      if row_metadata is None:
         return RowRenderables(None, [])

      formatted_row_cells: list[RenderableType] = [
         (
            _EMPTY_TEXT
            if datum is None
            else self._aligned_cell_formatter(
               datum,
               column_key,
               wrap=row_metadata.height != 1,
               height=row_metadata.height,
            )
            or _EMPTY_TEXT
         )
         for datum, column_key in zip_longest(ordered_row, self.columns)
      ]

      label = default_cell_formatter(row_metadata.label, wrap=False, height=1) if row_metadata.label is not None else None

      return RowRenderables(label, formatted_row_cells)

   def _aligned_cell_formatter(self, obj, column_key, wrap=True, height=0):
      """Custom cell formatter that applies column alignment."""
      justify = self._column_alignments.get(column_key, "left")
      if isinstance(obj, str):
         return Text.from_markup(obj, justify=justify)
      elif isinstance(obj, float):
         content = f"{obj:.2f}"
      elif isinstance(obj, Text):
         aligned = obj.copy()
         aligned.justify = justify
         return aligned
      else:
         content = str(obj)
      return Text(content, justify=justify, no_wrap=not wrap)

   def on_click(self, event: Click) -> None:
      self.post_message(AlignedDataTableClicked())

   async def on_mouse_down(self, event: MouseDown) -> None:
      await self._on_click(event)  # type: ignore

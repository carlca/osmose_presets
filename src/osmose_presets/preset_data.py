from textual import log
import json
import os
from dataclasses import dataclass, field, fields
from typing import List


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESET_DATA = os.path.join(SCRIPT_DIR, "OsmosePresets.json")


@dataclass
class Preset:
   pack: str
   type: str
   cc0: int
   pgm: int
   preset: str
   chars: List[str] = field(default_factory=list)

   def get_field_widths(self) -> list[int]:
      result = []
      for f in fields(self):
         value = getattr(self, f.name)
         if isinstance(value, int):
            result.append(len(str(value)))
         elif isinstance(value, list):
            result.append(len(", ".join(str(item) for item in value)))
         else:
            result.append(len(value))
      return result


class PresetData:
   cached_presets = []
   pack_filters = []
   type_filters = []
   char_filters = []
   search_term = ""

   @staticmethod
   def load_from_json(file_path: str) -> List[Preset]:
      loaded_presets = []
      with open(file_path, "r", encoding="utf-8") as f:
         data = json.load(f)

         for preset_dict in data:
            preset = Preset(
               pack=preset_dict.get("pack"),
               type=preset_dict.get("type"),
               cc0=preset_dict.get("cc0"),
               pgm=preset_dict.get("pgm"),
               preset=preset_dict.get("preset"),
               chars=preset_dict.get("chars", []),
            )
            loaded_presets.append(preset)
      return loaded_presets

   @staticmethod
   def evaluate_search(search_term, target_string):
      # Split the search term by " OR " to handle the lowest precedence operator.
      or_clauses = [clause.strip() for clause in search_term.split(" OR ")]
      # Evaluate each "AND" clause independently.
      # Using a generator expression for efficiency.
      and_results = (all(term.strip() in target_string for term in clause.split(" AND ")) for clause in or_clauses)

      # Step 3: The final result is TRUE if any of the "AND" clauses were a match.
      return any(and_results)

   @staticmethod
   def get_presets():
      result = []
      # only apply filters if both filters are active
      if not PresetData.pack_filters or not PresetData.type_filters or not PresetData.char_filters:
         return result
      # build filtered list from cached list
      for preset in PresetData.cached_presets:
         pack_ok = not PresetData.pack_filters or preset.pack in PresetData.pack_filters
         type_ok = not PresetData.type_filters or preset.type in PresetData.type_filters
         char_ok = not PresetData.char_filters or set(preset.chars) & set(PresetData.char_filters)
         # search_ok = not PresetData.search_term or PresetData.search_term in preset.preset
         search_ok = not PresetData.search_term or PresetData.evaluate_search(PresetData.search_term, preset.preset)

         if pack_ok and type_ok and char_ok and search_ok:
            result.append(preset)

      return result

   @staticmethod
   def preset_to_tuple(preset: Preset) -> tuple:
      return tuple(", ".join(value) if isinstance(value, list) else value for f in fields(preset) for value in [getattr(preset, f.name)])

   @staticmethod
   def flatten_presets_to_tuples(preset_list: List[Preset]) -> List[tuple]:
      return [PresetData.preset_to_tuple(preset) for preset in preset_list]

   @staticmethod
   def get_presets_as_tuples():
      return PresetData.flatten_presets_to_tuples(PresetData.get_presets())

   @staticmethod
   def get_all_presets():
      return PresetData.cached_presets

   @staticmethod
   def get_preset_max_widths() -> list[int]:
      if not PresetData.cached_presets:
         return []
      num_fields = len(PresetData.cached_presets[0].get_field_widths())
      result = [0] * num_fields
      for preset in PresetData.cached_presets:
         widths = preset.get_field_widths()
         for i, width in enumerate(widths):
            if width > result[i]:
               result[i] = width
      return result

   @staticmethod
   def get_chars() -> list[str]:
      result = []
      if not PresetData.cached_presets:
         return result
      unassigned_found = False
      for preset in PresetData.cached_presets:
         for char in preset.chars:
            if char not in result:
               if char != "UNASSIGNED":
                  result.append(char)
            if char == "UNASSIGNED":
               unassigned_found = True
      result.sort()
      if unassigned_found:
         result.append("UNASSIGNED")
      return result

   @staticmethod
   def set_search_filter(search_term):
      PresetData.search_term = search_term

   @staticmethod
   def get_all_preset_names():
      result = []
      for preset in PresetData.cached_presets:
         result.append(preset.preset)
      return result

   @staticmethod
   def clear_pack_filters():
      PresetData.pack_filters.clear()

   @staticmethod
   def add_pack_filter(pack_filter):
      if isinstance(pack_filter, str):
         PresetData.pack_filters.append(pack_filter)
      elif isinstance(pack_filter, list):
         PresetData.pack_filters.extend(pack_filter)
      else:
         raise TypeError("pack_filter must be a string or a list of strings")

   @staticmethod
   def clear_type_filters():
      PresetData.type_filters.clear()

   @staticmethod
   def add_type_filter(type_filter):
      if isinstance(type_filter, str):
         PresetData.type_filters.append(type_filter)
      elif isinstance(type_filter, list):
         PresetData.type_filters.extend(type_filter)
      else:
         raise TypeError("type_filter must be a string or a list of strings")

   @staticmethod
   def clear_char_filters():
      PresetData.char_filters.clear()

   @staticmethod
   def add_char_filter(char_filter):
      if isinstance(char_filter, str):
         PresetData.char_filters.append(char_filter)
      elif isinstance(char_filter, list):
         PresetData.char_filters.extend(char_filter)
      else:
         raise TypeError("char_filter must be a string or a list of strings")

   @staticmethod
   def get_packs():
      packs = []
      for preset in PresetData.cached_presets:
         if preset.pack not in packs:
            packs.append(preset.pack)
      return packs

   @staticmethod
   def get_types(pack=""):
      types = []
      for preset in PresetData.cached_presets:
         if (pack and preset.pack == pack) or not pack:
            if preset.type not in types:
               types.append(preset.type)
      return types


if not PresetData.cached_presets:
   PresetData.cached_presets = PresetData.load_from_json(PRESET_DATA)

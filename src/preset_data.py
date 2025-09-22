import json
import os
from dataclasses import dataclass, field, fields
from typing import List
import functools

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESET_DATA = os.path.join(SCRIPT_DIR, "OsmosePresets.json")


@dataclass
class Preset:
   pack: str
   type: str
   cc0: int
   pgm: int
   preset: str
   characters: List[str] = field(default_factory=list)

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
   sort_criteria = []  # e.g., [('pack', True), ('preset', False)]

   @staticmethod
   def add_sort_criterion(field_name: str, ascending: bool = True):
      PresetData.sort_criteria.append((field_name, ascending))

   @staticmethod
   def set_sort_criteria(criteria: List[tuple[str, bool]]):
      PresetData.sort_criteria = list(criteria)

   @staticmethod
   def clear_sort_criteria():
      PresetData.sort_criteria.clear()

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
               characters=preset_dict.get("characters", []),
            )
            loaded_presets.append(preset)
      return loaded_presets

   @staticmethod
   def get_presets():
      result = []
      # only apply filters if both filters are active
      if not PresetData.pack_filters or not PresetData.type_filters:
         return result
      # build filtered list from cached list
      for preset in PresetData.cached_presets:
         pack_filtered = not PresetData.pack_filters or preset.pack in PresetData.pack_filters
         type_filtered = not PresetData.type_filters or preset.type in PresetData.type_filters
         if pack_filtered and type_filtered:
            result.append(preset)
      # if sort_criteria active and an non-empty results
      if PresetData.sort_criteria and result:
         # nested compare function used by sort
         def compare_presets(p1: Preset, p2: Preset):
            for field_name, ascending in PresetData.sort_criteria:
               v1 = getattr(p1, field_name)
               v2 = getattr(p2, field_name)
               if v1 < v2:
                  return -1 if ascending else 1
               if v1 > v2:
                  return 1 if ascending else -1
            return 0

         # apply the sort function
         result.sort(key=functools.cmp_to_key(compare_presets))
      # return fileterd and optionally sorted presets
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
   def get_characters() -> list[str]:
      result = []
      if not PresetData.cached_presets:
         return result
      for preset in PresetData.cached_presets:
         for character in preset.characters:
            if character not in result:
               result.append(character)
      return result

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

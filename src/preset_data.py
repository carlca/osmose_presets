import os
import json
from dataclasses import dataclass, field
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
  characters: List[str] = field(default_factory=list)


class PresetData:
  cached_presets = []
  pack_filters = []
  type_filters = []

  @staticmethod
  def load_from_json(file_path: str) -> List[Preset]:
    loaded_presets = []
    with open(file_path, 'r', encoding='utf-8') as f:
      data = json.load(f)

      for preset_dict in data:
        preset = Preset(
          pack=preset_dict.get("pack"),
          type=preset_dict.get("type"),
          cc0=preset_dict.get("cc0"),
          pgm=preset_dict.get("pgm"),
          preset=preset_dict.get("preset"),
          characters=preset_dict.get("characters", [])
        )
        loaded_presets.append(preset)
    return loaded_presets

  @staticmethod
  def presets():
    result = []
    for preset in PresetData.cached_presets:
      pack_filtered = not PresetData.pack_filters or preset.pack in PresetData.pack_filters
      type_filtered = not PresetData.type_filters or preset.type in PresetData.type_filters
      if pack_filtered and type_filtered:
        result.append(preset)
    return result

  @staticmethod
  def clear_pack_filters():
    PresetData.pack_filters.clear()

  @staticmethod
  def add_pack_filter(pack_filter):
    PresetData.pack_filters.append(pack_filter)

  @staticmethod
  def clear_type_filters():
    PresetData.type_filters.clear()

  @staticmethod
  def add_type_filter(pack_filter):
    PresetData.type_filters.append(pack_filter)

  @staticmethod
  def get_packs():
    packs = []
    for preset in PresetData.cached_presets:
      if preset.pack not in packs:
        packs.append(preset.pack)
    return packs

  @staticmethod
  def get_types(pack = ""):
    types = []
    for preset in PresetData.cached_presets:
      if pack and preset.pack == pack or not pack:
        if preset.type not in types:
          types.append(preset.type)
    return types


if not PresetData.cached_presets:
  PresetData.cached_presets = PresetData.load_from_json(PRESET_DATA)

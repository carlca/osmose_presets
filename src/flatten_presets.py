from dataclasses import dataclass, field, fields
from typing import List, Any


@dataclass
class Preset:
   pack: str
   type: str
   cc0: int
   pgm: int
   preset: str
   characters: List[str] = field(default_factory=list)


# Sample data
presets = [
   Preset(pack="factory", type="keys", cc0=30, pgm=4, preset="aerials", characters=["analog"]),
   Preset(pack="factory", type="keys", cc0=30, pgm=10, preset="ambiant analog 1", characters=["analog", "big", "echo", "reverberant", "synthetic"]),
   Preset(pack="factory", type="keys", cc0=30, pgm=11, preset="analog adsr", characters=["analog", "synthetic"]),
   Preset(
      pack="factory", type="keys", cc0=30, pgm=12, preset="analog scream", characters=["aggressive", "analog", "big", "distorted", "noise", "stereo", "warm"]
   ),
   Preset(pack="factory", type="keys", cc0=30, pgm=18, preset="aqueous feel", characters=["airy", "bright", "clean", "digital"]),
   Preset(pack="factory", type="keys", cc0=30, pgm=22, preset="azure key", characters=["bright", "clean", "digital", "simple", "soft"]),
   Preset(pack="factory", type="keys", cc0=30, pgm=50, preset="bowedsymphfm", characters=["acoustic", "clean", "fm", "shaking", "soft", "stereo"]),
   Preset(pack="factory", type="keys", cc0=30, pgm=78, preset="classicana key", characters=["analog", "simple"]),
]


def preset_to_tuple(preset: Preset) -> tuple:
   """Convert a Preset object to a tuple of its field values."""
   return tuple(getattr(preset, f.name) for f in fields(preset))


def flatten_presets_to_tuples(preset_list: List[Preset]) -> List[tuple]:
   """Convert a list of Preset objects to a list of tuples containing their field values."""
   return [preset_to_tuple(preset) for preset in preset_list]


# Example usage
if __name__ == "__main__":
   result = flatten_presets_to_tuples(presets)
   print(result)

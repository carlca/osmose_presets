import json
import os
import sys
from pathlib import Path


class Helper:
   @staticmethod
   def get_config_path() -> Path:
      if sys.platform == "darwin":
         config_dir = (
            Path.home()
            / "Library"
            / "Application Support"
            / "OsmosePresets"
         )

      elif os.name == "nt":
         config_dir = (
            Path(os.environ.get("APPDATA", Path.home()))
            / "OsmosePresets"
         )

      else:
         config_dir = (
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
            / "OsmosePresets"
         )

      config_dir.mkdir(parents=True, exist_ok=True)

      return config_dir / "config.json"

   @staticmethod
   def read_config():
      config_path = Helper.get_config_path()

      try:
         if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
               return json.load(f)
      except json.decoder.JSONDecodeError:
         return {}

      return {}

   @staticmethod
   def write_config(config_data):
      config_path = Helper.get_config_path()

      with config_path.open("w", encoding="utf-8") as f:
         json.dump(config_data, f, indent=2)

# import os
# import json


# class Helper:
#    @staticmethod
#    def get_config_path():
#       """Return the absolute path to the config.json file in the same directory as this script."""
#       script_dir = os.path.dirname(os.path.abspath(__file__))
#       return os.path.join(script_dir, "config.json")

#    @staticmethod
#    def read_config():
#       config_path = Helper.get_config_path()
#       try:
#          if os.path.exists(config_path):
#             with open(config_path, "r") as f:
#                return json.load(f)
#       except json.decoder.JSONDecodeError:
#          return {}
#       return {}

#    @staticmethod
#    def write_config(config_data):
#       config_path = Helper.get_config_path()
#       with open(config_path, "w") as f:
#          json.dump(config_data, f, indent=2)

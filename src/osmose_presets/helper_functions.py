import json
from pathlib import Path

from platformdirs import user_config_dir


class Helper:
   @staticmethod
   def get_config_path() -> Path:
      config_dir = Path(
         user_config_dir(
            appname="OsmosePresets",
            appauthor=False,
         )
      )

      config_dir.mkdir(parents=True, exist_ok=True)

      return config_dir / "config.json"

   @staticmethod
   def read_config() -> dict:
      config_path = Helper.get_config_path()

      try:
         with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

      except FileNotFoundError:
         return {}

      except json.JSONDecodeError:
         return {}

   @staticmethod
   def write_config(config_data: dict) -> None:
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

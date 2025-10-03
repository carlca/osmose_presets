import os
import json


class Helper:
    @staticmethod
    def get_config_path():
        """Return the absolute path to the config.json file in the same directory as this script."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "config.json")

    @staticmethod
    def read_config():
        config_path = Helper.get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return json.load(f)
        except json.decoder.JSONDecodeError:
            return {}
        return {}

    @staticmethod
    def write_config(config_data):
        config_path = Helper.get_config_path()
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)


# class Helper:
#    @staticmethod
#    def read_config():
#       config_path = "config.json"
#       try:
#          if os.path.exists(config_path):
#             with open(config_path, "r") as f:
#                return json.load(f)
#       except json.decoder.JSONDecodeError:
#          return {}
#       return {}

#    @staticmethod
#    def write_config(config_data):
#       config_path = "config.json"
#       with open(config_path, "w") as f:
#          json.dump(config_data, f, indent=2)

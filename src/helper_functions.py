import mido
import consts as c
from preset_data import PresetData

# ----------------------------------------------------------------------------------------------------

class Helper:

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_input_ports():
    try:
      return mido.get_input_names()
    except Exception as e:
      print(f"Error getting MIDI input ports: {e}")
      return []

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_width(strings):
    max_len = 0
    for string in strings:
      if len(string) > max_len:
        max_len = len(string)
    return max_len

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_preset_width():
    return Helper.get_longest_width(PresetData.get_all_preset_names())

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_character_list(preset):
    return ", ".join(preset.characters) if preset.characters else ""

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_characters_width():
    characters = []
    for preset in PresetData.get_all_presets():
      characters.append(Helper.get_character_list(preset))
    return Helper.get_longest_width(characters)

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_port_width():
    ports = Helper.get_input_ports()
    if c.DEBUG_LAYOUT:
      ports.append(c.TEXT_26)
      ports.append(c.TEXT_50)
    return Helper.get_longest_width(ports)

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_pack_width():
    return Helper.get_longest_width(PresetData.get_packs())

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_type_width():
    return Helper.get_longest_width(PresetData.get_types())

  # ----------------------------------------------------------------------------------------------------

  @staticmethod
  def get_longest_pack_and_type_length():
    return max(get_longest_pack_width(), get_longest_type_width())

  # ----------------------------------------------------------------------------------------------------

import mido
import consts as c
from preset_data import PresetData

# ----------------------------------------------------------------------------------------------------

def get_input_ports():
  try:
    return mido.get_input_names()
  except Exception as e:
    print(f"Error getting MIDI input ports: {e}")
    return []

# ----------------------------------------------------------------------------------------------------

def get_longest_width(strings):
  max_len = 0
  for string in strings:
    if len(string) > max_len:
      max_len = len(string)
  return max_len

# ----------------------------------------------------------------------------------------------------

def get_longest_port_width():
  ports = get_input_ports()
  if c.DEBUG_LAYOUT:
    ports.append(c.TEXT_26)
    ports.append(c.TEXT_50)
  return get_longest_width(ports)

# ----------------------------------------------------------------------------------------------------

def get_longest_pack_width():
  return get_longest_width(PresetData.get_packs())

# ----------------------------------------------------------------------------------------------------

def get_longest_type_width():
  return get_longest_width(PresetData.get_types())

# ----------------------------------------------------------------------------------------------------

def get_longest_pack_and_type_length():
  return max(get_longest_pack_width(), get_longest_type_width())

# ----------------------------------------------------------------------------------------------------

import mido
from consts import *

def get_input_ports():
  try:
    return mido.get_input_names()
  except Exception as e:
    print(f"Error getting MIDI input ports: {e}")
    return[]

def get_longest_port_width():
  ports = get_input_ports()
  if DEBUG_LAYOUT:
    ports.append(TEXT_26)
    ports.append(TEXT_50)
  max_len = 0
  for port in ports:
    if len(port) > max_len:
      max_len = len(port)
  return max_len

import mido
from consts import *

def get_input_ports():
  try:
    return mido.get_input_names()
  except Exception as e:
    return [str(e)]

def get_longest_port_width():
  ports = get_input_ports()
  if DEBUG_LAYOUT:
    ports.append(TEXT_26)
    ports.append(TEXT_50)
  max = 0
  for port in ports:
    if len(port) > max:
      max = len(port)
  return max

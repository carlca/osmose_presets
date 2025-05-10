import mido
import consts as c

def get_input_ports():
  try:
    return mido.get_input_names()
  except Exception as e:
    print(f"Error getting MIDI input ports: {e}")
    return[]

def get_longest_port_width():
  ports = get_input_ports()
  if c.DEBUG_LAYOUT:
    ports.append(c.TEXT_26)
    ports.append(c.TEXT_50)
  max_len = 0
  for port in ports:
    if len(port) > max_len:
      max_len = len(port)
  return max_len

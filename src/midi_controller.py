import mido
import time


class MidiController:
   @staticmethod
   def send_preset_change(port, cc, pgm):
      try:
         output = mido.open_output(port)
      except OSError as e:
         print(f"Error opening MIDI port '{port}': {e}")
         return False

      cc_msg = mido.Message("control_change", channel=0, control=0, value=cc)
      print(f"Sending CC message: {cc_msg.hex()}")
      output.send(cc_msg)

      time.sleep(0.4)

      pgm_msg = mido.Message("program_change", channel=0, program=pgm)
      print(f"Sending PGM message: {pgm_msg.hex()}")
      output.send(pgm_msg)

      output.close()

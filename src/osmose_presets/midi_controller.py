import mido
import time
from textual import log


class MidiController:
   @staticmethod
   def open_midi_port(port_name: str, delay: float = 0.5) -> mido.ports.BaseOutput:
      try:
         midi_port = mido.open_output(port_name)
         log(f"Initially opened port: {port_name}")
         midi_port.close()
         # Give it time to reset
         time.sleep(delay)
         midi_port = mido.open_output(port_name)
         log(f"Successfully opened port: {port_name}")
         return midi_port
      except Exception as e:
         log(f"Error opening {port_name}: {e}")
         raise

   @staticmethod
   def send_preset_change(port: str, cc: int, pgm: int):
      output = MidiController.open_midi_port(port)

      cc_msg = mido.Message("control_change", channel=0, control=0, value=cc)
      log(f"Sending CC message: {cc_msg.hex()}")
      output.send(cc_msg)
      log(f"Sent CC message: {cc_msg.hex()}")

      time.sleep(0.4)

      pgm_msg = mido.Message("program_change", channel=0, program=pgm)
      log(f"Sending PGM message: {pgm_msg.hex()}")
      output.send(pgm_msg)
      log(f"Sent PGM message: {pgm_msg.hex()}")

      output.close()

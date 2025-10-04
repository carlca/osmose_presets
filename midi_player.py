import mido
import time

# The name of your MIDI output port
port_name = "MIDIOUT2 (Osmose) 2"

# Ensure we're using the correct backend
mido.set_backend("mido.backends.rtmidi")

try:
   # Open the MIDI output port
   with mido.open_output(port_name) as port:
      print(f"Opened port: {port_name}")

      # Define a sequence of MIDI notes to play (note number, velocity, duration)
      notes = [
         (60, 64, 0.5),  # C4
         (62, 64, 0.5),  # D4
         (64, 64, 0.5),  # E4
         (65, 64, 0.5),  # F4
         (67, 64, 0.5),  # G4
         (69, 64, 0.5),  # A4
         (71, 64, 0.5),  # B4
         (72, 64, 1.0),  # C5
      ]

      # Play each note in the sequence
      for note, velocity, duration in notes:
         # Send a note on message
         port.send(mido.Message("note_on", channel=0, note=note, velocity=velocity))
         print(f"Playing note {note} with velocity {velocity}")

         # Wait for the duration of the note
         time.sleep(duration)

         # Send a note off message
         port.send(mido.Message("note_off", channel=0, note=note, velocity=velocity))

      print("Finished playing notes")

except ValueError as e:
   print(f"Error: Could not open MIDI port '{port_name}'. Make sure the port exists and is available.")
   print(f"Available output ports: {mido.get_output_names()}")

except Exception as e:
   print(f"Unexpected error: {e}")
   print("Make sure your MIDI device is connected and not being used by another application.")

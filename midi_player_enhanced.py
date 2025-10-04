import mido
import time

# Ensure we're using the correct backend
mido.set_backend("mido.backends.rtmidi")

print(f"MIDO version: {mido.version_info}")
print(f"Backend: {mido.backend}")

# The name of your MIDI output port
port_name = "MIDIOUT2 (Osmose) 2"

# List all available ports
available_ports = mido.get_output_names()
print("Available MIDI output ports:")
for i, port in enumerate(available_ports):
   print(f"  {i}: {port}")

try:
   # Open the MIDI output port
   with mido.open_output(port_name) as port:
      print(f"\nOpened port: {port_name}")
      print(f"Port type: {type(port)}")

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
         try:
            port.send(mido.Message("note_on", channel=0, note=note, velocity=velocity))
            print(f"Playing note {note} with velocity {velocity}")

            # Wait for the duration of the note
            time.sleep(duration)

            # Send a note off message
            port.send(mido.Message("note_off", channel=0, note=note, velocity=velocity))

         except Exception as note_error:
            print(f"Error playing note {note}: {note_error}")

      print("Finished playing notes")

except ValueError as e:
   print(f"Error: Could not open MIDI port '{port_name}'. Make sure the port exists and is available.")
   print(f"Available output ports: {mido.get_output_names()}")

except Exception as e:
   print(f"Unexpected error: {e}")
   print("Make sure your MIDI device is connected and not being used by another application.")

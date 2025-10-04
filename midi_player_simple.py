try:
   import rtmidi
   import time

   # Create a MIDI output object
   midiout = rtmidi.MidiOut()

   # Get available ports
   available_ports = midiout.get_ports()
   print("Available MIDI output ports:")
   for i, port in enumerate(available_ports):
      print(f"  {i}: {port}")

   # Check if our target port exists
   port_name = "MIDIOUT2 (Osmose) 2"
   port_index = None
   for i, port in enumerate(available_ports):
      if port == port_name:
         port_index = i
         break

   if port_index is not None:
      # Open the port
      midiout.open_port(port_index)
      print(f"\nOpened port: {port_name}")

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
         # Send a note on message [status, note, velocity]
         midiout.send_message([0x90, note, velocity])  # Note on, channel 0
         print(f"Playing note {note} with velocity {velocity}")

         # Wait for the duration of the note
         time.sleep(duration)

         # Send a note off message
         midiout.send_message([0x80, note, velocity])  # Note off, channel 0

      print("Finished playing notes")

      # Close the port
      midiout.close_port()
   else:
      print(f"Error: Could not find MIDI port '{port_name}'")

except ImportError as e:
   print("Error: rtmidi module not found. Please make sure python-rtmidi is installed in your virtual environment.")
   print(f"Import error: {e}")

except Exception as e:
   print(f"Unexpected error: {e}")
   print("Make sure your MIDI device is connected and not being used by another application.")

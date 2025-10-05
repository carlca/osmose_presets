try:
   import mido
   import time

   # Target the Osmose port directly
   port_name = "MIDIOUT2 (Osmose) 2"
   print(f"Targeting port: {port_name}")
   
   # Alternative approach: Open, close, then reopen for better initialization
   try:
      # First open to establish connection
      midi_port = mido.open_output(port_name)
      print(f"Initially opened port: {port_name}")
      midi_port.close()
      
      # Give it time to reset
      time.sleep(1)
      
      # Reopen (this is the working alternative approach)
      midi_port = mido.open_output(port_name)
      print(f"Reopened port with alternative approach: {port_name}")
      time.sleep(0.5)
      
   except Exception as e:
      print(f"Error opening {port_name}: {e}")
      raise
   
   # Define the sequence of MIDI notes to play
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

   print("Starting to play notes...")
   successful_notes = 0
   
   # Play each note in the sequence
   for i, (note, velocity, duration) in enumerate(notes):
      try:
         # Send note on
         note_on_msg = mido.Message('note_on', note=note, velocity=velocity, channel=0)
         midi_port.send(note_on_msg)
         print(f"Note {i+1}: Playing note {note} with velocity {velocity} ✓")
         successful_notes += 1
         
         # Wait for note duration
         time.sleep(duration)

         # Send note off
         note_off_msg = mido.Message('note_off', note=note, velocity=velocity, channel=0)
         midi_port.send(note_off_msg)
         
         # Small delay between notes
         time.sleep(0.1)
         
      except Exception as note_error:
         print(f"Error playing note {note}: {note_error}")
         continue

   print(f"\nFinished - {successful_notes}/{len(notes)} notes played successfully")

   # Close the port
   midi_port.close()
   print("MIDI port closed")

except ImportError as e:
   print("Error: mido module not found.")
   print(f"Import error: {e}")
   print("Install with: pip install mido python-rtmidi")

except Exception as e:
   print(f"Unexpected error: {e}")
   print("Make sure the Osmose is connected and not used by other apps.")
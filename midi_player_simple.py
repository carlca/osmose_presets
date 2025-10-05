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

   # First try to use Microsoft GS Wavetable Synth for testing
   test_port_name = "Microsoft GS Wavetable Synth 0"
   port_name = "MIDIOUT2 (Osmose) 2"
   
   # Try Osmose first, fall back to Microsoft GS for testing
   port_index = None
   for i, port in enumerate(available_ports):
      if port == port_name:
         port_index = i
         break
         
   # If Osmose not found, try Microsoft GS for testing
   if port_index is None:
      print(f"Osmose port '{port_name}' not found. Trying {test_port_name} for testing...")
      for i, port in enumerate(available_ports):
         if port == test_port_name:
            port_index = i
            port_name = test_port_name
            break

   if port_index is not None:
      # Test if we can actually send messages to this port
      print(f"\nTesting port: {port_name}")
      
      # Try to open port first
      try:
         midiout.open_port(port_index)
         print(f"Successfully opened port: {port_name}")
         time.sleep(0.1)  # Give port time to initialize
      except Exception as open_error:
         print(f"Error opening port: {open_error}")
         midiout.close_port()
         
         # Try fallback to Microsoft GS if Osmose fails
         if "Osmose" in port_name:
            print("Falling back to Microsoft GS Wavetable Synth for testing...")
            for i, port in enumerate(available_ports):
               if "Microsoft GS" in port:
                  port_index = i
                  port_name = port
                  break
            if port_index is not None:
               try:
                  midiout.open_port(port_index)
                  print(f"Successfully opened fallback port: {port_name}")
               except Exception as fallback_error:
                  print(f"Fallback also failed: {fallback_error}")
                  raise
            else:
               raise Exception("No working MIDI ports found")
      
      # Test basic MIDI message
      test_passed = False
      for test_attempt in range(3):
         try:
            # Send a simple program change (very safe command)
            midiout.send_message([0xC0, 1])  # Program change, channel 0, program 1
            time.sleep(0.1)
            print("MIDI communication test PASSED")
            test_passed = True
            break
         except Exception as test_error:
            print(f"MIDI test attempt {test_attempt + 1} failed: {test_error}")
            time.sleep(0.5)
      
      if not test_passed:
         print("MIDI communication test FAILED - trying alternative approach...")
         # Try to close and reopen with different parameters
         try:
            midiout.close_port()
            time.sleep(1)
            midiout.open_port(port_index)
            time.sleep(0.5)
            print("Port reopened successfully")
         except Exception as reopen_error:
            print(f"Port reopen failed: {reopen_error}")
            # If all else fails, try Microsoft GS
            if "Osmose" in port_name:
               print("Switching to Microsoft GS Wavetable Synth...")
               for i, port in enumerate(available_ports):
                  if "Microsoft GS" in port:
                     port_index = i
                     port_name = port
                     break
               midiout.close_port()
               midiout.open_port(port_index)
               print(f"Using port: {port_name}")
      
      # Define a sequence of MIDI notes to play (note number, velocity, duration)
      notes = [
         (60, 64, 0.5),  # C4 - back to moderate velocity
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
            # Send a note on message [status, note, velocity]
            note_on = [0x90, note, velocity]  # Note on, channel 0
            midiout.send_message(note_on)
            print(f"Note {i+1}: Playing note {note} with velocity {velocity} ✓")
            successful_notes += 1
            
            # Wait for the duration of the note
            time.sleep(duration)

            # Send a note off message
            note_off = [0x80, note, velocity]  # Note off, channel 0
            midiout.send_message(note_off)
            
            # Delay between notes
            time.sleep(0.1)
            
         except Exception as note_error:
            print(f"Error playing note {note}: {note_error}")
            # Try to continue with next note
            continue

      print(f"\nFinished playing notes - {successful_notes}/{len(notes)} notes played successfully")

      # Close the port
      midiout.close_port()
      print("MIDI port closed")
   else:
      print(f"Error: Could not find MIDI port '{port_name}'")

except ImportError as e:
   print("Error: rtmidi module not found. Please make sure python-rtmidi is installed in your virtual environment.")
   print(f"Import error: {e}")
   print("Install with: pip install python-rtmidi")

except Exception as e:
   print(f"Unexpected error: {e}")
   print("Make sure your MIDI device is connected and not being used by another application.")
   print("\nTroubleshooting tips:")
   print("1. Make sure the Osmose is powered on and connected via USB")
   print("2. Close any other applications that might be using MIDI (DAWs, other MIDI software)")
   print("3. Try unplugging and reconnecting the Osmose")
   print("4. Try using the 'Microsoft GS Wavetable Synth' port to test if the script works")
   print("5. Check Windows Device Manager to ensure the Osmose MIDI drivers are properly installed")

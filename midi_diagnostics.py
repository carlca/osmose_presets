import mido

print("=== MIDI Diagnostics ===")
print(f"MIDO version: {mido.version_info}")
print(f"Default backend: {mido.backend}")

# List all available ports
print("\nAvailable MIDI Output Ports:")
output_ports = mido.get_output_names()
for i, port in enumerate(output_ports):
   print(f"  {i}: {port}")

print("\nAvailable MIDI Input Ports:")
input_ports = mido.get_input_names()
for i, port in enumerate(input_ports):
   print(f"  {i}: {port}")

# Check if the specific port exists
target_port = "MIDIOUT2 (Osmose) 2"
if target_port in output_ports:
   print(f"\n✓ Target port '{target_port}' found")

   # Try to open and send a simple message
   try:
      with mido.open_output(target_port) as outport:
         print(f"✓ Successfully opened port '{target_port}'")

         # Try sending a simple note on/off sequence
         msg = mido.Message("note_on", note=60, velocity=64, channel=0)
         outport.send(msg)
         print("✓ Successfully sent note_on message")

         msg = mido.Message("note_off", note=60, velocity=64, channel=0)
         outport.send(msg)
         print("✓ Successfully sent note_off message")

   except Exception as e:
      print(f"\n✗ Error opening or using port: {e}")
else:
   print(f"\n✗ Target port '{target_port}' NOT found")

import mido

print("Available MIDI output ports:")
for port in mido.get_output_names():
   print(f"  - {port}")

print("\nAvailable MIDI input ports:")
for port in mido.get_input_names():
   print(f"  - {port}")

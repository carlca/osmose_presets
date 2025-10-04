import mido

# Test with the exact port name from the error
port_name = "MIDIOUT2 (Osmose) 2"
print("Available input ports:", mido.get_output_names())

if port_name in mido.get_output_names():
   try:
      with mido.open_output(port_name) as inport:
         print(f"Successfully opened {port_name} as output")
   except Exception as e:
      print(f"Error opening {port_name} as output: {e}")
else:
   print(f"Port {port_name} not found in output ports list")

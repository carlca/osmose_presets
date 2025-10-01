import mido

# Test with the exact port name from the error
port_name = "MIDIIN2 (Osmose) 1"
print("Available input ports:", mido.get_input_names())

if port_name in mido.get_input_names():
   try:
      with mido.open_input(port_name) as inport:
         print(f"Successfully opened {port_name} as input")
   except Exception as e:
      print(f"Error opening {port_name} as input: {e}")
else:
   print(f"Port {port_name} not found in input ports list")

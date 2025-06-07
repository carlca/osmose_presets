leaves = 19
daily_weather = ["⛈️","☀️","☀️"]
if day == "⛈️":
  water = 3
for day in daily_weather:
  light = 1
  water = 1
  if day == "☀️":
    light = 2
  leaves += water + light
  print("Leaves:", leaves)

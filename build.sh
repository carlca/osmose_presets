#!/bin/zsh

rm -rf build dist

uv run pyinstaller \
  --name OsmosePresets \
  --onefile \
  --hidden-import=mido.backends.rtmidi \
  --collect-all=rtmidi \
  --add-data "src/osmose_presets/OsmosePresets.json:osmose_presets" \
  --add-data "src/osmose_presets/osmose_presets.tcss:." \
  src/osmose_presets/app.py

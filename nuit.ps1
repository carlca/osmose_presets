python -m nuitka --onefile --windows-console-mode=force --follow-imports --include-package=textual --include-package=mido --include-package=rtmidi `
--include-data-files=src/osmose_presets/osmose_presets.tcss=osmose_presets.tcss `
--include-data-files=src/osmose_presets/OsmosePresets.json=OsmosePresets.json `
--output-dir=dist src/osmose_presets/app.py
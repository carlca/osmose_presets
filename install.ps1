python -m venv .venv
.\.venv\scripts\Activate.ps1
python.exe -m pip install --upgrade pip
pip install textual
pip install textual-dev
pip install "textual[syntax]"
pip install python-rtmidi
pip install mido
pip install -e .

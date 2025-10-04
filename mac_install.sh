python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install textual
pip install textual-dev
pip install "textual[syntax]"
pip install python-rtmidi
pip install mido
pip install -e .
pip install build
pip install twine

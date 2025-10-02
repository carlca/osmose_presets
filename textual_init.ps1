# if a venv is active, deativate it
if ($env:VIRTUAL_ENV) {
   .\.venv\Scripts\deactivate.bat
}

# if a venv folder is preset, the delete it
if (Test-Path .venv) {
   rm -r ./.venv
}

#
python -m venv .venv

if (-not $env:VIRTUAL_ENV) {
   .\.venv\Scripts\Activate.ps1
}

pip install textual
pip install textual-dev
pip install "textual[syntax]"
pip install python-rtmidi
pip install mido

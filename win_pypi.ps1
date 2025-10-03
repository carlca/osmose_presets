if (Test-Path "./dist") {
    rm -r -Force ./dist/*.*
}
python -m build -C pyproject-win.toml
twine upload dist/*

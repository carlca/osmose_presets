@echo off
REM Workaround for missing vcvarsx86_arm64.bat
REM Use the arm64_amd64 variant as a substitute

call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsarm64_amd64.bat"
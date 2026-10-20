@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. See requirements.txt for dependencies.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 -m code.scripts.clean_detection_app %*
if errorlevel 1 pause

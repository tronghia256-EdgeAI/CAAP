@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. See README.md.
  if "%~1"=="" pause
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 tools\caap.py %*
set "CAAP_EXIT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %CAAP_EXIT%

@echo off
cd /d "%~dp0..\.."
".venv\Scripts\python.exe" -X utf8 -m code.scripts.gt_roi_app %*
if errorlevel 1 pause

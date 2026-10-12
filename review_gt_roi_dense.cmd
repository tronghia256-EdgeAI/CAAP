@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -X utf8 -m code.scripts.gt_mixed_app --roi-segment dense
if errorlevel 1 pause

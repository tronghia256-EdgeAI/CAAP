@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -X utf8 -m code.scripts.paper_gt_audit_app
if errorlevel 1 pause

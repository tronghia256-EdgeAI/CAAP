@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -X utf8 -m code.scripts.gt_audit_reconcile_app
if errorlevel 1 pause

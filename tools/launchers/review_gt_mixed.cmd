@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. See docs\GT_REVIEW_WORKFLOW.md for setup.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 -m code.scripts.gt_mixed_app %*
if errorlevel 1 pause

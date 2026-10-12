@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv Python. See docs\PAPER_EXPERIMENT_WORKFLOW.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -X utf8 -u -m code.scripts.run_roi_paper --phase all %*
set "CAAP_RUN_EXIT=%ERRORLEVEL%"
if not "%CAAP_RUN_EXIT%"=="0" echo Experiment stopped. Existing cache checkpoints are preserved.
pause
exit /b %CAAP_RUN_EXIT%

@echo off
cd /d "%~dp0..\.."
".venv\Scripts\python.exe" -X utf8 -m code.scripts.train_detection_trial --prepare --train --profile smoke --device cpu
pause

@echo off
cd /d "%~dp0"
python "%~dp0run_app.py"
if errorlevel 1 pause

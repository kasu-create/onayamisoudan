@echo off
cd /d "%~dp0revenue"
echo Starting revenue server on http://127.0.0.1:5000/
echo Optional: create tools\revenue\.env from env.local.example see stripe_setup.txt
py -m pip install python-dotenv -q 2>nul
py server.py
pause

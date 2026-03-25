@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [%date% %time%] 自動予約: キューに1件追加を試行します。
python auto_schedule.py
if errorlevel 1 (
  echo auto_schedule でエラーまたは追加対象なし。
)

python run_upload.py
if errorlevel 1 (
  echo run_upload でエラーが発生しました。
)

echo [%date% %time%] 完了しました。
pause

@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\uvicorn.exe" (
  echo Create the venv first:
  echo   python -m venv .venv
  echo   .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
REM Port 8000 is often blocked on Windows (Hyper-V, reserved range); 8765 is a safe default.
echo Starting server at http://127.0.0.1:8765
echo If the page fails, open http://127.0.0.1:8765/api/debug-paths
echo Press Ctrl+C to stop.
.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8765 --reload

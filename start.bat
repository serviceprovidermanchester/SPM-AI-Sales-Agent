@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL%==0 (set "PYTHON=py -3") else (set "PYTHON=python")
if not exist ".venv\Scripts\python.exe" (
  %PYTHON% -m venv .venv || goto :fail
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
if not exist ".env" (
  ".venv\Scripts\python.exe" scripts\bootstrap.py || goto :fail
)
echo.
echo Open http://127.0.0.1:8000 in your browser
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
goto :eof
:fail
echo Setup failed. Ensure Python 3.11+ and internet access for initial installation.
pause

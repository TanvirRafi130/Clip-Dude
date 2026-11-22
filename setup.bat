rem Copyright (c) 2026 Tanvir.
@echo off
cd /d "%~dp0"
where ffmpeg >nul 2>&1 || echo WARNING: ffmpeg not found. Install it: winget install Gyan.FFmpeg

rem This dependency set currently targets Python 3.12 wheel availability.
py -3.12 -c "import sys; print(sys.version)" >nul 2>&1 || (echo Python 3.12 is required. Install Python 3.12, then run py -0. & pause & exit /b 1)

if exist .venv (
  ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
  if errorlevel 1 (
    echo Existing .venv is not Python 3.12. Recreating it...
    rmdir /s /q .venv
  )
)
if not exist .venv (
  echo Creating Python 3.12 environment...
  py -3.12 -m venv .venv || (echo Could not create Python 3.12 environment. & pause & exit /b 1)
)
echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip || (pause & exit /b 1)
".venv\Scripts\python.exe" -m pip install -r requirements.txt || (pause & exit /b 1)
if not exist .profile copy .profile.example .profile >nul
echo.
echo Done. If you have not downloaded the AI model: ollama pull qwen3.5:4b
echo Then double-click run.bat
pause

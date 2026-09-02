@echo off
cd /d "%~dp0"
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    python -m venv ..\venv
    call "..\venv\Scripts\activate.bat"
)
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

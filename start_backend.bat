@echo off
title AgroTech Backend Server (FastAPI)
echo Starting AgroTech Backend on http://127.0.0.1:8000 ...
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
pause

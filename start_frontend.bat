@echo off
title AgroTech Frontend Server (HTTP Server)
echo Starting AgroTech Frontend on http://127.0.0.1:5500 ...
python -m http.server 5500
pause

@echo off
echo ========================================
echo Willis Facemap 24/7 Server
echo ========================================
echo.
echo Starting Willis server...
start "Willis Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python run.py"
timeout /t 5 /nobreak > nul
echo.
echo Starting Cloudflare Tunnel...
start "Cloudflare Tunnel" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --url http://localhost:5001"
echo.
echo ========================================
echo Both servers started!
echo Check the new windows for URLs
echo ========================================
pause

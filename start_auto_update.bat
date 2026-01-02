@echo off
title Willis Facemap - Auto Update Mode
color 0A

echo ========================================
echo Willis Facemap - 자동 업데이트 모드
echo ========================================
echo.
echo 이 모드는 다음을 수행합니다:
echo 1. Willis 서버 시작
echo 2. Cloudflare Tunnel 시작
echo 3. GitHub 변경사항 자동 감지 (30초마다)
echo 4. 업데이트 발견 시 알림
echo.
echo 개발 컴퓨터에서 코드 수정 후:
echo   git add . && git commit -m "메시지" && git push
echo.
echo 그러면 이 서버에서 자동으로 감지합니다!
echo ========================================
echo.

REM Willis 서버 시작
echo [1/3] Willis 서버 시작...
start "Willis Server" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python run.py"
timeout /t 5 /nobreak > nul

REM Cloudflare Tunnel 시작
echo [2/3] Cloudflare Tunnel 시작...
start "Cloudflare Tunnel" cmd /k "cd /d %~dp0 && cloudflared.exe tunnel --url http://localhost:5001"
timeout /t 3 /nobreak > nul

REM 자동 업데이트 감시 시작
echo [3/3] 자동 업데이트 감시 시작...
echo.
echo ========================================
echo 모든 서비스가 시작되었습니다!
echo ========================================
echo.
cd /d %~dp0
.venv\Scripts\activate && python auto_update.py

pause

@echo off
title Willis Facemap Server
color 0A

echo ========================================
echo Willis Facemap - 통합 서버
echo ========================================
echo.
echo 기능:
echo   - Next.js 서버 자동 시작
echo   - Cloudflare Tunnel 자동 시작
echo   - GitHub 변경사항 자동 감지 (30초마다)
echo   - 업데이트 시 자동 빌드 + 재시작
echo.
echo ========================================
echo.

cd /d %~dp0
python server.py

pause

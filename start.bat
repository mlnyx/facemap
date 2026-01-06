@echo off
title Willis Facemap Server
echo.
echo ========================================
echo   Willis Facemap Server
echo ========================================
echo.

REM Named Tunnel 사용시 아래 주석 해제
REM set USE_NAMED_TUNNEL=true

python scripts\server.py
pause

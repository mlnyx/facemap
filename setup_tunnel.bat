@echo off
title Cloudflare Tunnel Setup
color 0B

echo ========================================
echo Cloudflare Named Tunnel 설정
echo ========================================
echo.
echo 이 스크립트는 고정 URL을 위한 Named Tunnel을 생성합니다.
echo (한 번만 실행하면 됩니다)
echo.
echo ========================================
echo.

echo [1/3] Cloudflare 로그인...
echo       브라우저에서 로그인하세요.
cloudflared tunnel login

echo.
echo [2/3] 터널 생성...
cloudflared tunnel create facemap

echo.
echo [3/3] 설정 파일 생성...

REM 홈 디렉토리의 .cloudflared 폴더 찾기
set CLOUDFLARED_DIR=%USERPROFILE%\.cloudflared

REM config.yml 생성
echo tunnel: facemap > "%CLOUDFLARED_DIR%\config.yml"
echo credentials-file: %CLOUDFLARED_DIR%\facemap.json >> "%CLOUDFLARED_DIR%\config.yml"
echo. >> "%CLOUDFLARED_DIR%\config.yml"
echo ingress: >> "%CLOUDFLARED_DIR%\config.yml"
echo   - service: http://localhost:3000 >> "%CLOUDFLARED_DIR%\config.yml"

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 이제 start_server.bat를 실행하면 고정 URL로 접속 가능합니다.
echo.
echo 터널 URL 확인:
cloudflared tunnel info facemap
echo.
echo ========================================

pause

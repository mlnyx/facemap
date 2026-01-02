# Willis Facemap - Auto Update Mode
# 자동 업데이트 및 서버 시작 스크립트

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Willis Facemap - 자동 업데이트 모드" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "이 모드는 다음을 수행합니다:" -ForegroundColor Yellow
Write-Host "  1. Willis 서버 시작"
Write-Host "  2. Cloudflare Tunnel 시작"
Write-Host "  3. GitHub 변경사항 자동 감지 (30초마다)"
Write-Host "  4. 업데이트 발견 시 알림`n"

Write-Host "개발 컴퓨터에서 코드 수정 후:" -ForegroundColor Yellow
Write-Host "  git add . && git commit -m '메시지' && git push`n"
Write-Host "그러면 이 서버에서 자동으로 감지합니다!`n" -ForegroundColor Green

Write-Host "========================================`n" -ForegroundColor Cyan

# Willis 서버 시작
Write-Host "[1/3] Willis 서버 시작..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; python run.py"
Start-Sleep -Seconds 5

# Cloudflare Tunnel 시작
Write-Host "[2/3] Cloudflare Tunnel 시작..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\cloudflared.exe tunnel --url http://localhost:5001"
Start-Sleep -Seconds 3

# 자동 업데이트 감시 시작
Write-Host "[3/3] 자동 업데이트 감시 시작...`n" -ForegroundColor Yellow

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ 모든 서비스가 시작되었습니다!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Python 자동 업데이트 스크립트 실행
.\.venv\Scripts\Activate.ps1
python auto_update.py

# Willis Facemap - 영구 실행 스크립트

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Willis Facemap 24/7 Server" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Willis 서버 시작
Write-Host "Starting Willis server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; python run.py"

# 5초 대기
Start-Sleep -Seconds 5

# Cloudflare Tunnel 시작
Write-Host "Starting Cloudflare Tunnel...`n" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\cloudflared.exe tunnel --url http://localhost:5001"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Both servers started!" -ForegroundColor Green
Write-Host "Check the new windows for Cloudflare URL" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

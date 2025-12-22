#!/bin/bash
# Willis 웹 서버 시작 스크립트

cd /Users/mlnyx/facemap

# 기존 프로세스 종료
echo "기존 프로세스 정리 중..."
pkill -f "python.*willis_web.py" 2>/dev/null
pkill -f "ngrok" 2>/dev/null
sleep 2

# 가상환경 활성화 및 Flask 서버 시작
echo "Flask 서버 시작 중..."
source .venv/bin/activate
nohup python willis_web.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo "Flask 서버 PID: $FLASK_PID"

# Flask 서버가 준비될 때까지 대기
sleep 3

# ngrok 시작
echo "ngrok 터널 시작 중..."
nohup ngrok http 5001 > logs/ngrok.log 2>&1 &
NGROK_PID=$!
echo "ngrok PID: $NGROK_PID"

sleep 3

# 상태 확인
echo ""
echo "======================================"
echo "✓ 서버 시작 완료!"
echo "======================================"
echo ""
echo "Flask 서버: http://localhost:5001"
echo "ngrok URL 확인: curl http://localhost:4040/api/tunnels | grep -o 'https://[^\"]*'"
echo ""
echo "서버 중지: pkill -f \"python.*willis_web.py\" && pkill -f ngrok"
echo "로그 확인: tail -f logs/flask.log"
echo "======================================"

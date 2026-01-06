
  cd C:\Users\user\workspace\facemap
  git pull
  start.bat

  동작 방식

  1. 처음 시작 → Quick Tunnel URL 받음 (예: https://xxx-yyy.trycloudflare.com)
  2. URL이 TUNNEL_URL.txt에 저장됨
  3. 메인컴에서 코드 수정 후 push → 서브컴이 자동 감지
  4. 서버만 재시작, 터널은 유지 → URL 그대로!
  5. 컴퓨터 재부팅하거나 Ctrl+C로 종료할 때만 URL 바뀜
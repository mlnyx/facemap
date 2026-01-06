 1. 프로젝트 업데이트

  cd C:\Users\user\workspace\facemap
  git pull

  2. Cloudflare Zero Trust Dashboard에서 설정

  1. https://one.dash.cloudflare.com 접속 (Cloudflare 로그인)
  2. Zero Trust > Networks > Tunnels 클릭
  3. Create a tunnel 클릭
  4. Tunnel name: facemap 입력 후 Save tunnel
  5. Connector 설치 화면에서:
    - OS: Windows 선택
    - 표시되는 명령어 복사 (대략 이런 형태):
  cloudflared.exe service install <YOUR_TOKEN>
    - 서브컴 터미널에서 실행
  6. Public hostname 설정:
    - Subdomain: facemap-willis (원하는 이름)
    - Domain: cfargotunnel.com 선택
    - Service Type: HTTP
    - URL: localhost:3000
    - Save

  3. 서버 실행

  # Named Tunnel 모드로 실행
  set USE_NAMED_TUNNEL=true
  start.bat

  또는 start.bat 파일에서 주석 해제:
  REM 이 줄의 주석을 해제
  set USE_NAMED_TUNNEL=true

  완료 후

  고정 URL로 접속 가능:
  https://facemap-willis.cfargotunnel.com

https://one.dash.cloudflare.com/8e162ebe1f70115af4959bf66b9b02f3/networks/connectors/cloudflare-tunnels/cfd_tunnel/32faad82-b167-4d7a-bde6-8463816c2abe/edit?tab=overview
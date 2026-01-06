# Cloudflare Tunnel로 24시간 배포하기

## 🎯 개요

24시간 켜놓을 수 있는 컴퓨터에서 Willis 앱을 실행하고, Cloudflare Tunnel로 외부 접속을 허용합니다.

**비용**: 완전 무료  
**속도**: Render.com보다 훨씬 빠름  
**URL**: 커스텀 도메인 또는 `*.trycloudflare.com`

---

## 📦 1단계: Cloudflare Tunnel 설치

### Windows

```powershell
# Chocolatey로 설치 (권장)
choco install cloudflared

# 또는 직접 다운로드
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
```

### macOS

```bash
brew install cloudflare/cloudflare/cloudflared
```

### Linux

```bash
# Debian/Ubuntu
sudo apt-get install cloudflared

# 또는 직접 다운로드
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

---

## 🚀 2단계: 빠른 시작 (임시 URL)

### 방법 1: 가장 간단 (추천)

```bash
# 1. Willis 서버 시작
python run.py

# 2. 새 터미널에서 Cloudflare Tunnel 시작
cloudflared tunnel --url http://localhost:5001
```

**결과**: `https://random-name.trycloudflare.com` 같은 URL이 즉시 생성됩니다!

이 URL을 친구들에게 공유하면 됩니다.

---

## 🔐 3단계: 영구 URL 설정 (선택사항)

임시 URL은 재시작할 때마다 바뀝니다. 고정 URL을 원하면:

### 3-1. Cloudflare 계정 생성

1. https://dash.cloudflare.com 회원가입 (무료)
2. 로그인

### 3-2. Cloudflared 인증

```bash
cloudflared tunnel login
```

브라우저가 열리면 승인합니다.

### 3-3. 터널 생성

```bash
# 터널 생성
cloudflared tunnel create willis-facemap

# 결과: UUID와 credentials.json 파일 생성됨
# 예: 1234abcd-5678-efgh-9012-ijklmnopqrst
```

### 3-4. 설정 파일 생성

`config.yml` 파일을 생성합니다:

```yaml
tunnel: 1234abcd-5678-efgh-9012-ijklmnopqrst  # 위에서 생성된 UUID
credentials-file: C:\Users\user\.cloudflared\1234abcd-5678-efgh-9012-ijklmnopqrst.json

ingress:
  - hostname: willis.example.com  # 커스텀 도메인 (또는 생략하면 Cloudflare 도메인)
    service: http://localhost:5001
  - service: http_status:404
```

### 3-5. DNS 레코드 추가

```bash
cloudflared tunnel route dns willis-facemap willis.example.com
```

### 3-6. 터널 시작

```bash
cloudflared tunnel run willis-facemap
```

---

## 🔄 4단계: 자동 시작 설정

### Windows (서비스로 등록)

```powershell
# 서비스 설치
cloudflared service install

# 서비스 시작
Start-Service cloudflared
```

### macOS/Linux (systemd)

`/etc/systemd/system/cloudflared.service`:

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/local/bin/cloudflared tunnel run willis-facemap
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## 📝 5단계: Willis 서버 자동 시작

### Windows (작업 스케줄러)

1. `작업 스케줄러` 실행
2. "기본 작업 만들기"
3. 트리거: "컴퓨터 시작 시"
4. 작업: `C:\Users\user\Desktop\facemap\.venv\Scripts\python.exe`
5. 인수: `C:\Users\user\Desktop\facemap\run.py`

### macOS/Linux (systemd)

`/etc/systemd/system/willis.service`:

```ini
[Unit]
Description=Willis Facemap Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/facemap
ExecStart=/path/to/.venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable willis
sudo systemctl start willis
```

---

## 🎉 완료!

이제 컴퓨터를 켜두기만 하면 24시간 접속 가능합니다!

### URL 확인

```bash
# 임시 URL 사용 시
cloudflared tunnel --url http://localhost:5001
# 출력: https://random-name.trycloudflare.com

# 영구 터널 사용 시
https://willis.example.com
```

---

## 💡 팁

### 1. 컴퓨터 절전 모드 비활성화

**Windows:**
- 설정 > 시스템 > 전원 및 절전
- "절전 모드" → "안 함"

**macOS:**
```bash
sudo pmset -a sleep 0
sudo pmset -a disablesleep 1
```

**Linux:**
```bash
sudo systemctl mask sleep.target suspend.target
```

### 2. 로그 확인

```bash
# Cloudflare Tunnel 로그
cloudflared tunnel info willis-facemap

# Willis 서버 로그
# run.py 실행한 터미널에서 확인
```

### 3. 속도 최적화

로컬 서버이므로 Render.com보다 훨씬 빠릅니다:
- Render: Cold start 30초~2분
- 로컬 + Cloudflare: 즉시 응답

---

## 🆚 비교: Render vs Cloudflare Tunnel

| 항목 | Render.com | Cloudflare Tunnel |
|------|------------|-------------------|
| 가격 | 무료 (제한적) | 완전 무료 |
| 속도 | 느림 (cold start) | 빠름 (로컬) |
| 배포 시간 | 5-30분 | 즉시 |
| 안정성 | 중간 (무료 티어 제한) | 높음 |
| URL | 고정 | 선택 가능 |
| 단점 | 느림, cold start | 컴퓨터 계속 켜야 함 |

---

## 🔒 보안

Cloudflare Tunnel은 안전합니다:
- ✅ HTTPS 자동 적용
- ✅ DDoS 보호
- ✅ 방화벽 뚫을 필요 없음 (포트 포워딩 불필요)
- ✅ 실제 IP 주소 숨김

---

## 🆘 문제 해결

### "cloudflared: command not found"
```bash
# 설치 확인
cloudflared --version

# 재설치
choco install cloudflared  # Windows
brew install cloudflared    # macOS
```

### 터널이 연결되지 않음
```bash
# 로그 확인
cloudflared tunnel --loglevel debug --url http://localhost:5001
```

### Willis 서버가 응답하지 않음
```bash
# 서버 실행 확인
curl http://localhost:5001

# 재시작
# Ctrl+C로 종료 후 다시 python run.py
```

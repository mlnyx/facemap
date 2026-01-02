# Willis Facemap 24시간 서버 설정 가이드

**24시간 컴퓨터에서 5분 안에 설정 완료!**

---

## 🚀 빠른 시작 (5분)

### 1단계: GitHub에서 클론

```powershell
# 원하는 위치로 이동
cd C:\Server

# GitHub에서 클론
git clone https://github.com/mlnyx/facemap.git
cd facemap
```

### 2단계: Python 가상환경 설정

```powershell
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
.\.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

**잠깐!** MediaPipe 모델이 자동으로 다운로드됩니다 (약 1분 소요).

### 3단계: Cloudflared 설치

```powershell
# 직접 다운로드
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
```

### 4단계: 서버 시작!

```powershell
# 방법 1: 배치 파일 실행 (가장 쉬움)
.\start_tunnel.bat

# 방법 2: PowerShell 스크립트
.\start_tunnel.ps1

# 방법 3: 수동 실행
# 터미널 1
python run.py

# 터미널 2 (새 PowerShell 창)
.\cloudflared.exe tunnel --url http://localhost:5001
```

### 5단계: URL 확인

Cloudflare Tunnel 창에서 생성된 URL 확인:

```
https://random-name.trycloudflare.com
```

이 URL을 복사해서 친구들에게 공유!

---

## 🔄 업데이트 방법

코드가 업데이트되면:

```powershell
# 서버 중지 (Ctrl+C 두 번)

# 최신 코드 받기
git pull origin main

# 서버 재시작
.\start_tunnel.bat
```

---

## ⚙️ Windows 시작 시 자동 실행

### 방법 1: 시작 프로그램 등록 (간단)

1. `Win + R` → `shell:startup` 입력
2. `start_tunnel.bat`의 바로가기를 만들어 이 폴더에 복사
3. 완료! 재부팅하면 자동 시작

### 방법 2: 작업 스케줄러 (고급)

1. `작업 스케줄러` 실행
2. "기본 작업 만들기" 클릭
3. **트리거**: "컴퓨터 시작 시"
4. **작업**: "프로그램 시작"
5. **프로그램**: `C:\Server\facemap\start_tunnel.bat`
6. 완료!

---

## 🔐 고정 URL 설정 (선택사항)

매번 재시작할 때마다 URL이 바뀌는 게 싫다면:

### Cloudflare 계정 생성

1. https://dash.cloudflare.com 회원가입 (무료)
2. 터미널에서:

```powershell
# 1. 로그인
.\cloudflared.exe tunnel login

# 2. 터널 생성 (한 번만)
.\cloudflared.exe tunnel create willis-facemap

# 3. DNS 연결 (한 번만)
.\cloudflared.exe tunnel route dns willis-facemap willis.yourdomain.com

# 4. 영구 실행
.\cloudflared.exe tunnel run willis-facemap
```

**결과**: `https://willis.yourdomain.com` 같은 고정 URL!

---

## 💡 전원 설정 (중요!)

24시간 실행을 위해:

### 절전 모드 비활성화

1. `설정` → `시스템` → `전원 및 절전`
2. **화면**: "안 함"
3. **절전**: "안 함"

### 자동 업데이트 시간 변경

1. `설정` → `Windows Update` → `활성 시간`
2. 사용하지 않는 시간대로 설정

---

## 📊 상태 확인

### Willis 서버 확인

```powershell
# 로컬에서 테스트
curl http://localhost:5001

# 응답: HTML 페이지
```

### Cloudflare Tunnel 확인

```powershell
# 생성된 URL로 접속
# 브라우저에서 열리면 성공!
```

### 서버 재시작

```powershell
# 모든 창에서 Ctrl+C

# 다시 시작
.\start_tunnel.bat
```

---

## 🛠️ 문제 해결

### "python: command not found"

Python이 설치되지 않았습니다:

1. https://www.python.org/downloads/ 에서 다운로드
2. **"Add Python to PATH"** 체크 필수!
3. 설치 후 PowerShell 재시작

### "ModuleNotFoundError"

의존성이 설치되지 않았습니다:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Cloudflare Tunnel이 연결 안 됨

1. 방화벽 확인
2. 인터넷 연결 확인
3. 재시도:

```powershell
.\cloudflared.exe tunnel --url http://localhost:5001
```

### URL이 응답하지 않음

1. Willis 서버가 실행 중인지 확인:
   ```powershell
   curl http://localhost:5001
   ```

2. 안 되면 재시작:
   ```powershell
   # Ctrl+C로 모두 종료
   .\start_tunnel.bat
   ```

---

## 📈 성능 최적화

### SSD 사용

프로젝트 폴더를 SSD에 두면 더 빠릅니다.

### 방화벽 예외 추가

`Windows Defender 방화벽` → `고급 설정` → `인바운드 규칙`
- `python.exe` 허용
- `cloudflared.exe` 허용

### 백그라운드 프로그램 최소화

불필요한 프로그램 종료로 리소스 확보

---

## 🔄 백업 및 복원

### 백업

```powershell
# GitHub에 커밋 (설정 변경 시)
git add .
git commit -m "서버 설정 변경"
git push origin main
```

### 복원

```powershell
# 다른 컴퓨터에서
git clone https://github.com/mlnyx/facemap.git
cd facemap
# 위의 설정 과정 반복
```

---

## 📝 디렉토리 구조

```
C:\Server\facemap\
├── .venv\                  # Python 가상환경
├── app\                    # 애플리케이션 코드
├── config\                 # 설정 파일
├── templates\              # HTML 템플릿
├── cloudflared.exe         # Cloudflare Tunnel
├── start_tunnel.bat        # 시작 스크립트
├── start_tunnel.ps1        # PowerShell 스크립트
├── run.py                  # 서버 진입점
└── requirements.txt        # Python 의존성
```

---

## 🆚 비교: 다른 방법들

| 방법 | 장점 | 단점 |
|------|------|------|
| **Cloudflare Tunnel** | 무료, 빠름, 쉬움 | 컴퓨터 켜둬야 함 |
| Render.com | 관리 불필요 | 느림 (cold start 30초) |
| AWS/GCP | 안정적 | 복잡, 비용 |
| 포트 포워딩 | 직접 제어 | 보안 위험, 공인 IP 필요 |

**결론**: 24시간 컴퓨터가 있다면 Cloudflare Tunnel이 최고!

---

## 🎯 체크리스트

설정 완료했는지 확인:

- [ ] Git 클론 완료
- [ ] Python 가상환경 생성 및 의존성 설치
- [ ] cloudflared.exe 다운로드
- [ ] `start_tunnel.bat` 실행 성공
- [ ] Cloudflare URL 확인
- [ ] 브라우저에서 접속 테스트
- [ ] 절전 모드 비활성화
- [ ] (선택) 시작 프로그램 등록

---

## 💬 추가 도움말

### 서버 로그 확인

Willis 서버 창에서 실시간 로그 확인:
```
127.0.0.1 - - [02/Jan/2026 11:31:44] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [02/Jan/2026 11:32:15] "POST /analyze HTTP/1.1" 200 -
```

### 네트워크 모니터링

Windows 작업 관리자 → 성능 → 이더넷에서 트래픽 확인

### 원격 접속

서버 컴퓨터에 원격 데스크톱 설정:
1. `설정` → `시스템` → `원격 데스크톱`
2. 활성화
3. 다른 컴퓨터에서 원격 연결

---

## 🚨 중요 주의사항

1. **보안**: 개인정보가 포함된 이미지는 업로드하지 마세요
2. **트래픽**: 무료 Cloudflare Tunnel은 트래픽 제한이 없지만 남용 금지
3. **업타임**: 컴퓨터가 꺼지면 서비스 중단됩니다
4. **백업**: 중요한 설정은 GitHub에 커밋하세요

---

## ✅ 완료!

이제 24시간 접속 가능한 Willis 앱이 실행 중입니다! 🎉

**URL 공유하기**: Cloudflare Tunnel 창에 표시된 URL을 복사해서 친구들에게 전송!

**문제 발생 시**: GitHub Issues에 문의 또는 README.md 참고

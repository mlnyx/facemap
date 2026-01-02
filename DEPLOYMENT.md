# Willis 안면 계측법 - 배포 가이드

이 문서는 Willis 안면 계측법 웹 애플리케이션을 다양한 플랫폼에 배포하는 방법을 안내합니다.

## 📋 목차

1. [Docker로 배포](#1-docker로-배포)
2. [Render.com에 배포](#2-rendercom에-배포)
3. [Heroku에 배포](#3-heroku에-배포)
4. [AWS EC2에 배포](#4-aws-ec2에-배포)
5. [Google Cloud Run에 배포](#5-google-cloud-run에-배포)

---

## 1. Docker로 배포

Docker를 사용하면 어떤 환경에서도 동일하게 실행할 수 있습니다.

### 1-1. Docker 설치

- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: `sudo apt install docker.io docker-compose`

### 1-2. Docker 빌드 및 실행

```bash
# 이미지 빌드
docker build -t willis-facemap .

# 컨테이너 실행
docker run -p 5001:5001 willis-facemap

# 또는 Docker Compose 사용
docker-compose up -d
```

### 1-3. 접속

브라우저에서 `http://localhost:5001` 접속

---

## 2. Render.com에 배포

Render는 무료로 웹 애플리케이션을 배포할 수 있는 플랫폼입니다.

### 2-1. 준비 사항

1. [Render 계정 생성](https://render.com)
2. GitHub/GitLab 저장소에 프로젝트 업로드

### 2-2. Render 배포 설정

1. Render 대시보드에서 "New +" → "Web Service" 클릭
2. GitHub 저장소 연결
3. 다음 설정 입력:
   - **Name**: `willis-facemap`
   - **Environment**: `Docker`
   - **Region**: `Singapore` (한국과 가까운 지역)
   - **Branch**: `main`
   - **Instance Type**: `Free` (또는 필요에 따라 유료 플랜)

4. 환경 변수 설정 (선택사항):
   ```
   FLASK_ENV=production
   ```

5. "Create Web Service" 클릭

### 2-3. 배포 완료

- 자동으로 Docker 이미지가 빌드되고 배포됩니다
- URL: `https://your-service-name.onrender.com`

### ⚠️ Render 무료 플랜 제약사항

- 15분 동안 요청이 없으면 자동으로 Sleep 모드 진입
- 첫 요청 시 30-60초 정도 재시작 시간 필요
- 750시간/월 무료 사용 (약 31일)

---

## 3. Heroku에 배포

### 3-1. 준비 사항

1. [Heroku 계정 생성](https://heroku.com)
2. [Heroku CLI 설치](https://devcenter.heroku.com/articles/heroku-cli)

### 3-2. Heroku 배포

```bash
# Heroku 로그인
heroku login

# 앱 생성
heroku create willis-facemap-app

# Git 저장소 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit"

# Heroku에 푸시
git push heroku main

# 앱 열기
heroku open
```

### 3-3. 환경 변수 설정

```bash
heroku config:set FLASK_ENV=production
heroku config:set PORT=5001
```

---

## 4. AWS EC2에 배포

### 4-1. EC2 인스턴스 생성

1. AWS 콘솔에서 EC2 인스턴스 생성
2. Ubuntu 22.04 LTS 선택
3. 보안 그룹에서 포트 5001 허용

### 4-2. 서버 설정

```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 업데이트 및 필수 패키지 설치
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

# 프로젝트 클론
git clone https://github.com/your-username/willis-facemap.git
cd willis-facemap

# 가상 환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# Gunicorn으로 실행
gunicorn wsgi:app --bind 0.0.0.0:5001 --workers 2 --timeout 120
```

### 4-3. Systemd 서비스 등록 (백그라운드 실행)

```bash
sudo nano /etc/systemd/system/willis.service
```

```ini
[Unit]
Description=Willis Facemap Web Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/willis-facemap
Environment="PATH=/home/ubuntu/willis-facemap/venv/bin"
ExecStart=/home/ubuntu/willis-facemap/venv/bin/gunicorn wsgi:app --bind 0.0.0.0:5001 --workers 2 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl start willis
sudo systemctl enable willis
sudo systemctl status willis
```

---

## 5. Google Cloud Run에 배포

Google Cloud Run은 컨테이너 기반 서버리스 플랫폼입니다.

### 5-1. 준비 사항

1. [Google Cloud 계정 생성](https://cloud.google.com)
2. [gcloud CLI 설치](https://cloud.google.com/sdk/docs/install)

### 5-2. 배포 명령

```bash
# gcloud 인증
gcloud auth login

# 프로젝트 설정
gcloud config set project your-project-id

# Cloud Run에 배포
gcloud run deploy willis-facemap \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 5001 \
  --memory 2Gi \
  --timeout 300
```

---

## 🔧 배포 전 체크리스트

- [ ] `requirements.txt` 업데이트
- [ ] `.env` 파일 보안 확인 (GitHub에 업로드 금지)
- [ ] `face_landmarker.task` 모델 파일 포함 또는 자동 다운로드 설정
- [ ] CORS 설정 확인 (필요 시)
- [ ] HTTPS 설정 (프로덕션 환경)
- [ ] 로깅 및 모니터링 설정
- [ ] 에러 핸들링 확인

---

## 🆘 문제 해결

### 메모리 부족 오류

- Docker: `--memory 2g` 옵션 추가
- Cloud: 인스턴스 메모리 증가 (최소 2GB 권장)

### MediaPipe 모델 다운로드 실패

```python
# willis_web.py에서 자동 다운로드 확인
# 또는 수동으로 다운로드:
wget https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

### 카메라 접근 권한 오류

- HTTPS 필수 (localhost 제외)
- 브라우저 카메라 권한 허용 확인

---

## 📞 추가 지원

문제가 발생하면 GitHub Issues에 보고해주세요.

**배포 성공을 기원합니다! 🚀**

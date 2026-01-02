# 🚀 빠른 배포 가이드 - 5분 만에 링크 공유하기

## 목표: 웹앱을 인터넷에 올려서 누구나 접속할 수 있는 링크 만들기

---

## ⚡ 가장 빠른 방법: Render.com (무료)

### 1단계: GitHub에 코드 올리기 (3분)

```bash
# Git 초기화 (처음 한 번만)
git init
git add .
git commit -m "Willis 안면 계측법 웹앱"

# GitHub 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/willis-facemap.git
git branch -M main
git push -u origin main
```

**GitHub 저장소 만들기:**
1. [GitHub](https://github.com) 접속/가입
2. 우측 상단 `+` → `New repository` 클릭
3. 이름: `willis-facemap` (원하는 이름)
4. Public 선택
5. `Create repository` 클릭
6. 위 명령어에 YOUR_USERNAME을 본인 계정명으로 변경하여 실행

---

### 2단계: Render.com에 배포 (2분)

1. **[Render.com](https://render.com) 가입**
   - GitHub 계정으로 가입 (가장 쉬움)

2. **대시보드에서 배포**
   - `New +` 버튼 클릭
   - `Web Service` 선택
   - GitHub 저장소 연결 허용
   - `willis-facemap` 저장소 선택

3. **설정 입력**
   ```
   Name: willis-facemap (원하는 이름)
   Environment: Docker
   Region: Singapore (한국과 가까운 서버)
   Branch: main
   Instance Type: Free
   ```

4. **Create Web Service 클릭**

5. **배포 대기 (5-10분)**
   - 자동으로 빌드 시작
   - 로그에서 진행 상황 확인 가능

---

### 3단계: 링크 받기! 🎉

배포 완료 후 Render가 자동으로 URL 제공:
```
https://willis-facemap.onrender.com
```

✅ **이 링크를 누구에게나 공유하면 됩니다!**

---

## 📱 공유 방법

### 카카오톡/메시지로 공유
```
Willis 안면 계측법 웹앱입니다.
카메라로 얼굴을 촬영하거나 사진을 업로드하면 
실시간으로 분석 결과를 확인할 수 있습니다.

🔗 https://your-app.onrender.com
```

### QR 코드 생성
1. [QR 코드 생성기](https://www.qr-code-generator.com/) 접속
2. URL 입력
3. QR 코드 다운로드
4. 모바일로 쉽게 접속 가능!

---

## ⚠️ 무료 플랜 알아두기

- ✅ 완전 무료
- ⚠️ 15분 미사용 시 Sleep 모드 (첫 접속 시 30초 대기)
- ⚠️ 750시간/월 무료 (충분함)
- ✅ HTTPS 자동 적용
- ✅ 무제한 방문자

**Sleep 모드 해결법:**
- 유료 플랜 ($7/월) 사용하면 24시간 활성 상태 유지

---

## 🔄 코드 수정 후 재배포

```bash
# 코드 수정 후
git add .
git commit -m "업데이트 설명"
git push

# Render가 자동으로 재배포! (5분 소요)
```

---

## 🌐 다른 무료 배포 옵션

### Vercel (프론트엔드 특화)
- 장점: 가장 빠른 배포, Sleep 없음
- 단점: 서버리스 함수 10초 제한 (분석 시간 부족할 수 있음)

### Railway (쉬운 배포)
- 장점: 설정 간단
- 단점: 무료 플랜 $5 크레딧만 제공 (시간 제한)

### Fly.io (Docker 최적화)
- 장점: 성능 좋음, 3개 앱 무료
- 단점: 신용카드 등록 필요

---

## 📊 배포 상태 확인

### Render 대시보드에서:
- ✅ **Live**: 정상 작동 중
- 🔄 **Building**: 배포 중
- ❌ **Failed**: 에러 발생 (로그 확인)

### 접속 테스트:
```
https://your-app.onrender.com
```
브라우저에서 열어서 정상 작동 확인

---

## 🆘 문제 해결

### 배포 실패 시
1. Render 로그 확인
2. Python 버전 문제: `runtime.txt` 확인
3. 패키지 설치 실패: `requirements.txt` 확인

### 카메라 안 열림
- HTTPS 필수 (Render는 자동 제공)
- 브라우저 권한 허용 확인
- 모바일: 주소창에서 자물쇠 아이콘 → 카메라 허용

### 너무 느림
- 무료 플랜 특성상 첫 로딩 느릴 수 있음
- 이미지 분석은 정상 속도
- 유료 플랜 고려

---

## 💡 팁

1. **도메인 연결** (선택사항)
   - Render에서 커스텀 도메인 설정 가능
   - 예: `facemap.yourdomain.com`

2. **분석 통계**
   - Render 대시보드에서 방문자 수 확인 가능

3. **비용 절감**
   - 여러 사람이 동시에 사용해도 무료!
   - 트래픽 제한 없음

---

## ✅ 체크리스트

배포 전:
- [ ] GitHub 계정 생성
- [ ] 저장소에 코드 업로드
- [ ] Render 계정 가입

배포 후:
- [ ] URL 접속 확인
- [ ] 카메라/업로드 기능 테스트
- [ ] 모바일에서 테스트
- [ ] 링크 공유!

---

**준비됐나요? 지금 바로 시작하세요! 🚀**

궁금한 점이 있으면 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.

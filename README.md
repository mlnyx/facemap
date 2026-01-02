# Willis Facial Analysis System

**전문 의료급 얼굴 분석 웹 애플리케이션**

MediaPipe 기반 실시간 얼굴 랜드마크 감지 및 Willis 계측법을 통한 수직 고경 평가 시스템입니다.

 **배포 URL**: [https://willis-facemap.onrender.com](https://willis-facemap.onrender.com)


##  프로젝트 구조

```
facemap/
├── app/                          # 메인 애플리케이션
│   ├── __init__.py              # Flask 앱 팩토리
│   ├── core/                    # 핵심 분석 로직
│   │   ├── detector.py          # MediaPipe 얼굴 감지 (468개 랜드마크)
│   │   ├── landmarks.py         # 특징점 추출 (눈동자, 입, 코, 턱)
│   │   ├── analyzer.py          # Willis 계측 분석 엔진
│   │   └── visualizer.py        # 랜드마크 시각화
│   ├── routes/                  # Flask 라우트
│   │   └── main_routes.py       # API 엔드포인트 (/analyze, /analyze_frame)
│   └── utils/                   # 유틸리티
│       ├── geometry.py          # 기하학 계산 (거리, 각도)
│       └── image.py             # 이미지 처리 (인코딩, 디코딩)
├── config/                      # 설정
│   └── settings.py              # 애플리케이션 설정 (임계값, 상수)
├── templates/                   # HTML 템플릿
│   └── index.html               # Liquid Glass UI (macOS/Vision Pro 스타일)
├── static/                      # 정적 파일
│   ├── manifest.json            # PWA 매니페스트
│   └── sw.js                    # Service Worker
├── docs/                        # 문서
│   └── ARCHITECTURE.md          # 아키텍처 설명
├── run.py                       #  로컬 개발 서버 진입점
├── wsgi.py                      #  프로덕션 WSGI 진입점
├── requirements.txt             # Python 의존성
├── Dockerfile                   # Docker 이미지 설정
├── docker-compose.yml           # Docker Compose 설정
├── Procfile                     # Render.com 배포 설정
└── runtime.txt                  # Python 버전 (3.11.7)
```

### 주요 파일 설명

####  **애플리케이션 코어**
- `app/core/detector.py`: MediaPipe 초기화, 468개 얼굴 랜드마크 감지
- `app/core/landmarks.py`: 눈동자/입/코/턱 특징점 추출, 대칭도 계산
- `app/core/analyzer.py`: Willis 비율 계산, 정면/측면 분석
- `app/core/visualizer.py`: 랜드마크 + 측정선 시각화

####  **웹 레이어**
- `app/routes/main_routes.py`: API 엔드포인트
  - `POST /analyze`: 업로드된 이미지 분석
  - `POST /analyze_frame`: 실시간 카메라 프레임 분석
- `templates/index.html`: Liquid Glass 디자인 UI

####  **설정 및 유틸리티**
- `config/settings.py`: 모든 임계값 및 상수 중앙 관리
  - `WILLIS_RATIO_NORMAL_MIN/MAX`: Willis 정상 범위 (0.90~1.10)
  - `FRONTAL_SYMMETRY_THRESHOLD`: 정면/측면 판단 기준 (0.85)
  - `MIN_DETECTION_CONFIDENCE`: 얼굴 감지 신뢰도 (0.1)
- `app/utils/geometry.py`: 거리/각도 계산 함수
- `app/utils/image.py`: base64 인코딩/디코딩, 파일 읽기

####  **실행 파일**
- `run.py`: 로컬 개발 서버 (Flask 내장 서버)
- `wsgi.py`: 프로덕션 서버 (Gunicorn 사용)



##  주요 기능

### Willis 안면 계측법
-  **수직 고경 자동 평가**: 468개 랜드마크 기반 정밀 측정
-  **동공 중심 - 입 중심 거리** (파란선)
-  **코 base - 턱끝 거리** (빨간선)
-  **Willis 비율 자동 계산** (0.90~1.10 정상)
-  **실시간 분류**: 정상 / 평균 이하 / 평균 이상

### 정면/측면 자동 판단
-  **양쪽 눈 대칭도 분석** (85% 이상 → 정면)
-  **자동 모드 전환**: 정면 Willis 분석 ↔ 측면 프로필 분석
-  **측면 분석**: 턱 돌출도, 각도, 자연스러움 평가

### 현대적 UI/UX
-  **Liquid Glass Design**: macOS Sonoma / Vision Pro 스타일
-  **Glassmorphism**: backdrop-blur, 반투명 효과
-  **반응형**: 데스크톱 / 태블릿 / 모바일 최적화
-  **2가지 모드**: 사진 업로드 / 실시간 카메라
-  **실시간 피드백**: 측정선 + 수치 + 분류 결과



##  로컬 실행 방법

### 1. 사전 준비

```bash
# Python 3.11 이상 필요
python --version

# Git 클론
git clone https://github.com/mlnyx/facemap.git
cd facemap
```

### 2. 가상환경 생성 (권장)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

**주요 패키지:**
- Flask 3.0.0+: 웹 프레임워크
- MediaPipe 0.10.0+: 얼굴 랜드마크 감지 (468개 포인트)
- OpenCV (opencv-python-headless): 이미지 처리
- Gunicorn: 프로덕션 서버
- NumPy: 수치 계산

### 4. 서버 실행

```bash
# 개발 모드 (추천)
python run.py

# 또는 Flask 직접 실행
flask --app run run --host=0.0.0.0 --port=5001
```

서버 시작 후 브라우저에서 열기:
- 로컬: `http://localhost:5001`
- 네트워크: `http://[내_IP]:5001` (같은 Wi-Fi의 다른 기기에서 접속)

### 5. 사용 방법

1. **사진 업로드 모드**
   - "사진 업로드" 버튼 클릭
   - 얼굴 사진 선택 (정면 또는 측면)
   - 자동 분석 → 결과 표시

2. **실시간 카메라 모드**
   - "카메라 모드" 버튼 클릭
   - 카메라 권한 허용
   - 얼굴을 카메라에 맞추면 실시간 분석


## 🔧 코드 수정 및 배포

### 코드 수정 후 로컬 테스트

1. **파일 수정**
   ```bash
   # 예: 설정 변경
   code config/settings.py
   
   # 예: 분석 로직 수정
   code app/core/analyzer.py
   ```

2. **서버 재시작**
   ```bash
   # Ctrl+C로 기존 서버 종료
   python run.py
   ```

3. **브라우저 새로고침**
   - `Ctrl+F5` (하드 리프레시)로 캐시 초기화

### 설정 변경 가이드

**config/settings.py**에서 주요 파라미터 조정:

```python
# Willis 정상 범위 수정
WILLIS_RATIO_NORMAL_MIN = 0.90  # 0.85로 낮추면 더 관대한 평가
WILLIS_RATIO_NORMAL_MAX = 1.10  # 1.15로 높이면 더 관대한 평가

# 정면/측면 판단 기준
FRONTAL_SYMMETRY_THRESHOLD = 0.85  # 0.80으로 낮추면 측면도 정면으로 판단

# 얼굴 감지 민감도
MIN_DETECTION_CONFIDENCE = 0.1  # 0.3으로 높이면 더 정확하게 감지
```

### Git으로 변경사항 관리

```bash
# 변경 파일 확인
git status

# 변경 파일 스테이징
git add .

# 커밋
git commit -m "설명: 무엇을 변경했는지"

# GitHub에 푸시
git push origin main
```

### 자동 배포 (Render.com)

GitHub에 push하면 **자동으로 배포**됩니다:

1. `git push origin main` 실행
2. Render.com이 자동으로 감지
3. 5-10분 후 배포 완료
4. `https://willis-facemap.onrender.com` 업데이트됨

**배포 상태 확인:**
- Render 대시보드: https://dashboard.render.com
- 로그에서 빌드/배포 진행 상황 확인

### Docker로 로컬 테스트

배포 전에 Docker로 프로덕션 환경 테스트:

```bash
# 이미지 빌드
docker build -t willis-facemap .

# 컨테이너 실행
docker run -p 5001:5001 willis-facemap

# 또는 docker-compose 사용
docker-compose up
```



## 치과 활용 예시 🏥

### 1. 수직 고경 감소 진단

- **문제**: 다수 치아 상실, 치아 마모로 인한 수직 고경 감소
- **활용**: Willis 계측법으로 객관적 평가
- **결과**: 비율 < 0.95 → 전악 보철 수복 고려

### 2. 치료 전후 비교

- 치료 전 Willis 비율 측정
- 보철 수복 후 재측정
- 수직 고경 회복 확인

### 3. 교정 치료 계획

- 턱 각도 및 대칭성 평가
- 입 모양 변화 추적
- 심미적 목표 설정

### 4. 환자 교육

- 실시간 시각화로 상태 설명
- 색상 코드로 직관적 이해
- 치료 필요성 설득력 향상

## 논문 연구 결과 

논문에서 보고된 Neuro-T 모델의 성능:

- **정면 얼굴 사진 분류 정확도**: 90.00%
- **측면 얼굴 사진**: 84.00%
- **측방두부방사선사진**: 73.07%

→ 정면 얼굴 사진이 Willis 계측법에 가장 효과적

**교육적 효과:**

- 치과대학 학생과 전공의의 Willis 분류 정확도가 프로그램 사용 후 유의하게 상승
- 임상 교육 도구로서의 활용 가능성 입증

## 시스템 요구사항 

- **OS**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.8 이상
- **RAM**: 최소 4GB (8GB 권장)
- **웹캠**: 720p 이상 권장 (정면 촬영)
- **프로세서**: Intel i5 이상 또는 동급

## 사용 팁 

### Willis 계측을 위한 최적 촬영 조건

1. **정면 응시**: 카메라를 정면으로 똑바로 보기
2. **적절한 거리**: 얼굴 전체가 화면에 들어오도록
3. **조명**: 균일한 조명, 그림자 최소화
##  Willis 계측법 상세 설명

### 측정 원리

Willis 안면 계측법은 수직 고경을 평가하는 방법입니다:

1. **동공 중심 - 입 중심 거리** (Pupil to Mouth)
2. **코 base - 턱끝 거리** (Nose to Chin)
3. **비율 계산**: `ratio = (코-턱) / (동공-입)`

### 판정 기준

```python
if 0.90 <= ratio <= 1.10:
    → "정상"
elif ratio < 0.90:
    → "평균 이하 (수직고경 감소)"
else:
    → "평균 이상 (수직고경 증가)"
```

### MediaPipe 랜드마크 사용

- **눈동자**: 양쪽 눈 7개 점 평균 (#33, #133, #160, #159, #158, #157, #173 등)
- **입**: #61, #291, #13, #14 평균
- **코 base**: #2
- **턱끝**: #152

### 정면/측면 자동 판단

- 양쪽 눈 크기 비교 → 대칭도 계산
- **대칭도 ≥ 85%**: 정면 분석 (Willis 방법)
- **대칭도 < 85%**: 측면 분석 (턱 각도, 돌출도)



## 아키텍처 설계 원칙

### 단일 책임 원칙 (SRP)
각 모듈/클래스는 하나의 명확한 책임만 가집니다:

- **FaceDetector**: MediaPipe 초기화, 랜드마크 감지만
- **LandmarkExtractor**: 468개 점에서 특징점 추출만
- **WillisAnalyzer**: Willis 비율 계산 및 분류만
- **LandmarkVisualizer**: 이미지에 랜드마크/측정선 그리기만

### 계층 분리

```
프레젠테이션 계층 (templates/index.html)
    ↓
라우팅 계층 (app/routes/main_routes.py)
    ↓
비즈니스 로직 (app/core/*.py)
    ↓
유틸리티 (app/utils/*.py)
    ↓
설정 (config/settings.py)
```

### 의존성 주입

전역 상태를 최소화하고 서비스를 명시적으로 초기화:

```python
# wsgi.py
init_services()  # detector, analyzer 초기화
app = create_app()  # Flask 앱 생성
```

### 코드 품질 지표

- **함수당 평균**: 12줄 (가독성 최적화)
- **파일당 평균**: 50줄
- **최대 파일**: 150줄 (analyzer.py)
- **순환 복잡도**: 낮음



## API 엔드포인트

### `POST /analyze`
업로드된 이미지 분석

**Request:**
```http
POST /analyze HTTP/1.1
Content-Type: multipart/form-data

file: [이미지 파일]
```

**Response:**
```json
{
  "analysis_type": "정면 분석 (Willis 방법)",
  "pupil_to_mouth": 245.3,
  "nose_to_chin": 230.8,
  "ratio": 0.941,
  "classification": "평균 이하 (수직고경 감소)",
  "symmetry": 87.5,
  "is_frontal": true,
  "landmarks": {
    "pupil_center": [320, 180],
    "mouth_center": [320, 380],
    "nose_point": [320, 280],
    "chin_point": [320, 480]
  },
  "all_landmarks": [[x1, y1], [x2, y2], ...],
  "vis_image": "base64_encoded_image"
}
```

### `POST /analyze_frame`
실시간 카메라 프레임 분석

**Request:**
```json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

**Response:** (동일한 JSON 형식, vis_image 제외)



## 보안 및 최적화

### 보안 기능
- 파일 업로드 크기 제한 (16MB)
- MIME 타입 검증 (이미지만 허용)
-  입력 데이터 검증
- 에러 처리 및 로깅

### 성능 최적화
- opencv-python-headless (서버 최적화)
- MediaPipe GPU 가속 지원
- Gunicorn 멀티 워커
- 이미지 캐싱 (브라우저)

### 환경 변수

`.env.example` 참고하여 `.env` 파일 생성:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAX_CONTENT_LENGTH=16777216  # 16MB
```



## 문제 해결

### 얼굴이 감지되지 않음
- 조명 확인 (너무 어둡거나 밝지 않게)
- 얼굴을 정면으로 향하기
- `config/settings.py`에서 `MIN_DETECTION_CONFIDENCE` 낮추기

### 서버가 시작되지 않음
```bash
# 포트 충돌 확인
netstat -ano | findstr :5001

# 다른 포트 사용
python run.py --port 5002
```

### MediaPipe 모델 다운로드 실패
```bash
# 수동 다운로드
curl -L "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" -o face_landmarker.task
```

### Docker 빌드 실패
```bash
# 캐시 없이 재빌드
docker build --no-cache -t willis-facemap .
```

## 기여 가이드

### 버그 리포트
GitHub Issues에 다음 정보와 함께 제출:
- 문제 설명
- 재현 단계
- 예상 동작 vs 실제 동작
- 환경 (OS, Python 버전)

### Pull Request
1. Fork 후 feature 브랜치 생성
2. 코드 작성 (함수당 평균 15줄 이하 유지)
3. 커밋 메시지: `feat: 기능 추가` 또는 `fix: 버그 수정`
4. PR 제출



##  기술 스택

- **Backend**: Python 3.11+, Flask 3.0+
- **Computer Vision**: MediaPipe 0.10+, OpenCV (headless)
- **Frontend**: HTML5, CSS3 (Liquid Glass Design), Vanilla JavaScript
- **Deployment**: Docker, Gunicorn, Render.com
- **Version Control**: Git, GitHub

## 학습 리소스

- [MediaPipe Face Mesh 문서](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [프로젝트 아키텍처 설명](docs/ARCHITECTURE.md)
- [리팩토링 로그](REFACTORING.md)

## 라이선스

MIT License - 교육 및 연구 목적으로 자유롭게 사용 가능

**의료 면책**: 이 프로그램은 진단 보조 도구입니다. 최종 진단은 반드시 치과 전문의가 수행해야 합니다.

---

**Made with for Dental Care**  
GitHub: [@mlnyx](https://github.com/mlnyx) | Website: [willis-facemap.onrender.com](https://willis-facemap.onrender.com)

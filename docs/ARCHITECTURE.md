# Willis 안면 계측법 - 클린 코드 버전

## 📁 프로젝트 구조

```
facemap/
├── src/                          # 소스 코드
│   ├── core/                     # 핵심 로직
│   │   ├── landmarker.py         # 얼굴 랜드마크 감지
│   │   └── analyzer.py           # Willis 분석
│   ├── ui/                       # 사용자 인터페이스
│   │   └── visualizer.py         # 시각화
│   └── utils/                    # 유틸리티
│       └── text_renderer.py      # 한글 렌더링
│
├── willis_realtime.py            # 실시간 카메라 분석
├── willis_photo_analysis.py      # 사진 분석
├── willis_web.py                 # 웹 서버 (Flask)
├── requirements.txt              # 의존성
│
├── data/                         # 데이터
│   ├── input/                    # 입력 이미지
│   └── output/                   # 출력 결과
│
├── tests/                        # 테스트
├── docs/                         # 문서
└── archive/                      # 이전 버전
```

## 🚀 사용법

### 1. 실시간 카메라 분석

```bash
python willis_realtime.py
```

### 2. 사진 분석

```bash
python willis_photo_analysis.py data/input/photo.jpg
```

### 3. 웹 서버

```bash
python willis_web.py
# http://localhost:5001
```

## 📦 설치

```bash
pip install -r requirements.txt
```

## 🏗️ 아키텍처

### Core 모듈

- **FaceLandmarker**: MediaPipe를 사용한 얼굴 랜드마크 감지
- **WillisAnalyzer**: Willis 비율 계산 및 분류

### UI 모듈

- **WillisVisualizer**: 결과 시각화 (랜드마크, 측정선, 정보 패널)

### Utils 모듈

- **KoreanTextRenderer**: PIL 기반 한글 렌더링

## 🎯 핵심 원칙

### 1. Single Responsibility Principle (SRP)

- 각 클래스는 하나의 책임만 가짐
- `FaceLandmarker`: 얼굴 감지만
- `WillisAnalyzer`: Willis 분석만
- `WillisVisualizer`: 시각화만

### 2. Don't Repeat Yourself (DRY)

- 공통 로직은 모듈화
- 랜드마크 인덱스 상수화
- 색상 상수화

### 3. Clean Code

- 명확한 함수/변수 이름
- Docstring으로 문서화
- Type Hints 사용

### 4. Separation of Concerns

- Core: 비즈니스 로직
- UI: 화면 표시
- Utils: 공통 기능

## 📊 데이터 흐름

```
카메라/사진
    ↓
FaceLandmarker (얼굴 감지)
    ↓
WillisAnalyzer (비율 계산)
    ↓
WillisVisualizer (시각화)
    ↓
화면 출력/파일 저장
```

## 🧪 테스트

```bash
# 단위 테스트
python -m pytest tests/

# 특정 테스트
python -m pytest tests/test_analyzer.py
```

## 📝 라이센스

MIT License

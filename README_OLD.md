# 치과용 얼굴 좌표 인식 프로그램

MediaPipe를 활용한 실시간 얼굴 랜드마크 감지 및 분석 프로그램입니다.
특히 **입과 턱 부분**에 중점을 두어 치과 진료에 활용할 수 있도록 설계되었습니다.

## 주요 기능 ✨

### 기본 기능

- 🎯 실시간 얼굴 랜드마크 감지 (468개 포인트)
- 👄 입술 외곽 및 내부 윤곽 감지 (빨간색/주황색)
- 🦴 턱 라인 및 턱 끝 감지 (파란색)
- 📏 입 너비/높이, 턱 너비/길이 실시간 측정

### 고급 분석 기능

- 📊 입 벌림 정도 측정 (0-100%)
- 📐 턱 각도 계산
- ⚖️ 얼굴 대칭성 점수 (입과 턱 중심)
- 📈 실시간 그래프 표시
- 💾 분석 데이터 저장 (JSON)
- 📸 스크린샷 및 리포트 생성

## 설치 방법 🚀

### 1. Python 환경 확인

Python 3.8 이상이 필요합니다.

```bash
python --version
```

### 2. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install opencv-python mediapipe numpy matplotlib
```

## 사용 방법 📖

### 기본 모드 실행

가장 간단한 방식으로 얼굴 인식과 측정을 수행합니다.

```bash
python main.py
```

**키보드 단축키:**

- `q` : 종료
- `s` : 스크린샷 저장
- `r` : 측정값 초기화

---

### 고급 모드 실행 (권장)

실시간 그래프, 데이터 기록, 리포트 생성 등 모든 기능을 사용합니다.

```bash
python advanced_analyzer.py
```

**키보드 단축키:**

- `q` 또는 `ESC` : 종료
- `s` : 현재 화면 스크린샷 저장
- `r` : 데이터 기록 시작/중지 (빨간 점 표시)
- `g` : 실시간 그래프 표시 켜기/끄기
- `e` : 분석 리포트 저장 (JSON)
- `v` : 분석 요약 이미지 저장 (PNG)
- `c` : 모든 데이터 초기화

---

### 이미지 파일 분석

정적 이미지를 분석할 수도 있습니다.

```bash
python main.py path/to/your/image.jpg
```

## 화면 표시 정보 📺

### 왼쪽 상단 패널

```
=== 치과용 얼굴 분석 ===
입 너비: 125.3px
입 높이: 15.8px
턱 너비: 215.7px
턱 길이: 98.2px
```

### 오른쪽 상단 패널 (고급 모드)

```
=== 상세 분석 ===
입 벌림: 35.2%
턱 각도: 142.5°
대칭성: 92.3%
평가: 매우 대칭적
```

### 화면 하단

- 실시간 그래프 (입 벌림, 턱 각도, 대칭성 추이)
- 색상 범례

## 출력 파일 📁

프로그램 실행 중 다음과 같은 파일들이 생성됩니다:

### 스크린샷

```
dental_screenshot_20231219_153045.png
dental_analysis_20231219_153045.png
```

### 분석 리포트 (JSON)

```json
{
  "analysis_date": "2023-12-19T15:30:45",
  "total_frames": 450,
  "statistics": {
    "mouth_openness": {
      "mean": 32.5,
      "max": 85.2,
      "min": 5.1,
      "std": 15.3
    },
    "jaw_angle": {
      "mean": 142.8,
      "max": 148.2,
      "min": 138.5,
      "std": 2.1
    },
    "symmetry_score": {
      "mean": 91.5,
      "max": 96.8,
      "min": 85.2,
      "std": 3.2
    }
  },
  "raw_data": { ... }
}
```

### 분석 요약 이미지

```
dental_summary_20231219_153045.png
```

- 입 벌림 시계열 그래프
- 턱 각도 분포 히스토그램
- 대칭성 시계열 그래프
- 통계 요약 텍스트

## 프로그램 구조 🏗️

```
facemap/
├── main.py                  # 기본 얼굴 인식 프로그램
├── dental_visualizer.py     # 시각화 및 분석 모듈
├── advanced_analyzer.py     # 통합 고급 분석 프로그램
├── requirements.txt         # 필수 패키지 목록
└── README.md               # 이 문서
```

### 주요 클래스

#### `DentalFaceMapper` (main.py)

- MediaPipe Face Mesh 초기화
- 얼굴 랜드마크 감지 및 시각화
- 기본 측정값 계산 (입/턱 크기)

#### `DentalVisualizer` (dental_visualizer.py)

- 입 벌림 정도 계산
- 턱 각도 및 대칭성 분석
- 실시간 그래프 생성
- 데이터 저장 및 리포트 생성

#### `AdvancedDentalAnalyzer` (advanced_analyzer.py)

- 위 두 클래스를 통합
- 실시간 데이터 기록
- 사용자 인터페이스 제공

## 기술 스택 🛠️

- **MediaPipe Face Mesh**: 468개 얼굴 랜드마크 감지
- **OpenCV**: 실시간 영상 처리 및 시각화
- **NumPy**: 수치 계산 및 데이터 처리
- **Matplotlib**: 그래프 및 리포트 생성

## 랜드마크 인덱스 📍

프로그램에서 사용하는 주요 랜드마크:

### 입 관련

- **입술 외곽**: 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291 등
- **입술 내부**: 78, 95, 88, 178, 87, 14, 317, 402, 318, 324 등
- **입 좌우 끝**: 61 (왼쪽), 291 (오른쪽)
- **입 상하 중앙**: 13 (위), 14 (아래)

### 턱 관련

- **턱 라인**: 172, 136, 150, 149, 176, 148, 152, 377, 400, 378 등
- **턱 끝**: 152 (중앙 하단)
- **턱 측면**: 234 (왼쪽), 454 (오른쪽)

## 측정 알고리즘 🧮

### 입 벌림 정도

```
입 벌림(%) = (윗입술-아랫입술 거리) / (입 너비 × 0.2) × 100
```

### 턱 각도

```
턱 각도 = 좌측 턱선 벡터와 우측 턱선 벡터 사이의 각도
```

### 대칭성 점수

```
대칭성 = 100 - (좌우 랜드마크 거리 차이 / 얼굴 너비 × 100)
```

## 치과 활용 예시 🏥

1. **교정 전후 비교**

   - 턱 각도 및 대칭성 변화 추적
   - 입 모양 변화 측정

2. **턱관절 장애 진단 보조**

   - 입 벌림 범위 측정
   - 개폐 시 대칭성 확인

3. **보철 치료 계획**

   - 입술 위치 및 턱 라인 분석
   - 심미적 비율 평가

4. **환자 교육**
   - 실시간 시각화로 상태 설명
   - 치료 목표 설정

## 문제 해결 🔧

### 카메라가 열리지 않음

```bash
# 카메라 번호를 변경해보세요
python advanced_analyzer.py
# 코드에서 camera_id=0 을 camera_id=1 로 변경
```

### MediaPipe 설치 오류

```bash
# M1/M2 Mac의 경우
pip install mediapipe --upgrade
```

### 성능이 느림

- 해상도를 낮춰보세요 (코드에서 `cap.set()` 사용)
- `min_detection_confidence` 값을 높여보세요

## 시스템 요구사항 💻

- **OS**: Windows 10/11, macOS 10.14+, Linux
- **Python**: 3.8 이상
- **RAM**: 최소 4GB (8GB 권장)
- **웹캠**: 720p 이상 권장
- **프로세서**: Intel i5 이상 또는 동급 (실시간 처리)

## 라이선스 📄

이 프로젝트는 교육 및 연구 목적으로 자유롭게 사용할 수 있습니다.

의료 기기로 사용하기 위해서는 관련 규정 및 승인이 필요할 수 있습니다.

## 참고 자료 📚

- [MediaPipe Face Mesh](https://google.github.io/mediapipe/solutions/face_mesh.html)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Face Landmark 468 Points](https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png)

## 업데이트 계획 🚧

- [ ] 3D 얼굴 모델 재구성
- [ ] 다중 얼굴 동시 분석
- [ ] 클라우드 데이터베이스 연동
- [ ] 모바일 앱 버전 개발
- [ ] AI 기반 자동 진단 보조

## 문의 및 기여 💬

문제가 발생하거나 개선 아이디어가 있으시면 이슈를 등록해주세요!

---

**Made with ❤️ for Dental Care**

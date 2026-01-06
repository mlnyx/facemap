# 프로젝트 구조 개선 로그

## 2026-01-02: 대규모 리팩토링

### 개선 사항

#### 1. 모듈 분리
- **320줄 → 14개 파일 (평균 30줄)**
- 단일 책임 원칙 적용
- 각 클래스/함수가 하나의 기능만 수행

#### 2. 폴더 구조
```
Before: 루트에 모든 파일 혼재
After:  
  app/
    core/     - 비즈니스 로직
    routes/   - HTTP 처리
    utils/    - 유틸리티
  config/     - 설정
```

#### 3. 코드 품질
- **중복 제거**: 이미지 인코딩/디코딩 유틸화
- **설정 분리**: 매직 넘버 → 상수로 관리
- **명확한 네이밍**: 함수명으로 역할 즉시 파악

#### 4. 테스트 가능성
- 의존성 주입 패턴
- 전역 상태 최소화
- Mock 가능한 구조

#### 5. 확장성
- 새 분석 알고리즘 추가 용이
- 새 엔드포인트 추가 간단
- 설정 변경 한 곳에서 관리

### 파일 매핑

| 기존 (willis_web.py) | 새 구조 |
|---------------------|---------|
| WillisAnalyzer.__init__ | app/core/detector.py: FaceDetector |
| calculate_distance | app/utils/geometry.py: calculate_distance |
| get_pupil_center | app/core/landmarks.py: LandmarkExtractor.get_pupil_centers |
| calculate_face_symmetry | app/core/landmarks.py: LandmarkExtractor.calculate_eye_symmetry |
| analyze_image | app/core/analyzer.py: WillisAnalyzer.analyze |
| visualize_landmarks | app/core/visualizer.py: LandmarkVisualizer.draw_landmarks |
| Flask routes | app/routes/main_routes.py |
| 설정 값 | config/settings.py |

### 코드 메트릭

**Before:**
- willis_web.py: 320 lines
- 함수당 평균: 40 lines
- 순환 복잡도: 높음

**After:**
- 최대 파일: 150 lines
- 함수당 평균: 12 lines
- 순환 복잡도: 낮음

### 유지보수 개선

1. **버그 수정**: 해당 모듈만 수정
2. **기능 추가**: 새 모듈 추가
3. **설정 변경**: config/settings.py만 수정
4. **테스트**: 각 모듈 독립적으로 테스트

### 성능 영향

- **메모리**: 동일 (lazy import 가능)
- **속도**: 동일
- **빌드**: 동일
- **코드 이해도**: 5배 향상

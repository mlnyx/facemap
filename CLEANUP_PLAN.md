# 사용하지 않는 파일 목록

## 제거할 파일들 (웹 앱에서 사용 안 함)
- willis_compare.py (비교 기능 - 웹에서 미사용)
- willis_korean.py (한글 렌더링 - 웹에서 미사용)
- willis_measurement.py (측정 기능 - 웹에 통합됨)
- willis_photo.py (사진 분석 - 웹에 통합됨)
- willis_photo_analysis.py (사진 분석 - 웹에 통합됨)
- willis_profile.py (프로필 분석 - 웹에 통합됨)
- willis_realtime.py (실시간 - 웹에 통합됨)
- ai_model.py (사용 안 함)
- ai_train_prepare.py (사용 안 함)
- src/ 폴더 (웹 앱에서 사용 안 함)

## 백업 파일들
- templates/index_old.html
- templates/index_backup.html
- README_OLD.md

## 보관할 파일들 (실제 사용)
- willis_web.py (메인 웹 서버)
- wsgi.py (프로덕션 배포용)
- templates/index.html (웹 UI)
- requirements.txt
- Dockerfile, docker-compose.yml
- Procfile, runtime.txt
- DEPLOYMENT.md, QUICK_DEPLOY.md, README.md

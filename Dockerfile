FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 포트 노출
EXPOSE 5001

# 환경 변수
ENV FLASK_APP=willis_web.py
ENV PYTHONUNBUFFERED=1

# Gunicorn으로 실행
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "--worker-class", "sync"]

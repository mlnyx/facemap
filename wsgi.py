"""
WSGI 엔트리 포인트
프로덕션 서버(Gunicorn, uWSGI 등)에서 사용
"""

from app import create_app
from app.routes.main_routes import init_services

# 서비스 초기화
init_services()

# Flask 앱 생성
app = create_app()

if __name__ == "__main__":
    app.run()

"""
WSGI 엔트리 포인트
프로덕션 서버(Gunicorn, uWSGI 등)에서 사용
"""

from willis_web import app

if __name__ == "__main__":
    app.run()

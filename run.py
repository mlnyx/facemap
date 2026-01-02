"""Willis Facial Analysis System - 애플리케이션 진입점"""
from app import create_app
from app.routes.main_routes import init_services
from config import HOST, PORT, DEBUG


def main():
    """애플리케이션 시작"""
    print("\n" + "=" * 70)
    print("Willis Facial Analysis System - Web Application")
    print("=" * 70)
    
    # 서비스 초기화
    init_services()
    
    # Flask 앱 생성
    app = create_app()
    
    # 서버 시작
    print("=" * 70)
    print("✓ 서버 시작!")
    print("=" * 70)
    print("\n브라우저에서 열기:")
    print(f"  http://localhost:{PORT}")
    print("\n종료: Ctrl+C")
    print("=" * 70 + "\n")
    
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)


if __name__ == '__main__':
    main()

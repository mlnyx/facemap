"""Flask 애플리케이션 팩토리"""
from flask import Flask


def create_app():
    """Flask 앱 생성 및 설정"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    from config import MAX_CONTENT_LENGTH
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # 라우트 등록
    from app.routes import main_routes
    app.register_blueprint(main_routes.bp)
    
    return app

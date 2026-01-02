"""메인 라우트"""
from flask import Blueprint, render_template, jsonify, request

from app.core import FaceDetector, WillisAnalyzer, LandmarkVisualizer
from app.utils import encode_image_to_base64, decode_base64_to_image, read_image_from_file

bp = Blueprint('main', __name__)

# 전역 인스턴스 (앱 시작 시 초기화)
detector = None
analyzer = None


def init_services():
    """서비스 초기화"""
    global detector, analyzer
    
    print("\n초기화 중...")
    print("  1. MediaPipe 얼굴 감지기 로드...")
    detector = FaceDetector()
    print("  ✓ 완료")
    
    print("  2. Willis 분석기 생성...")
    analyzer = WillisAnalyzer()
    print("  ✓ 완료")
    
    print("\n✓ 모든 서비스 준비 완료\n")


@bp.route('/')
def index():
    """메인 페이지"""
    import subprocess
    try:
        git_version = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd='.',
            text=True
        ).strip()
    except:
        git_version = 'unknown'
    
    return render_template('index.html', git_version=git_version)


@bp.route('/analyze', methods=['POST'])
def analyze_photo():
    """업로드된 사진 분석"""
    # 파일 검증
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    if not file.content_type.startswith('image/'):
        return jsonify({'error': '이미지 파일만 업로드 가능합니다'}), 400
    
    try:
        # 이미지 읽기
        image = read_image_from_file(file)
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        
        # 얼굴 감지
        landmarks = detector.detect_landmarks(image)
        if landmarks is None:
            return jsonify({'error': '얼굴을 찾을 수 없습니다'}), 400
        
        # Willis 분석
        h, w = image.shape[:2]
        result = analyzer.analyze(landmarks, w, h)
        
        # 랜드마크 시각화
        image = LandmarkVisualizer.draw_landmarks(image, result)
        
        # base64 인코딩
        result['vis_image'] = encode_image_to_base64(image)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500


@bp.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    """실시간 카메라 프레임 분석"""
    try:
        data = request.json
        if not data or 'frame' not in data:
            return jsonify({'error': '프레임 데이터가 없습니다'}), 400
        
        # Base64 디코딩
        image = decode_base64_to_image(data['frame'])
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        
        # 얼굴 감지
        landmarks = detector.detect_landmarks(image)
        if landmarks is None:
            return jsonify({'error': '얼굴을 찾을 수 없습니다'}), 400
        
        # Willis 분석
        h, w = image.shape[:2]
        result = analyzer.analyze(landmarks, w, h)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"프레임 분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500

"""
Willis Facial Analysis System - Web Application
실시간 얼굴 분석 및 Willis 계측법 기반 수직 고경 평가
"""

from flask import Flask, render_template, jsonify, request
import cv2
import numpy as np
import os
from base64 import b64encode, b64decode
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit


class WillisAnalyzer:
    """Willis 안면 계측 분석기"""
    
    def __init__(self):
        """MediaPipe 초기화 및 모델 로드"""
        print("MediaPipe 초기화 중...")
        
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            import urllib.request
            
            # 모델 파일 확인 및 다운로드
            model_path = "face_landmarker.task"
            if not os.path.exists(model_path):
                print("모델 다운로드 중...")
                url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                urllib.request.urlretrieve(url, model_path)
                print("다운로드 완료!")
            
            # MediaPipe FaceLandmarker 설정
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=1,
                min_face_detection_confidence=0.1,
                min_face_presence_confidence=0.1,
                min_tracking_confidence=0.1,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False
            )
            self.detector = vision.FaceLandmarker.create_from_options(options)
            print("✓ MediaPipe 초기화 완료")
            
        except Exception as e:
            print(f"MediaPipe 초기화 실패: {e}")
            raise
        
        # 카메라 초기화
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(1)
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("✓ 카메라 초기화 완료")
    
    @staticmethod
    def calculate_distance(p1, p2):
        """두 점 사이의 유클리드 거리 계산"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_pupil_center(self, landmarks, w, h):
        """양쪽 눈의 중심점 계산"""
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        left_x = np.mean([landmarks[i].x * w for i in left_eye_indices])
        left_y = np.mean([landmarks[i].y * h for i in left_eye_indices])
        right_x = np.mean([landmarks[i].x * w for i in right_eye_indices])
        right_y = np.mean([landmarks[i].y * h for i in right_eye_indices])
        
        center_x = (left_x + right_x) / 2
        center_y = (left_y + right_y) / 2
        
        return (center_x, center_y), (left_x, left_y), (right_x, right_y)
    
    def calculate_face_symmetry(self, landmarks, w, h):
        """얼굴 대칭도 계산 (정면/측면 판단용)"""
        left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        left_eye_points = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in left_eye_indices])
        right_eye_points = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in right_eye_indices])
        
        left_size = np.max(left_eye_points[:, 0]) - np.min(left_eye_points[:, 0])
        right_size = np.max(right_eye_points[:, 0]) - np.min(right_eye_points[:, 0])
        
        symmetry = min(left_size, right_size) / max(left_size, right_size) if max(left_size, right_size) > 0 else 0
        return symmetry
    
    def analyze_image(self, image):
        """이미지 분석 (업로드된 사진 또는 실시간 프레임)"""
        h, w = image.shape[:2]
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect(mp_image)
        
        # 얼굴 감지 실패
        if not result.face_landmarks:
            return {'error': '얼굴을 찾을 수 없습니다'}
        
        landmarks = result.face_landmarks[0]
        
        # 대칭도 계산 (정면/측면 판단)
        symmetry = self.calculate_face_symmetry(landmarks, w, h)
        is_frontal = symmetry >= 0.85
        
        # Willis 계측
        pupil_center, left_pupil, right_pupil = self.get_pupil_center(landmarks, w, h)
        
        mouth_x = (landmarks[61].x + landmarks[291].x) / 2 * w
        mouth_y = (landmarks[13].y + landmarks[14].y) / 2 * h
        mouth_center = (mouth_x, mouth_y)
        
        nose_point = (landmarks[2].x * w, landmarks[2].y * h)
        chin_point = (landmarks[152].x * w, landmarks[152].y * h)
        
        pupil_to_mouth = self.calculate_distance(pupil_center, mouth_center)
        nose_to_chin = self.calculate_distance(nose_point, chin_point)
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0
        
        if is_frontal:
            # 정면 분석
            if 0.90 <= ratio <= 1.10:
                classification = "정상"
            elif ratio < 0.90:
                classification = "평균 이하 (수직고경 감소)"
            else:
                classification = "평균 이상 (수직고경 증가)"
            
            # 모든 랜드마크 좌표
            all_landmarks = [[int(lm.x * w), int(lm.y * h)] for lm in landmarks]
            
            return {
                'analysis_type': '정면 분석 (Willis 방법)',
                'pupil_to_mouth': round(pupil_to_mouth, 1),
                'nose_to_chin': round(nose_to_chin, 1),
                'ratio': round(ratio, 3),
                'classification': classification,
                'symmetry': round(symmetry * 100, 1),
                'is_frontal': True,
                'landmarks': {
                    'pupil_center': [int(pupil_center[0]), int(pupil_center[1])],
                    'mouth_center': [int(mouth_center[0]), int(mouth_center[1])],
                    'nose_point': [int(nose_point[0]), int(nose_point[1])],
                    'chin_point': [int(chin_point[0]), int(chin_point[1])],
                    'left_pupil': [int(left_pupil[0]), int(left_pupil[1])],
                    'right_pupil': [int(right_pupil[0]), int(right_pupil[1])]
                },
                'all_landmarks': all_landmarks
            }
        else:
            # 측면 분석
            nose_tip = (landmarks[1].x * w, landmarks[1].y * h)
            chin_bottom = (landmarks[152].x * w, landmarks[152].y * h)
            
            dx = chin_bottom[0] - nose_tip[0]
            dy = chin_bottom[1] - nose_tip[1]
            angle = abs(np.degrees(np.arctan2(dy, dx)))
            
            jaw_prominence = nose_to_chin / h * 100
            
            if 15 < jaw_prominence < 25 and 70 < angle < 110:
                profile_status = "자연스러운 측면 윤곽"
                naturalness = "양호"
            elif jaw_prominence >= 25 or angle >= 110:
                profile_status = "턱이 다소 길거나 각진 편"
                naturalness = "주의"
            else:
                profile_status = "턱이 다소 짧은 편"
                naturalness = "주의"
            
            return {
                'analysis_type': '측면 분석 (Profile 방법)',
                'jaw_prominence': round(jaw_prominence, 1),
                'chin_angle': round(angle, 1),
                'nose_to_chin': round(nose_to_chin, 1),
                'classification': profile_status,
                'naturalness': naturalness,
                'symmetry': round(symmetry * 100, 1),
                'is_frontal': False
            }
    
    def visualize_landmarks(self, image, result):
        """랜드마크 시각화"""
        if not result.get('is_frontal') or 'landmarks' not in result:
            return image
        
        # 468개 랜드마크 (회색 작은 점)
        all_landmarks = result.get('all_landmarks', [])
        for (x, y) in all_landmarks:
            cv2.circle(image, (x, y), 1, (180, 180, 180), -1)
        
        # 주요 포인트 (노란색/빨간색 큰 점)
        for key, color in zip(
            ['pupil_center', 'mouth_center', 'nose_point', 'chin_point'],
            [(255, 255, 0), (255, 255, 0), (0, 0, 255), (0, 0, 255)]
        ):
            pt = result['landmarks'][key]
            cv2.circle(image, tuple(pt), 7, color, -1)
        
        # 측정선
        cv2.line(image, 
                tuple(result['landmarks']['pupil_center']), 
                tuple(result['landmarks']['mouth_center']), 
                (255, 0, 0), 3)
        cv2.line(image, 
                tuple(result['landmarks']['nose_point']), 
                tuple(result['landmarks']['chin_point']), 
                (0, 0, 255), 3)
        
        return image


# 전역 analyzer 인스턴스
analyzer = None


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze_photo():
    """업로드된 사진 분석"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    if not file.content_type.startswith('image/'):
        return jsonify({'error': '이미지 파일만 업로드 가능합니다'}), 400
    
    try:
        # 이미지 읽기
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        
        # 분석
        result = analyzer.analyze_image(image)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # 랜드마크 시각화
        image = analyzer.visualize_landmarks(image, result)
        
        # base64 인코딩
        _, buffer = cv2.imencode('.jpg', image)
        img_b64 = b64encode(buffer).decode('utf-8')
        result['vis_image'] = img_b64
        
        return jsonify(result)
    
    except Exception as e:
        print(f"분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500


@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    """실시간 카메라 프레임 분석"""
    try:
        data = request.json
        if not data or 'frame' not in data:
            return jsonify({'error': '프레임 데이터가 없습니다'}), 400
        
        # Base64 디코딩
        frame_data = re.sub('^data:image/.+;base64,', '', data['frame'])
        frame_bytes = b64decode(frame_data)
        
        # NumPy 배열로 변환
        nparr = np.frombuffer(frame_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        
        # 분석
        result = analyzer.analyze_image(image)
        return jsonify(result)
    
    except Exception as e:
        print(f"프레임 분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Willis Facial Analysis System - Web Application")
    print("=" * 70)
    print("\n초기화 중...\n")
    
    analyzer = WillisAnalyzer()
    
    print("\n" + "=" * 70)
    print("✓ 서버 시작!")
    print("=" * 70)
    print("\n브라우저에서 열기:")
    print("  http://localhost:5001")
    print("\n종료: Ctrl+C")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

"""
Willis 안면 계측법 - 웹 기반 실시간 버전
브라우저에서 실시간으로 볼 수 있습니다 (macOS GUI 문제 해결)
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from datetime import datetime
import json
import os
import sys
from werkzeug.utils import secure_filename
import tempfile
from base64 import b64encode
from io import BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# 전역 변수
latest_data = {
    'pupil_to_mouth': 0,
    'nose_to_chin': 0,
    'ratio': 0,
    'classification': '대기 중'
}

class WillisWebAnalyzer:
    def __init__(self):
        print("MediaPipe 초기화 중...")
        
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            model_path = "face_landmarker.task"
            if not os.path.exists(model_path):
                print("모델 다운로드 중...")
                import urllib.request
                url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                urllib.request.urlretrieve(url, model_path)
                print("다운로드 완료!")
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=1,
                min_face_detection_confidence=0.1,  # 더 낮춤 (측면 감지용)
                min_face_presence_confidence=0.1,
                min_tracking_confidence=0.1,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False
            )
            self.detector = vision.FaceLandmarker.create_from_options(options)
            self.python = python
            self.vision = vision
            print("✓ MediaPipe 초기화 완료")
            
        except Exception as e:
            print(f"MediaPipe 초기화 실패: {e}")
            sys.exit(1)
        
        # 카메라 초기화
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(1)
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("✓ 카메라 초기화 완료")
    
    def calculate_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_pupil_center(self, landmarks, w, h):
        left_eye = [33, 133, 160, 159, 158, 157, 173]
        right_eye = [362, 263, 387, 386, 385, 384, 398]
        
        left_x = np.mean([landmarks[i].x * w for i in left_eye])
        left_y = np.mean([landmarks[i].y * h for i in left_eye])
        right_x = np.mean([landmarks[i].x * w for i in right_eye])
        right_y = np.mean([landmarks[i].y * h for i in right_eye])
        
        center_x = (left_x + right_x) / 2
        center_y = (left_y + right_y) / 2
        
        return (center_x, center_y), (left_x, left_y), (right_x, right_y)
    
    def process_frame(self, frame):
        global latest_data
        
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        result = self.detector.detect(mp_image)
        
        if not result.face_landmarks:
            cv2.putText(frame, "Face not detected", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame
        
        landmarks = result.face_landmarks[0]
        
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
        
        if 0.95 <= ratio <= 1.05:
            classification = "정상"
            color = (0, 255, 0)
        elif ratio < 0.95:
            classification = "평균 이하"
            color = (0, 0, 255)
        else:
            classification = "평균 이상"
            color = (255, 165, 0)
        
        # 전역 데이터 업데이트
        latest_data = {
            'pupil_to_mouth': round(pupil_to_mouth, 1),
            'nose_to_chin': round(nose_to_chin, 1),
            'ratio': round(ratio, 3),
            'classification': classification
        }
        
        # 시각화
        for pt in [pupil_center, mouth_center, nose_point, chin_point]:
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 5, (255, 255, 0), -1)
        
        cv2.line(frame, 
                (int(pupil_center[0]), int(pupil_center[1])),
                (int(mouth_center[0]), int(mouth_center[1])),
                (255, 0, 0), 3)
        
        cv2.line(frame,
                (int(nose_point[0]), int(nose_point[1])),
                (int(chin_point[0]), int(chin_point[1])),
                (0, 0, 255), 3)
        
        # 정보 표시
        y = 30
        cv2.putText(frame, f"Ratio: {ratio:.3f}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 30
        cv2.putText(frame, f"Status: {classification}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
    
    def generate_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            
            frame = self.process_frame(frame)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
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
    
    def analyze_profile_with_opencv(self, image):
        """OpenCV로 측면 얼굴 분석 (MediaPipe 실패 시)"""
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Haar Cascade로 얼굴 감지 (측면용)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 100))
        
        if len(faces) == 0:
            # 일반 얼굴 감지로 재시도
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(100, 100))
        
        if len(faces) == 0:
            return {'error': '얼굴을 찾을 수 없습니다 (OpenCV 측면 감지 실패)'}
        
        # 가장 큰 얼굴 선택
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        
        # 측면 얼굴 주요 랜드마크 추정 (간단한 휴리스틱)
        # 이마
        forehead = (x + fw // 2, y + fh // 4)
        # 코 끝 (얼굴 중앙, 중간 높이)
        nose_tip = (x + fw * 3 // 4, y + fh // 2)
        # 턱 끝 (아래)
        chin_bottom = (x + fw // 2, y + fh)
        # 입 (중간)
        mouth = (x + fw * 2 // 3, y + fh * 2 // 3)
        
        # 눈 위치 추정
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        roi_gray = gray[y:y+fh, x:x+fw]
        eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5)
        
        if len(eyes) > 0:
            ex, ey, ew, eh = eyes[0]
            eye_center = (x + ex + ew // 2, y + ey + eh // 2)
        else:
            eye_center = (x + fw // 2, y + fh // 3)
        
        # 거리 계산
        forehead_to_chin = self.calculate_distance(forehead, chin_bottom)
        nose_to_chin = self.calculate_distance(nose_tip, chin_bottom)
        eye_to_chin = self.calculate_distance(eye_center, chin_bottom)
        
        # 측면 Willis 비율 계산
        # 정면 Willis와 유사하게: (하안면) / (상안면)
        # 측면: (코끝-턱끝) / (눈-턱끝)
        if eye_to_chin > 0:
            lateral_willis_ratio = nose_to_chin / eye_to_chin
        else:
            lateral_willis_ratio = 0
        
        # 턱 각도 계산 (참고용)
        dx = chin_bottom[0] - nose_tip[0]
        dy = chin_bottom[1] - nose_tip[1]
        chin_angle = abs(np.degrees(np.arctan2(dy, dx)))
        
        # 측면 Willis 비율 평가 (정상 범위: 0.40-0.60)
        if 0.40 <= lateral_willis_ratio <= 0.60:
            profile_status = "측면 비율 정상 (자연스러운 윤곽)"
            naturalness = "정상"
        elif 0.35 <= lateral_willis_ratio < 0.40 or 0.60 < lateral_willis_ratio <= 0.65:
            profile_status = "측면 비율 경계 (경미한 불균형)"
            naturalness = "주의"
        elif lateral_willis_ratio > 0.65:
            profile_status = "측면 비율 높음 (턱이 긴 편)"
            naturalness = "평균 이하"
        else:
            profile_status = "측면 비율 낮음 (턱이 짧은 편)"
            naturalness = "평균 이하"
        
        return {
            'analysis_type': '측면 Willis 분석 (OpenCV 방법)',
            'lateral_ratio': round(lateral_willis_ratio, 3),
            'nose_to_chin': round(nose_to_chin, 1),
            'eye_to_chin': round(eye_to_chin, 1),
            'chin_angle': round(chin_angle, 1),
            'classification': profile_status,
            'naturalness': naturalness,
            'symmetry': 0,  # 측면이므로 대칭도 없음
            'is_frontal': False,
            'method': 'opencv'
        }
    
    def analyze_single_image(self, image):
        """단일 이미지 분석 (업로드용) - 정면/측면 자동 감지"""
        h, w = image.shape[:2]
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        result = self.detector.detect(mp_image)
        
        # MediaPipe로 얼굴을 못 찾으면 OpenCV 측면 분석 시도
        if not result.face_landmarks:
            return self.analyze_profile_with_opencv(image)
        
        landmarks = result.face_landmarks[0]
        
        # 대칭도 계산 (정면/측면 판단)
        symmetry = self.calculate_face_symmetry(landmarks, w, h)
        is_frontal = symmetry >= 0.85
        
        # Willis 계측 (공통)
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
            # 정면 분석: Willis 방법
            if 0.90 <= ratio <= 1.10:
                classification = "정상"
            elif ratio < 0.90:
                classification = "평균 이하 (수직고경 감소)"
            else:
                classification = "평균 이상 (수직고경 증가)"
            
            # 모든 MediaPipe 랜드마크 좌표 추가
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
            # 측면 분석: Profile 방법
            # 턱 각도 계산
            nose_tip = (landmarks[1].x * w, landmarks[1].y * h)
            chin_bottom = (landmarks[152].x * w, landmarks[152].y * h)
            
            # 수평선 기준 턱 각도
            dx = chin_bottom[0] - nose_tip[0]
            dy = chin_bottom[1] - nose_tip[1]
            angle = abs(np.degrees(np.arctan2(dy, dx)))
            
            # 턱 돌출도 (비저부-턱끝 거리의 비율)
            jaw_prominence = nose_to_chin / h * 100  # 이미지 높이 대비 비율
            
            # 측면 자연스러움 평가
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

# 전역 analyzer 인스턴스
analyzer = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(analyzer.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def get_data():
    return jsonify(latest_data)

@app.route('/pwa')
def pwa():
    return render_template('pwa.html')

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
        # 파일을 메모리에서 직접 읽기
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        # 이미지 분석
        result = analyzer.analyze_single_image(image)
        # 시각화 이미지 생성 (정면 분석일 때만)
        if result.get('is_frontal', False) and 'landmarks' in result:
            # 468개 랜드마크 복원
            all_landmarks = result.get('all_landmarks', [])
            for (x, y) in all_landmarks:
                cv2.circle(image, (x, y), 1, (180, 180, 180), -1)
            # 주요 포인트
            for key, color in zip(['pupil_center', 'mouth_center', 'nose_point', 'chin_point'],
                                  [(255,255,0), (255,255,0), (0,0,255), (0,0,255)]):
                pt = result['landmarks'][key]
                cv2.circle(image, tuple(pt), 7, color, -1)
            # 측정선
            cv2.line(image, tuple(result['landmarks']['pupil_center']), tuple(result['landmarks']['mouth_center']), (255,0,0), 3)
            cv2.line(image, tuple(result['landmarks']['nose_point']), tuple(result['landmarks']['chin_point']), (0,0,255), 3)
        # 이미지를 base64로 인코딩
        _, buffer = cv2.imencode('.jpg', image)
        img_b64 = b64encode(buffer).decode('utf-8')
        result['vis_image'] = img_b64
        return jsonify(result)
    except Exception as e:
        print(f"분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500

@app.route('/analyze_frame', methods=['POST'])
def analyze_frame():
    """클라이언트 카메라에서 캡처한 프레임 분석"""
    try:
        data = request.json
        if not data or 'frame' not in data:
            return jsonify({'error': '프레임 데이터가 없습니다'}), 400
        
        # Base64 이미지 디코딩
        import base64
        import re
        
        # data:image/jpeg;base64, 제거
        frame_data = re.sub('^data:image/.+;base64,', '', data['frame'])
        frame_bytes = base64.b64decode(frame_data)
        
        # NumPy 배열로 변환
        nparr = np.frombuffer(frame_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': '이미지를 읽을 수 없습니다'}), 400
        
        # 이미지 분석
        result = analyzer.analyze_single_image(image)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"프레임 분석 오류: {e}")
        return jsonify({'error': f'분석 중 오류 발생: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Willis 안면 계측법 - 웹 기반 실시간 버전")
    print("="*70)
    print("\n초기화 중...\n")
    
    analyzer = WillisWebAnalyzer()
    
    print("\n" + "="*70)
    print("✓ 서버 시작!")
    print("="*70)
    print("\n브라우저에서 열기:")
    print("  http://localhost:5001")
    print("\n종료: Ctrl+C")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

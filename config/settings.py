"""애플리케이션 설정"""
import os

# Flask 설정
DEBUG = False
HOST = '0.0.0.0'
PORT = 5001
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# MediaPipe 설정
MODEL_PATH = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# 얼굴 감지 임계값
MIN_DETECTION_CONFIDENCE = 0.1
MIN_PRESENCE_CONFIDENCE = 0.1
MIN_TRACKING_CONFIDENCE = 0.1

# 카메라 설정
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# 분석 임계값
FRONTAL_SYMMETRY_THRESHOLD = 0.85
WILLIS_RATIO_NORMAL_MIN = 0.90
WILLIS_RATIO_NORMAL_MAX = 1.10

# 측면 분석 임계값
JAW_PROMINENCE_MIN = 15
JAW_PROMINENCE_MAX = 25
CHIN_ANGLE_MIN = 70
CHIN_ANGLE_MAX = 110

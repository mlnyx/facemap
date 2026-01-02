"""얼굴 감지 및 랜드마크 추출"""
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request

from config import (
    MODEL_PATH, MODEL_URL,
    MIN_DETECTION_CONFIDENCE,
    MIN_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE
)


class FaceDetector:
    """MediaPipe 기반 얼굴 랜드마크 감지기"""
    
    def __init__(self):
        """MediaPipe FaceLandmarker 초기화"""
        self._download_model_if_needed()
        self.detector = self._create_detector()
    
    def _download_model_if_needed(self):
        """모델 파일이 없으면 다운로드"""
        if not os.path.exists(MODEL_PATH):
            print(f"모델 다운로드 중: {MODEL_URL}")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("✓ 모델 다운로드 완료")
    
    def _create_detector(self):
        """MediaPipe FaceLandmarker 생성"""
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_face_presence_confidence=MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        return vision.FaceLandmarker.create_from_options(options)
    
    def detect_landmarks(self, image):
        """
        이미지에서 얼굴 랜드마크 감지
        
        Args:
            image: OpenCV BGR 이미지
        
        Returns:
            list: 랜드마크 리스트 (468개 포인트) 또는 None (감지 실패 시)
        """
        rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        result = self.detector.detect(mp_image)
        
        if not result.face_landmarks:
            return None
        
        return result.face_landmarks[0]

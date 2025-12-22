#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
얼굴 랜드마크 감지 모듈
"""

import os
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat


class FaceLandmarker:
    """MediaPipe 얼굴 랜드마크 감지기"""
    
    # 주요 랜드마크 인덱스
    NOSE_TIP = 2
    CHIN = 152
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    LEFT_EYE = [33, 133, 160, 159, 158, 157, 173]
    RIGHT_EYE = [362, 263, 387, 386, 385, 384, 398]
    LEFT_FACE = 234
    RIGHT_FACE = 454
    
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    MODEL_FILE = "face_landmarker.task"
    
    def __init__(self, model_path: str = None):
        """
        초기화
        
        Args:
            model_path: 모델 파일 경로 (None이면 자동 다운로드)
        """
        self.model_path = model_path or self.MODEL_FILE
        self._download_model_if_needed()
        self.detector = self._create_detector()
    
    def _download_model_if_needed(self):
        """모델 파일이 없으면 자동 다운로드"""
        if not os.path.exists(self.model_path):
            print(f"📥 모델 다운로드 중... ({self.MODEL_FILE})")
            import urllib.request
            urllib.request.urlretrieve(self.MODEL_URL, self.model_path)
            print("✓ 다운로드 완료")
    
    def _create_detector(self):
        """감지기 생성"""
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        return vision.FaceLandmarker.create_from_options(options)
    
    def detect(self, image: np.ndarray):
        """
        얼굴 감지
        
        Args:
            image: BGR 이미지 (OpenCV format)
            
        Returns:
            MediaPipe detection result
        """
        import cv2
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        return self.detector.detect(mp_image)
    
    def get_landmarks(self, image: np.ndarray):
        """
        랜드마크 추출
        
        Args:
            image: BGR 이미지
            
        Returns:
            landmarks list or None
        """
        result = self.detect(image)
        if result.face_landmarks:
            return result.face_landmarks[0]
        return None

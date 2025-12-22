#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 안면 계측 분석 모듈
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class WillisClassification(Enum):
    """Willis 비율 분류"""
    NORMAL = "정상"
    BELOW_AVERAGE = "평균 이하 (수직고경 감소)"
    ABOVE_AVERAGE = "평균 이상 (수직고경 증가)"


@dataclass
class WillisResult:
    """Willis 측정 결과"""
    pupil_to_mouth_distance: float
    nose_to_chin_distance: float
    ratio: float
    classification: WillisClassification
    face_symmetry: float  # 0~1 (1이 완전 정면)
    
    @property
    def is_frontal(self) -> bool:
        """정면 사진 여부"""
        return self.face_symmetry >= 0.85
    
    @property
    def color_bgr(self) -> Tuple[int, int, int]:
        """분류별 색상 (BGR)"""
        colors = {
            WillisClassification.NORMAL: (80, 200, 120),
            WillisClassification.BELOW_AVERAGE: (80, 80, 255),
            WillisClassification.ABOVE_AVERAGE: (80, 165, 255)
        }
        return colors[self.classification]


class WillisAnalyzer:
    """Willis 안면 계측 분석기"""
    
    # Willis 비율 정상 범위
    NORMAL_RANGE = (0.90, 1.10)
    
    # 랜드마크 인덱스 (FaceLandmarker와 동일)
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
    
    @staticmethod
    def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """두 점 사이 유클리드 거리"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_pupil_center(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """양쪽 눈 중심점 계산"""
        left_x = np.mean([landmarks[i].x * width for i in self.LEFT_EYE])
        left_y = np.mean([landmarks[i].y * height for i in self.LEFT_EYE])
        right_x = np.mean([landmarks[i].x * width for i in self.RIGHT_EYE])
        right_y = np.mean([landmarks[i].y * height for i in self.RIGHT_EYE])
        return ((left_x + right_x) / 2, (left_y + right_y) / 2)
    
    def get_mouth_center(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """입 중심점 계산"""
        x = (landmarks[self.MOUTH_LEFT].x + landmarks[self.MOUTH_RIGHT].x) / 2 * width
        y = (landmarks[self.MOUTH_TOP].y + landmarks[self.MOUTH_BOTTOM].y) / 2 * height
        return (x, y)
    
    def calculate_symmetry(self, landmarks, width: int, height: int) -> float:
        """
        얼굴 대칭도 계산 (정면도 판단)
        
        Returns:
            0~1 사이 값 (1이 완전 정면)
        """
        left = (landmarks[self.LEFT_FACE].x * width, landmarks[self.LEFT_FACE].y * height)
        right = (landmarks[self.RIGHT_FACE].x * width, landmarks[self.RIGHT_FACE].y * height)
        nose = (landmarks[self.NOSE_TIP].x * width, landmarks[self.NOSE_TIP].y * height)
        
        face_center_x = (left[0] + right[0]) / 2
        deviation = abs(nose[0] - face_center_x)
        face_width = self.calculate_distance(left, right)
        
        return max(0.0, 1.0 - (deviation / (face_width / 2)))
    
    def classify_ratio(self, ratio: float) -> WillisClassification:
        """Willis 비율 분류"""
        min_normal, max_normal = self.NORMAL_RANGE
        
        if min_normal <= ratio <= max_normal:
            return WillisClassification.NORMAL
        elif ratio < min_normal:
            return WillisClassification.BELOW_AVERAGE
        else:
            return WillisClassification.ABOVE_AVERAGE
    
    def analyze(self, landmarks, width: int, height: int) -> WillisResult:
        """
        Willis 안면 계측 분석
        
        Args:
            landmarks: MediaPipe face landmarks
            width: 이미지 너비
            height: 이미지 높이
            
        Returns:
            WillisResult
        """
        # 대칭도 계산
        symmetry = self.calculate_symmetry(landmarks, width, height)
        
        # 주요 포인트 추출
        pupil = self.get_pupil_center(landmarks, width, height)
        mouth = self.get_mouth_center(landmarks, width, height)
        nose = (landmarks[self.NOSE_TIP].x * width, landmarks[self.NOSE_TIP].y * height)
        chin = (landmarks[self.CHIN].x * width, landmarks[self.CHIN].y * height)
        
        # 거리 계산
        pupil_to_mouth = self.calculate_distance(pupil, mouth)
        nose_to_chin = self.calculate_distance(nose, chin)
        
        # Willis 비율
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0.0
        
        # 분류
        classification = self.classify_ratio(ratio)
        
        return WillisResult(
            pupil_to_mouth_distance=pupil_to_mouth,
            nose_to_chin_distance=nose_to_chin,
            ratio=ratio,
            classification=classification,
            face_symmetry=symmetry
        )

"""Willis 계측 분석기"""
import numpy as np

from app.utils import calculate_distance, calculate_angle
from .landmarks import LandmarkExtractor
from config import (
    FRONTAL_SYMMETRY_THRESHOLD,
    WILLIS_RATIO_NORMAL_MIN,
    WILLIS_RATIO_NORMAL_MAX,
    JAW_PROMINENCE_MIN,
    JAW_PROMINENCE_MAX,
    CHIN_ANGLE_MIN,
    CHIN_ANGLE_MAX
)


class WillisAnalyzer:
    """Willis 방법 기반 수직 고경 분석"""
    
    def __init__(self):
        self.extractor = LandmarkExtractor()
    
    def analyze_frontal(self, landmarks, width, height):
        """
        정면 얼굴 Willis 분석
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            dict: 분석 결과
        """
        # 주요 포인트 추출
        pupil_center, left_pupil, right_pupil = self.extractor.get_pupil_centers(
            landmarks, width, height
        )
        mouth_center = self.extractor.get_mouth_center(landmarks, width, height)
        _, nose_point = self.extractor.get_nose_points(landmarks, width, height)
        chin_point = self.extractor.get_chin_point(landmarks, width, height)
        
        # 거리 계산
        pupil_to_mouth = calculate_distance(pupil_center, mouth_center)
        nose_to_chin = calculate_distance(nose_point, chin_point)
        
        # Willis 비율
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0
        
        # 분류
        if WILLIS_RATIO_NORMAL_MIN <= ratio <= WILLIS_RATIO_NORMAL_MAX:
            classification = "정상"
        elif ratio < WILLIS_RATIO_NORMAL_MIN:
            classification = "평균 이하 (수직고경 감소)"
        else:
            classification = "평균 이상 (수직고경 증가)"
        
        # 대칭도
        symmetry = self.extractor.calculate_eye_symmetry(landmarks, width, height)
        
        # 모든 랜드마크
        all_landmarks = self.extractor.get_all_landmarks_as_array(
            landmarks, width, height
        )
        
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
    
    def analyze_profile(self, landmarks, width, height):
        """
        측면 얼굴 프로필 분석
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            dict: 분석 결과
        """
        nose_tip, _ = self.extractor.get_nose_points(landmarks, width, height)
        chin_point = self.extractor.get_chin_point(landmarks, width, height)
        
        # 각도 계산
        angle = calculate_angle(nose_tip, chin_point)
        
        # 턱 돌출도
        nose_to_chin = calculate_distance(nose_tip, chin_point)
        jaw_prominence = nose_to_chin / height * 100
        
        # 평가
        if (JAW_PROMINENCE_MIN < jaw_prominence < JAW_PROMINENCE_MAX and 
            CHIN_ANGLE_MIN < angle < CHIN_ANGLE_MAX):
            profile_status = "자연스러운 측면 윤곽"
            naturalness = "양호"
        elif jaw_prominence >= JAW_PROMINENCE_MAX or angle >= CHIN_ANGLE_MAX:
            profile_status = "턱이 다소 길거나 각진 편"
            naturalness = "주의"
        else:
            profile_status = "턱이 다소 짧은 편"
            naturalness = "주의"
        
        # 대칭도
        symmetry = self.extractor.calculate_eye_symmetry(landmarks, width, height)
        
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
    
    def analyze(self, landmarks, width, height):
        """
        얼굴 분석 (정면/측면 자동 판단)
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            dict: 분석 결과
        """
        symmetry = self.extractor.calculate_eye_symmetry(landmarks, width, height)
        is_frontal = symmetry >= FRONTAL_SYMMETRY_THRESHOLD
        
        if is_frontal:
            return self.analyze_frontal(landmarks, width, height)
        else:
            return self.analyze_profile(landmarks, width, height)

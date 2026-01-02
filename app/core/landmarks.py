"""랜드마크 기반 특징점 추출"""
import numpy as np
from app.utils import calculate_distance


class LandmarkExtractor:
    """468개 랜드마크에서 주요 특징점 추출"""
    
    # MediaPipe 랜드마크 인덱스
    LEFT_EYE_INDICES = [33, 133, 160, 159, 158, 157, 173]
    RIGHT_EYE_INDICES = [362, 263, 387, 386, 385, 384, 398]
    MOUTH_INDICES = [61, 291, 13, 14]
    NOSE_TIP_INDEX = 1
    NOSE_BASE_INDEX = 2
    CHIN_INDEX = 152
    
    @classmethod
    def get_pupil_centers(cls, landmarks, width, height):
        """
        양쪽 눈동자 중심점 계산
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            tuple: (중앙점, 왼쪽 눈동자, 오른쪽 눈동자)
        """
        left_x = np.mean([landmarks[i].x * width for i in cls.LEFT_EYE_INDICES])
        left_y = np.mean([landmarks[i].y * height for i in cls.LEFT_EYE_INDICES])
        
        right_x = np.mean([landmarks[i].x * width for i in cls.RIGHT_EYE_INDICES])
        right_y = np.mean([landmarks[i].y * height for i in cls.RIGHT_EYE_INDICES])
        
        center_x = (left_x + right_x) / 2
        center_y = (left_y + right_y) / 2
        
        return (center_x, center_y), (left_x, left_y), (right_x, right_y)
    
    @classmethod
    def get_mouth_center(cls, landmarks, width, height):
        """
        입 중심점 계산
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            tuple: (x, y) 입 중심점
        """
        mouth_x = (landmarks[61].x + landmarks[291].x) / 2 * width
        mouth_y = (landmarks[13].y + landmarks[14].y) / 2 * height
        return (mouth_x, mouth_y)
    
    @classmethod
    def get_nose_points(cls, landmarks, width, height):
        """
        코 관련 포인트 추출
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            tuple: (코끝, 코 base)
        """
        nose_tip = (landmarks[cls.NOSE_TIP_INDEX].x * width, 
                    landmarks[cls.NOSE_TIP_INDEX].y * height)
        nose_base = (landmarks[cls.NOSE_BASE_INDEX].x * width,
                     landmarks[cls.NOSE_BASE_INDEX].y * height)
        return nose_tip, nose_base
    
    @classmethod
    def get_chin_point(cls, landmarks, width, height):
        """
        턱 끝점 추출
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            tuple: (x, y) 턱 끝점
        """
        return (landmarks[cls.CHIN_INDEX].x * width,
                landmarks[cls.CHIN_INDEX].y * height)
    
    @classmethod
    def calculate_eye_symmetry(cls, landmarks, width, height):
        """
        눈 크기 대칭도 계산 (정면/측면 판단용)
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            float: 대칭도 (0~1, 1이 완전 대칭)
        """
        left_eye_points = np.array([
            (landmarks[i].x * width, landmarks[i].y * height) 
            for i in cls.LEFT_EYE_INDICES
        ])
        right_eye_points = np.array([
            (landmarks[i].x * width, landmarks[i].y * height) 
            for i in cls.RIGHT_EYE_INDICES
        ])
        
        left_size = np.max(left_eye_points[:, 0]) - np.min(left_eye_points[:, 0])
        right_size = np.max(right_eye_points[:, 0]) - np.min(right_eye_points[:, 0])
        
        if max(left_size, right_size) == 0:
            return 0
        
        return min(left_size, right_size) / max(left_size, right_size)
    
    @classmethod
    def get_all_landmarks_as_array(cls, landmarks, width, height):
        """
        모든 랜드마크를 정수 좌표 배열로 변환
        
        Args:
            landmarks: MediaPipe 랜드마크 리스트
            width: 이미지 너비
            height: 이미지 높이
        
        Returns:
            list: [[x, y], ...] 형식의 468개 좌표
        """
        return [[int(lm.x * width), int(lm.y * height)] for lm in landmarks]

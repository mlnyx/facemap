"""랜드마크 시각화"""
import cv2


class LandmarkVisualizer:
    """얼굴 랜드마크 및 측정선 시각화"""
    
    # 색상 정의
    COLOR_LANDMARK = (180, 180, 180)  # 회색 (468개 점)
    COLOR_KEY_POINT = (255, 255, 0)   # 노란색 (눈동자, 입)
    COLOR_MEASUREMENT = (0, 0, 255)   # 빨간색 (코, 턱)
    COLOR_LINE_PUPIL = (255, 0, 0)    # 파란색 (눈동자-입 선)
    COLOR_LINE_NOSE = (0, 0, 255)     # 빨간색 (코-턱 선)
    
    LANDMARK_SIZE = 1
    KEY_POINT_SIZE = 7
    LINE_THICKNESS = 3
    
    @classmethod
    def draw_landmarks(cls, image, result):
        """
        이미지에 랜드마크 그리기
        
        Args:
            image: OpenCV 이미지
            result: analyze() 결과 딕셔너리
        
        Returns:
            numpy.ndarray: 랜드마크가 그려진 이미지
        """
        if not result.get('is_frontal') or 'landmarks' not in result:
            return image
        
        # 1. 468개 랜드마크 (작은 회색 점)
        all_landmarks = result.get('all_landmarks', [])
        for (x, y) in all_landmarks:
            cv2.circle(image, (x, y), cls.LANDMARK_SIZE, cls.COLOR_LANDMARK, -1)
        
        # 2. 주요 포인트 (큰 노란색/빨간색 점)
        key_points = [
            ('pupil_center', cls.COLOR_KEY_POINT),
            ('mouth_center', cls.COLOR_KEY_POINT),
            ('nose_point', cls.COLOR_MEASUREMENT),
            ('chin_point', cls.COLOR_MEASUREMENT)
        ]
        
        for key, color in key_points:
            pt = result['landmarks'][key]
            cv2.circle(image, tuple(pt), cls.KEY_POINT_SIZE, color, -1)
        
        # 3. 측정선
        cls._draw_measurement_lines(image, result['landmarks'])
        
        return image
    
    @classmethod
    def _draw_measurement_lines(cls, image, landmarks):
        """
        Willis 측정선 그리기
        
        Args:
            image: OpenCV 이미지
            landmarks: 주요 포인트 딕셔너리
        """
        # 눈동자 중심 - 입 중심 (파란색)
        cv2.line(
            image,
            tuple(landmarks['pupil_center']),
            tuple(landmarks['mouth_center']),
            cls.COLOR_LINE_PUPIL,
            cls.LINE_THICKNESS
        )
        
        # 코 - 턱 (빨간색)
        cv2.line(
            image,
            tuple(landmarks['nose_point']),
            tuple(landmarks['chin_point']),
            cls.COLOR_LINE_NOSE,
            cls.LINE_THICKNESS
        )

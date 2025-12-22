#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 안면 계측법 - 실시간 분석 (한글 지원 + 각도 보정)
"""

import cv2
import numpy as np
import os
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum
from PIL import Image as PILImage, ImageDraw, ImageFont

# MediaPipe 임포트
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat


class Classification(Enum):
    """Willis 비율 분류"""
    NORMAL = "정상"
    BELOW = "평균 이하 (수직고경 감소)"
    ABOVE = "평균 이상 (수직고경 증가)"


@dataclass
class WillisResult:
    """Willis 측정 결과"""
    pupil_to_mouth: float
    nose_to_chin: float
    ratio: float
    classification: Classification
    confidence: float  # 측정 신뢰도 (정면도에 가까울수록 높음)
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """BGR 색상"""
        if self.classification == Classification.NORMAL:
            return (80, 200, 120)  # 초록
        elif self.classification == Classification.BELOW:
            return (80, 80, 255)  # 빨강
        else:
            return (80, 165, 255)  # 주황


class FaceAnalyzer:
    """얼굴 분석기 (각도 보정 포함)"""
    
    NOSE_TIP = 2
    CHIN = 152
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    
    LEFT_EYE = [33, 133, 160, 159, 158, 157, 173]
    RIGHT_EYE = [362, 263, 387, 386, 385, 384, 398]
    
    # 얼굴 좌우 기준점 (대칭성 확인용)
    LEFT_FACE = 234
    RIGHT_FACE = 454
    
    # Willis 비율 범위 (더 관대하게 조정)
    NORMAL_MIN = 0.90
    NORMAL_MAX = 1.10
    
    def __init__(self):
        model_path = "face_landmarker.task"
        if not os.path.exists(model_path):
            print("모델 다운로드 중...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
    
    def detect(self, frame):
        """얼굴 감지"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        return self.detector.detect(mp_image)
    
    @staticmethod
    def distance(p1, p2):
        """거리 계산"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_face_symmetry(self, landmarks, w, h):
        """얼굴 대칭도 측정 (정면도 판단)"""
        left = (landmarks[self.LEFT_FACE].x * w, landmarks[self.LEFT_FACE].y * h)
        right = (landmarks[self.RIGHT_FACE].x * w, landmarks[self.RIGHT_FACE].y * h)
        nose = (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h)
        
        # 코끝이 얼굴 중앙에 가까울수록 정면
        face_center_x = (left[0] + right[0]) / 2
        deviation = abs(nose[0] - face_center_x)
        face_width = self.distance(left, right)
        
        # 0~1 사이 값 (1에 가까울수록 정면)
        symmetry = max(0, 1 - (deviation / (face_width / 2)))
        return symmetry
    
    def get_pupil_center(self, landmarks, w, h):
        """양쪽 동공 중심"""
        left_x = np.mean([landmarks[i].x * w for i in self.LEFT_EYE])
        left_y = np.mean([landmarks[i].y * h for i in self.LEFT_EYE])
        right_x = np.mean([landmarks[i].x * w for i in self.RIGHT_EYE])
        right_y = np.mean([landmarks[i].y * h for i in self.RIGHT_EYE])
        return ((left_x + right_x) / 2, (left_y + right_y) / 2)
    
    def get_mouth_center(self, landmarks, w, h):
        """입 중심"""
        x = (landmarks[self.MOUTH_LEFT].x + landmarks[self.MOUTH_RIGHT].x) / 2 * w
        y = (landmarks[self.MOUTH_TOP].y + landmarks[self.MOUTH_BOTTOM].y) / 2 * h
        return (x, y)
    
    def analyze(self, landmarks, w, h):
        """Willis 분석 (각도 보정)"""
        # 대칭도 측정
        symmetry = self.get_face_symmetry(landmarks, w, h)
        
        # 주요 포인트
        pupil = self.get_pupil_center(landmarks, w, h)
        mouth = self.get_mouth_center(landmarks, w, h)
        nose = (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h)
        chin = (landmarks[self.CHIN].x * w, landmarks[self.CHIN].y * h)
        
        # 거리 계산
        pupil_to_mouth = self.distance(pupil, mouth)
        nose_to_chin = self.distance(nose, chin)
        
        # Willis 비율
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0
        
        # 각도 보정: 비정면일 때는 판정을 보류하거나 경고
        if symmetry < 0.85:  # 정면이 아닐 때
            # 판정 유보 - 정상으로 표시하되 신뢰도 낮춤
            classification = Classification.NORMAL
            confidence = symmetry
        else:
            # 정면일 때만 정확한 판정
            if self.NORMAL_MIN <= ratio <= self.NORMAL_MAX:
                classification = Classification.NORMAL
            elif ratio < self.NORMAL_MIN:
                classification = Classification.BELOW
            else:
                classification = Classification.ABOVE
            confidence = symmetry
        
        return WillisResult(
            pupil_to_mouth=pupil_to_mouth,
            nose_to_chin=nose_to_chin,
            ratio=ratio,
            classification=classification,
            confidence=confidence
        )


class KoreanRenderer:
    """한글 렌더러 (PIL 사용)"""
    
    def __init__(self):
        # macOS 시스템 한글 폰트 경로
        font_paths = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/Arial Unicode.ttf"
        ]
        
        self.font_path = None
        for path in font_paths:
            if os.path.exists(path):
                self.font_path = path
                break
        
        if not self.font_path:
            print("⚠️  한글 폰트를 찾을 수 없습니다. 영문으로 표시됩니다.")
    
    def get_font(self, size):
        """폰트 가져오기"""
        if self.font_path:
            return ImageFont.truetype(self.font_path, size)
        return ImageFont.load_default()
    
    def cv2_to_pil(self, cv2_image):
        """OpenCV → PIL"""
        return PILImage.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    
    def pil_to_cv2(self, pil_image):
        """PIL → OpenCV"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def draw_text(self, cv2_image, text, position, font_size, color=(255, 255, 255)):
        """한글 텍스트 그리기"""
        pil_image = self.cv2_to_pil(cv2_image)
        draw = ImageDraw.Draw(pil_image)
        font = self.get_font(font_size)
        
        # PIL은 RGB, OpenCV는 BGR
        rgb_color = (color[2], color[1], color[0])
        draw.text(position, text, font=font, fill=rgb_color)
        
        return self.pil_to_cv2(pil_image)


class Visualizer:
    """시각화"""
    
    def __init__(self):
        self.analyzer = FaceAnalyzer()
        self.renderer = KoreanRenderer()
        
        # 색상
        self.WHITE = (255, 255, 255)
        self.GRAY = (180, 180, 180)
        self.BLACK = (0, 0, 0)
        self.BLUE = (255, 200, 100)
        self.RED = (100, 100, 255)
        self.YELLOW = (100, 255, 255)
    
    def draw_landmarks(self, frame, landmarks, w, h):
        """랜드마크 표시"""
        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 1, self.GRAY, -1)
    
    def draw_lines(self, frame, result, landmarks, w, h):
        """측정선"""
        pupil = self.analyzer.get_pupil_center(landmarks, w, h)
        mouth = self.analyzer.get_mouth_center(landmarks, w, h)
        nose = (landmarks[self.analyzer.NOSE_TIP].x * w, 
                landmarks[self.analyzer.NOSE_TIP].y * h)
        chin = (landmarks[self.analyzer.CHIN].x * w, 
                landmarks[self.analyzer.CHIN].y * h)
        
        # 파란선 (동공-입)
        cv2.line(frame, (int(pupil[0]), int(pupil[1])),
                (int(mouth[0]), int(mouth[1])), self.BLUE, 3)
        
        # 빨간선 (비저부-턱끝)
        cv2.line(frame, (int(nose[0]), int(nose[1])),
                (int(chin[0]), int(chin[1])), self.RED, 3)
        
        # 포인트
        for pt in [pupil, mouth, nose, chin]:
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 6, self.WHITE, -1)
            cv2.circle(frame, (int(pt[0]), int(pt[1])), 7, self.BLACK, 2)
    
    def draw_info(self, frame, result, w, h):
        """정보 패널 (한글)"""
        # 반투명 배경
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 200), self.BLACK, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        
        # 한글 텍스트
        frame = self.renderer.draw_text(frame, "Willis 안면 계측법", (20, 10), 32, self.WHITE)
        
        frame = self.renderer.draw_text(
            frame, 
            f"동공-구열 거리: {result.pupil_to_mouth:.1f}px", 
            (20, 55), 24, self.BLUE
        )
        
        frame = self.renderer.draw_text(
            frame, 
            f"비저부-턱끝 거리: {result.nose_to_chin:.1f}px", 
            (20, 90), 24, self.RED
        )
        
        frame = self.renderer.draw_text(
            frame, 
            f"Willis 비율: {result.ratio:.3f}", 
            (20, 125), 24, self.WHITE
        )
        
        frame = self.renderer.draw_text(
            frame, 
            "(정상 범위: 0.90 ~ 1.10)", 
            (20, 160), 18, self.GRAY
        )
        
        return frame
    
    def draw_result(self, frame, result, w, h):
        """판정 결과 (한글)"""
        text = f"판정: {result.classification.value}"
        
        # 배경 박스
        x = w - 280
        cv2.rectangle(frame, (x, 20), (w - 20, 75), result.color, -1)
        cv2.rectangle(frame, (x, 20), (w - 20, 75), self.WHITE, 3)
        
        # 신뢰도가 낮으면 경고
        if result.confidence < 0.85:
            frame = self.renderer.draw_text(frame, "⚠️ 정면을 보세요", (x + 10, 25), 22, self.YELLOW)
        else:
            frame = self.renderer.draw_text(frame, text, (x + 10, 30), 24, self.WHITE)
        
        return frame
    
    def draw_footer(self, frame, h, w):
        """하단"""
        frame = self.renderer.draw_text(
            frame,
            "파란선: 동공-구열 | 빨간선: 비저부-턱끝 | ESC/Q: 종료",
            (w // 2 - 250, h - 30),
            18,
            self.WHITE
        )
        return frame
    
    def process(self, frame):
        """프레임 처리"""
        h, w = frame.shape[:2]
        result = self.analyzer.detect(frame)
        
        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            
            # 랜드마크
            self.draw_landmarks(frame, landmarks, w, h)
            
            # 분석
            willis = self.analyzer.analyze(landmarks, w, h)
            
            # 측정선
            self.draw_lines(frame, willis, landmarks, w, h)
            
            # 정보
            frame = self.draw_info(frame, willis, w, h)
            
            # 판정
            frame = self.draw_result(frame, willis, w, h)
            
            # 하단
            frame = self.draw_footer(frame, h, w)
        else:
            frame = self.renderer.draw_text(frame, "얼굴을 카메라에 대주세요", (50, 50), 28, self.RED)
        
        return frame


def main():
    print("=" * 60)
    print("Willis 안면 계측법 - 실시간 분석")
    print("=" * 60)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    vis = Visualizer()
    window = 'Willis 안면 계측법'
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    
    print("\n✓ 준비 완료! (ESC 또는 Q로 종료)\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = vis.process(frame)
            cv2.imshow(window, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key in [ord('q'), ord('Q')]:
                break
    
    except KeyboardInterrupt:
        print("\n중단됨")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("종료")


if __name__ == "__main__":
    main()

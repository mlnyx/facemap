#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
측면 얼굴 분석 - 턱관절 위치(CR) 파악
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

from src.core import FaceLandmarker
from src.utils import KoreanTextRenderer


@dataclass
class ProfileAnalysisResult:
    """측면 분석 결과"""
    chin_movement: float  # 턱끝 이동 거리 (픽셀)
    chin_angle_change: float  # 턱 각도 변화 (도)
    naturalness_score: float  # 자연스러움 점수 (0~100)
    is_acceptable: bool  # 허용 가능한 변화인지
    
    @property
    def status(self) -> str:
        """판정"""
        if self.is_acceptable:
            return "적절한 턱관절 위치"
        else:
            return "과도한 턱 위치 변화"
    
    @property
    def color_bgr(self) -> Tuple[int, int, int]:
        """상태별 색상"""
        return (80, 200, 120) if self.is_acceptable else (80, 80, 255)


class ProfileAnalyzer:
    """측면 얼굴 분석기"""
    
    # 주요 랜드마크 인덱스
    CHIN = 152  # 턱끝 (Pogonion)
    NOSE_TIP = 2  # 코끝 (Pronasale)
    UPPER_LIP = 13  # 윗입술
    LOWER_LIP = 14  # 아랫입술
    FOREHEAD = 10  # 이마
    
    # 하악각 측정용
    GONION = 172  # 하악각
    
    # 허용 가능한 턱 이동 거리 (픽셀)
    MAX_ACCEPTABLE_MOVEMENT = 30  # 약 3cm (이미지 해상도에 따라 조정)
    
    def __init__(self):
        """초기화"""
        self.landmarker = FaceLandmarker()
        self.renderer = KoreanTextRenderer()
    
    def get_chin_position(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """턱끝 위치"""
        return (
            landmarks[self.CHIN].x * width,
            landmarks[self.CHIN].y * height
        )
    
    def get_nose_position(self, landmarks, width: int, height: int) -> Tuple[float, float]:
        """코끝 위치"""
        return (
            landmarks[self.NOSE_TIP].x * width,
            landmarks[self.NOSE_TIP].y * height
        )
    
    def calculate_facial_angle(self, landmarks, width: int, height: int) -> float:
        """
        안면각 계산 (Facial Angle)
        코끝-턱끝 라인과 수직선의 각도
        """
        nose = self.get_nose_position(landmarks, width, height)
        chin = self.get_chin_position(landmarks, width, height)
        
        # 각도 계산 (라디안 → 도)
        dx = chin[0] - nose[0]
        dy = chin[1] - nose[1]
        angle = np.degrees(np.arctan2(dy, dx))
        
        return angle
    
    def calculate_movement(
        self,
        before_pos: Tuple[float, float],
        after_pos: Tuple[float, float]
    ) -> float:
        """두 위치 사이 이동 거리"""
        return np.sqrt(
            (after_pos[0] - before_pos[0])**2 +
            (after_pos[1] - before_pos[1])**2
        )
    
    def calculate_naturalness_score(
        self,
        movement: float,
        angle_change: float
    ) -> float:
        """
        자연스러움 점수 계산 (0~100)
        - 이동 거리가 작을수록 높은 점수
        - 각도 변화가 작을수록 높은 점수
        """
        # 이동 점수 (0~50)
        movement_score = max(0, 50 - (movement / self.MAX_ACCEPTABLE_MOVEMENT * 50))
        
        # 각도 점수 (0~50)
        angle_score = max(0, 50 - abs(angle_change))
        
        return movement_score + angle_score
    
    def analyze_profile_change(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray
    ) -> Optional[ProfileAnalysisResult]:
        """
        측면 사진 2장 비교 분석
        
        Args:
            before_image: 의치 없는 측면 사진
            after_image: 의치 낀 측면 사진
            
        Returns:
            ProfileAnalysisResult or None
        """
        # 이미지 크기
        h1, w1 = before_image.shape[:2]
        h2, w2 = after_image.shape[:2]
        
        # 얼굴 감지
        before_landmarks = self.landmarker.get_landmarks(before_image)
        after_landmarks = self.landmarker.get_landmarks(after_image)
        
        if not before_landmarks or not after_landmarks:
            return None
        
        # Before 분석
        before_chin = self.get_chin_position(before_landmarks, w1, h1)
        before_angle = self.calculate_facial_angle(before_landmarks, w1, h1)
        
        # After 분석
        after_chin = self.get_chin_position(after_landmarks, w2, h2)
        after_angle = self.calculate_facial_angle(after_landmarks, w2, h2)
        
        # 변화량 계산
        # 주의: 이미지 크기가 다를 수 있으므로 정규화 필요
        scale_factor = w1 / w2
        after_chin_scaled = (after_chin[0] * scale_factor, after_chin[1] * scale_factor)
        
        movement = self.calculate_movement(before_chin, after_chin_scaled)
        angle_change = after_angle - before_angle
        
        # 자연스러움 점수
        naturalness = self.calculate_naturalness_score(movement, angle_change)
        
        # 판정
        is_acceptable = movement < self.MAX_ACCEPTABLE_MOVEMENT
        
        return ProfileAnalysisResult(
            chin_movement=movement,
            chin_angle_change=angle_change,
            naturalness_score=naturalness,
            is_acceptable=is_acceptable
        )


class ProfileVisualizer:
    """측면 분석 시각화"""
    
    COLOR_WHITE = (255, 255, 255)
    COLOR_GRAY = (180, 180, 180)
    COLOR_BLACK = (0, 0, 0)
    COLOR_BLUE = (255, 200, 100)
    COLOR_RED = (100, 100, 255)
    COLOR_GREEN = (100, 255, 100)
    
    def __init__(self):
        """초기화"""
        self.renderer = KoreanTextRenderer()
        self.analyzer = ProfileAnalyzer()
    
    def draw_profile_landmarks(
        self,
        image: np.ndarray,
        landmarks,
        width: int,
        height: int
    ):
        """측면 주요 랜드마크 표시"""
        # 턱끝
        chin = self.analyzer.get_chin_position(landmarks, width, height)
        cv2.circle(image, (int(chin[0]), int(chin[1])), 8, self.COLOR_RED, -1)
        
        # 코끝
        nose = self.analyzer.get_nose_position(landmarks, width, height)
        cv2.circle(image, (int(nose[0]), int(nose[1])), 8, self.COLOR_BLUE, -1)
        
        # E-line 그리기
        cv2.line(
            image,
            (int(nose[0]), int(nose[1])),
            (int(chin[0]), int(chin[1])),
            self.COLOR_GREEN,
            2
        )
    
    def create_comparison_view(
        self,
        before_image: np.ndarray,
        after_image: np.ndarray,
        result: ProfileAnalysisResult
    ) -> np.ndarray:
        """비교 뷰 생성"""
        # 이미지 크기 조정 (같은 높이로)
        h1, w1 = before_image.shape[:2]
        h2, w2 = after_image.shape[:2]
        
        target_height = 600
        before_resized = cv2.resize(before_image, (int(w1 * target_height / h1), target_height))
        after_resized = cv2.resize(after_image, (int(w2 * target_height / h2), target_height))
        
        # 좌우로 합치기
        combined = np.hstack([before_resized, after_resized])
        h, w = combined.shape[:2]
        
        # 정보 패널
        panel_height = 200
        overlay = combined.copy()
        cv2.rectangle(overlay, (0, 0), (w, panel_height), self.COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.75, combined, 0.25, 0, combined)
        
        # 텍스트
        combined = self.renderer.draw_text(combined, "측면 분석 - 턱관절 위치(CR) 파악", (20, 20), 32, self.COLOR_WHITE)
        combined = self.renderer.draw_text(combined, "Before (의치 없음)", (20, 70), 24, self.COLOR_BLUE)
        combined = self.renderer.draw_text(combined, "After (의치 착용)", (w//2 + 20, 70), 24, self.COLOR_RED)
        
        combined = self.renderer.draw_text(
            combined,
            f"턱 이동 거리: {result.chin_movement:.1f}px",
            (20, 110), 22, self.COLOR_WHITE
        )
        combined = self.renderer.draw_text(
            combined,
            f"각도 변화: {result.chin_angle_change:.1f}°",
            (20, 140), 22, self.COLOR_WHITE
        )
        combined = self.renderer.draw_text(
            combined,
            f"자연스러움: {result.naturalness_score:.0f}/100",
            (20, 170), 22, self.COLOR_WHITE
        )
        
        # 판정
        x = w - 350
        cv2.rectangle(combined, (x, 20), (w - 20, 80), result.color_bgr, -1)
        cv2.rectangle(combined, (x, 20), (w - 20, 80), self.COLOR_WHITE, 3)
        combined = self.renderer.draw_text(combined, f"판정: {result.status}", (x + 15, 40), 24, self.COLOR_WHITE)
        
        return combined


def analyze_profile_photos(before_path: str, after_path: str):
    """
    측면 사진 2장 분석
    
    Args:
        before_path: 의치 없는 측면 사진
        after_path: 의치 낀 측면 사진
    """
    print("=" * 60)
    print("측면 분석 - 턱관절 위치(CR) 파악")
    print("=" * 60)
    
    # 이미지 로드
    before_img = cv2.imread(before_path)
    after_img = cv2.imread(after_path)
    
    if before_img is None or after_img is None:
        print("❌ 이미지를 읽을 수 없습니다")
        return
    
    # 분석
    analyzer = ProfileAnalyzer()
    result = analyzer.analyze_profile_change(before_img, after_img)
    
    if result is None:
        print("❌ 얼굴을 감지할 수 없습니다")
        return
    
    # 결과 출력
    print("\n📊 분석 결과:")
    print("=" * 60)
    print(f"턱 이동 거리: {result.chin_movement:.1f}px")
    print(f"각도 변화: {result.chin_angle_change:.1f}°")
    print(f"자연스러움 점수: {result.naturalness_score:.0f}/100")
    print(f"판정: {result.status}")
    print("=" * 60)
    
    # 시각화
    visualizer = ProfileVisualizer()
    comparison = visualizer.create_comparison_view(before_img, after_img, result)
    
    # 저장
    output_path = "data/output/profile_comparison.jpg"
    cv2.imwrite(output_path, comparison)
    print(f"\n✅ 결과 저장: {output_path}")
    
    # 화면 표시
    cv2.namedWindow('측면 분석 결과', cv2.WINDOW_NORMAL)
    cv2.imshow('측면 분석 결과', comparison)
    print("\n아무 키나 누르면 종료...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("\n사용법:")
        print("  python willis_profile.py <before.jpg> <after.jpg>")
        print("\n예시:")
        print("  python willis_profile.py data/input/구의치옆.jpeg data/input/신의치옆.jpeg")
        sys.exit(1)
    
    analyze_profile_photos(sys.argv[1], sys.argv[2])

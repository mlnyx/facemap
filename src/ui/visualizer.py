#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시각화 모듈
"""

import cv2
import numpy as np
from typing import Tuple

from ..core.analyzer import WillisResult, WillisAnalyzer
from ..utils.text_renderer import KoreanTextRenderer


class WillisVisualizer:
    """Willis 분석 결과 시각화"""
    
    # 색상 상수 (BGR)
    COLOR_WHITE = (255, 255, 255)
    COLOR_GRAY = (180, 180, 180)
    COLOR_BLACK = (0, 0, 0)
    COLOR_BLUE = (255, 200, 100)
    COLOR_RED = (100, 100, 255)
    COLOR_YELLOW = (100, 255, 255)
    
    def __init__(self):
        """초기화"""
        self.renderer = KoreanTextRenderer()
        self.analyzer = WillisAnalyzer()
    
    def draw_all_landmarks(
        self,
        image: np.ndarray,
        landmarks,
        width: int,
        height: int
    ):
        """468개 전체 랜드마크 표시"""
        for landmark in landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(image, (x, y), 1, self.COLOR_GRAY, -1)
    
    def draw_measurement_lines(
        self,
        image: np.ndarray,
        landmarks,
        width: int,
        height: int
    ):
        """측정선 및 주요 포인트 표시"""
        # 주요 포인트 계산
        pupil = self.analyzer.get_pupil_center(landmarks, width, height)
        mouth = self.analyzer.get_mouth_center(landmarks, width, height)
        nose = (
            landmarks[self.analyzer.NOSE_TIP].x * width,
            landmarks[self.analyzer.NOSE_TIP].y * height
        )
        chin = (
            landmarks[self.analyzer.CHIN].x * width,
            landmarks[self.analyzer.CHIN].y * height
        )
        
        # 측정선 그리기
        # 동공-입 (파란선)
        cv2.line(
            image,
            (int(pupil[0]), int(pupil[1])),
            (int(mouth[0]), int(mouth[1])),
            self.COLOR_BLUE,
            3
        )
        
        # 비저부-턱끝 (빨간선)
        cv2.line(
            image,
            (int(nose[0]), int(nose[1])),
            (int(chin[0]), int(chin[1])),
            self.COLOR_RED,
            3
        )
        
        # 주요 포인트 강조
        for point in [pupil, mouth, nose, chin]:
            cv2.circle(image, (int(point[0]), int(point[1])), 6, self.COLOR_WHITE, -1)
            cv2.circle(image, (int(point[0]), int(point[1])), 7, self.COLOR_BLACK, 2)
    
    def draw_info_panel(
        self,
        image: np.ndarray,
        result: WillisResult,
        width: int
    ) -> np.ndarray:
        """정보 패널 그리기"""
        panel_height = 200
        
        # 반투명 배경
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, panel_height), self.COLOR_BLACK, -1)
        cv2.addWeighted(overlay, 0.75, image, 0.25, 0, image)
        
        # 텍스트 렌더링
        image = self.renderer.draw_text(image, "Willis 안면 계측법", (20, 10), 32, self.COLOR_WHITE)
        image = self.renderer.draw_text(
            image,
            f"동공-구열 거리: {result.pupil_to_mouth_distance:.1f}px",
            (20, 55), 24, self.COLOR_BLUE
        )
        image = self.renderer.draw_text(
            image,
            f"비저부-턱끝 거리: {result.nose_to_chin_distance:.1f}px",
            (20, 90), 24, self.COLOR_RED
        )
        image = self.renderer.draw_text(
            image,
            f"Willis 비율: {result.ratio:.3f}",
            (20, 125), 24, self.COLOR_WHITE
        )
        image = self.renderer.draw_text(
            image,
            f"(정상 범위: {WillisAnalyzer.NORMAL_RANGE[0]:.2f} ~ {WillisAnalyzer.NORMAL_RANGE[1]:.2f})",
            (20, 160), 18, self.COLOR_GRAY
        )
        
        return image
    
    def draw_classification(
        self,
        image: np.ndarray,
        result: WillisResult,
        width: int
    ) -> np.ndarray:
        """판정 결과 표시"""
        # 텍스트
        if not result.is_frontal:
            text = "⚠️ 정면을 보세요"
            color = self.COLOR_YELLOW
        else:
            text = f"판정: {result.classification.value}"
            color = result.color_bgr
        
        # 배경 박스
        box_x = width - 350
        cv2.rectangle(image, (box_x, 20), (width - 20, 80), color, -1)
        cv2.rectangle(image, (box_x, 20), (width - 20, 80), self.COLOR_WHITE, 3)
        
        # 텍스트
        image = self.renderer.draw_text(image, text, (box_x + 15, 35), 24, self.COLOR_WHITE)
        
        return image
    
    def draw_footer(
        self,
        image: np.ndarray,
        height: int,
        width: int
    ) -> np.ndarray:
        """하단 설명"""
        text = f"대칭도: {0:.1%} | 파란선: 동공-구열 | 빨간선: 비저부-턱끝 | ESC/Q: 종료"
        image = self.renderer.draw_text(image, text, (20, height - 40), 18, self.COLOR_WHITE)
        return image
    
    def visualize(
        self,
        image: np.ndarray,
        landmarks,
        result: WillisResult
    ) -> np.ndarray:
        """
        전체 시각화
        
        Args:
            image: 원본 이미지
            landmarks: 얼굴 랜드마크
            result: Willis 분석 결과
            
        Returns:
            시각화된 이미지
        """
        height, width = image.shape[:2]
        
        # 모든 랜드마크 표시
        self.draw_all_landmarks(image, landmarks, width, height)
        
        # 측정선
        self.draw_measurement_lines(image, landmarks, width, height)
        
        # 정보 패널
        image = self.draw_info_panel(image, result, width)
        
        # 판정 결과
        image = self.draw_classification(image, result, width)
        
        # 하단 정보
        image = self.draw_footer(image, height, width)
        
        return image

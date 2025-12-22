#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
한글 렌더링 유틸리티
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple


class KoreanTextRenderer:
    """한글 텍스트 렌더러 (PIL 기반)"""
    
    # macOS 시스템 폰트 경로
    FONT_PATHS = [
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    
    def __init__(self):
        """초기화"""
        self.font_path = self._find_korean_font()
        if not self.font_path:
            print("⚠️  한글 폰트를 찾을 수 없습니다")
    
    def _find_korean_font(self) -> str:
        """시스템에서 한글 폰트 찾기"""
        for path in self.FONT_PATHS:
            if os.path.exists(path):
                return path
        return None
    
    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """폰트 객체 가져오기"""
        if self.font_path:
            return ImageFont.truetype(self.font_path, size)
        return ImageFont.load_default()
    
    @staticmethod
    def cv2_to_pil(cv2_image: np.ndarray) -> Image:
        """OpenCV BGR → PIL RGB"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    
    @staticmethod
    def pil_to_cv2(pil_image: Image) -> np.ndarray:
        """PIL RGB → OpenCV BGR"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def draw_text(
        self,
        image: np.ndarray,
        text: str,
        position: Tuple[int, int],
        font_size: int,
        color: Tuple[int, int, int] = (255, 255, 255)
    ) -> np.ndarray:
        """
        OpenCV 이미지에 한글 텍스트 그리기
        
        Args:
            image: BGR 이미지
            text: 표시할 텍스트
            position: (x, y) 좌표
            font_size: 폰트 크기
            color: BGR 색상
            
        Returns:
            텍스트가 그려진 이미지
        """
        pil_image = self.cv2_to_pil(image)
        draw = ImageDraw.Draw(pil_image)
        font = self.get_font(font_size)
        
        # BGR → RGB
        rgb_color = (color[2], color[1], color[0])
        draw.text(position, text, font=font, fill=rgb_color)
        
        return self.pil_to_cv2(pil_image)

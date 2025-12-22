#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 안면 계측법 - 사진 분석 버전
"""

import cv2
import numpy as np
import os
import sys
from PIL import Image as PILImage, ImageDraw, ImageFont

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import Image, ImageFormat


class PhotoAnalyzer:
    """사진 분석기"""
    
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
    
    NORMAL_MIN = 0.90
    NORMAL_MAX = 1.10
    
    def __init__(self):
        model_path = "face_landmarker.task"
        if not os.path.exists(model_path):
            print("📥 모델 다운로드 중...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.3
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # 한글 폰트
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
    
    def detect(self, image):
        """얼굴 감지"""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        return self.detector.detect(mp_image)
    
    @staticmethod
    def distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_symmetry(self, landmarks, w, h):
        """대칭도"""
        left = (landmarks[self.LEFT_FACE].x * w, landmarks[self.LEFT_FACE].y * h)
        right = (landmarks[self.RIGHT_FACE].x * w, landmarks[self.RIGHT_FACE].y * h)
        nose = (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h)
        
        face_center = (left[0] + right[0]) / 2
        deviation = abs(nose[0] - face_center)
        face_width = self.distance(left, right)
        return max(0, 1 - (deviation / (face_width / 2)))
    
    def get_pupil(self, landmarks, w, h):
        """동공 중심"""
        left_x = np.mean([landmarks[i].x * w for i in self.LEFT_EYE])
        left_y = np.mean([landmarks[i].y * h for i in self.LEFT_EYE])
        right_x = np.mean([landmarks[i].x * w for i in self.RIGHT_EYE])
        right_y = np.mean([landmarks[i].y * h for i in self.RIGHT_EYE])
        return ((left_x + right_x) / 2, (left_y + right_y) / 2)
    
    def get_mouth(self, landmarks, w, h):
        """입 중심"""
        x = (landmarks[self.MOUTH_LEFT].x + landmarks[self.MOUTH_RIGHT].x) / 2 * w
        y = (landmarks[self.MOUTH_TOP].y + landmarks[self.MOUTH_BOTTOM].y) / 2 * h
        return (x, y)
    
    def draw_korean(self, image, text, pos, size, color):
        """한글 그리기"""
        pil_img = PILImage.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        if self.font_path:
            font = ImageFont.truetype(self.font_path, size)
        else:
            font = ImageFont.load_default()
        
        rgb_color = (color[2], color[1], color[0])
        draw.text(pos, text, font=font, fill=rgb_color)
        
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    def analyze_photo(self, image_path):
        """사진 분석"""
        print(f"\n📷 사진 분석 중: {image_path}")
        
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print("❌ 이미지를 읽을 수 없습니다")
            return None
        
        h, w = image.shape[:2]
        result = self.detect(image)
        
        if not result.face_landmarks:
            print("❌ 얼굴을 찾을 수 없습니다")
            return None
        
        landmarks = result.face_landmarks[0]
        
        # 랜드마크 표시
        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(image, (x, y), 2, (180, 180, 180), -1)
        
        # 대칭도
        symmetry = self.get_symmetry(landmarks, w, h)
        
        # 주요 포인트
        pupil = self.get_pupil(landmarks, w, h)
        mouth = self.get_mouth(landmarks, w, h)
        nose = (landmarks[self.NOSE_TIP].x * w, landmarks[self.NOSE_TIP].y * h)
        chin = (landmarks[self.CHIN].x * w, landmarks[self.CHIN].y * h)
        
        # 거리 계산
        pupil_to_mouth = self.distance(pupil, mouth)
        nose_to_chin = self.distance(nose, chin)
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0
        
        # 판정
        if symmetry < 0.85:
            classification = "⚠️ 정면이 아님"
            color = (100, 255, 255)
        elif self.NORMAL_MIN <= ratio <= self.NORMAL_MAX:
            classification = "정상"
            color = (80, 200, 120)
        elif ratio < self.NORMAL_MIN:
            classification = "평균 이하 (수직고경 감소)"
            color = (80, 80, 255)
        else:
            classification = "평균 이상 (수직고경 증가)"
            color = (80, 165, 255)
        
        # 측정선 그리기
        cv2.line(image, (int(pupil[0]), int(pupil[1])),
                (int(mouth[0]), int(mouth[1])), (255, 200, 100), 4)
        cv2.line(image, (int(nose[0]), int(nose[1])),
                (int(chin[0]), int(chin[1])), (100, 100, 255), 4)
        
        # 포인트
        for pt in [pupil, mouth, nose, chin]:
            cv2.circle(image, (int(pt[0]), int(pt[1])), 8, (255, 255, 255), -1)
            cv2.circle(image, (int(pt[0]), int(pt[1])), 9, (0, 0, 0), 2)
        
        # 정보 패널
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, 220), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.75, image, 0.25, 0, image)
        
        image = self.draw_korean(image, "Willis 안면 계측법 분석 결과", (20, 10), 36, (255, 255, 255))
        image = self.draw_korean(image, f"동공-구열 거리: {pupil_to_mouth:.1f}px", (20, 60), 26, (255, 200, 100))
        image = self.draw_korean(image, f"비저부-턱끝 거리: {nose_to_chin:.1f}px", (20, 100), 26, (100, 100, 255))
        image = self.draw_korean(image, f"Willis 비율: {ratio:.3f}", (20, 140), 26, (255, 255, 255))
        image = self.draw_korean(image, "(정상 범위: 0.90 ~ 1.10)", (20, 180), 20, (180, 180, 180))
        
        # 판정 결과
        x = w - 400
        cv2.rectangle(image, (x, 20), (w - 20, 90), color, -1)
        cv2.rectangle(image, (x, 20), (w - 20, 90), (255, 255, 255), 4)
        image = self.draw_korean(image, f"판정: {classification}", (x + 15, 35), 28, (255, 255, 255))
        
        # 하단 정보
        image = self.draw_korean(image, f"대칭도: {symmetry:.1%} | 파란선: 동공-구열 | 빨간선: 비저부-턱끝", 
                                (20, h - 40), 20, (255, 255, 255))
        
        # 결과 출력
        print("=" * 60)
        print(f"동공-구열 거리: {pupil_to_mouth:.1f}px")
        print(f"비저부-턱끝 거리: {nose_to_chin:.1f}px")
        print(f"Willis 비율: {ratio:.3f}")
        print(f"대칭도: {symmetry:.1%}")
        print(f"판정: {classification}")
        print("=" * 60)
        
        # 저장
        output_path = image_path.rsplit('.', 1)[0] + '_willis_분석.jpg'
        cv2.imwrite(output_path, image)
        print(f"✅ 결과 저장됨: {output_path}")
        
        # 화면 표시
        cv2.namedWindow('Willis 분석 결과', cv2.WINDOW_NORMAL)
        cv2.imshow('Willis 분석 결과', image)
        print("\n아무 키나 누르면 종료됩니다...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return image


def main():
    print("=" * 60)
    print("Willis 안면 계측법 - 사진 분석")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n사용법:")
        print("  python willis_photo.py <이미지_파일>")
        print("\n예시:")
        print("  python willis_photo.py photo.jpg")
        print("  python willis_photo.py /Users/name/Desktop/face.png")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return
    
    analyzer = PhotoAnalyzer()
    analyzer.analyze_photo(image_path)


if __name__ == "__main__":
    main()

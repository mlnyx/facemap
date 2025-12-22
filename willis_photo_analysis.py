#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 안면 계측법 - 사진 분석
"""

import cv2
import sys
import os

from src.core import FaceLandmarker, WillisAnalyzer
from src.ui import WillisVisualizer


def analyze_photo(image_path: str) -> int:
    """
    사진 파일 분석
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        종료 코드 (0=성공, 1=실패)
    """
    # 파일 존재 확인
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return 1
    
    print(f"\n📷 사진 분석 중: {image_path}")
    
    # 이미지 로드
    image = cv2.imread(image_path)
    if image is None:
        print("❌ 이미지를 읽을 수 없습니다")
        return 1
    
    height, width = image.shape[:2]
    
    # 초기화
    landmarker = FaceLandmarker()
    analyzer = WillisAnalyzer()
    visualizer = WillisVisualizer()
    
    # 얼굴 감지
    landmarks = landmarker.get_landmarks(image)
    if not landmarks:
        print("❌ 얼굴을 찾을 수 없습니다")
        return 1
    
    # Willis 분석
    result = analyzer.analyze(landmarks, width, height)
    
    # 결과 출력
    print("=" * 60)
    print(f"동공-구열 거리: {result.pupil_to_mouth_distance:.1f}px")
    print(f"비저부-턱끝 거리: {result.nose_to_chin_distance:.1f}px")
    print(f"Willis 비율: {result.ratio:.3f}")
    print(f"대칭도: {result.face_symmetry:.1%}")
    print(f"판정: {result.classification.value}")
    print("=" * 60)
    
    # 시각화
    image = visualizer.visualize(image, landmarks, result)
    
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
    
    return 0


def main():
    """메인 실행"""
    print("=" * 60)
    print("Willis 안면 계측법 - 사진 분석")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n사용법:")
        print("  python willis_photo_analysis.py <이미지_파일>")
        print("\n예시:")
        print("  python willis_photo_analysis.py data/input/photo.jpg")
        return 1
    
    image_path = sys.argv[1]
    return analyze_photo(image_path)


if __name__ == "__main__":
    sys.exit(main())

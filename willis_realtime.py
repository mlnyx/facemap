#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 안면 계측법 - 실시간 카메라 분석
"""

import cv2
import sys

from src.core import FaceLandmarker, WillisAnalyzer
from src.ui import WillisVisualizer


def main():
    """메인 실행"""
    print("=" * 60)
    print("Willis 안면 계측법 - 실시간 분석")
    print("=" * 60)
    
    # 초기화
    print("\n📷 카메라 초기화 중...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("❌ 카메라를 열 수 없습니다")
        return 1
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("🎨 시스템 초기화 중...")
    landmarker = FaceLandmarker()
    analyzer = WillisAnalyzer()
    visualizer = WillisVisualizer()
    
    print("\n✓ 준비 완료!")
    print("=" * 60)
    print("🔹 ESC 또는 Q: 종료")
    print("=" * 60)
    print()
    
    # 메인 루프
    window_name = 'Willis 안면 계측법'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            height, width = frame.shape[:2]
            
            # 얼굴 감지
            landmarks = landmarker.get_landmarks(frame)
            
            if landmarks:
                # Willis 분석
                result = analyzer.analyze(landmarks, width, height)
                
                # 시각화
                frame = visualizer.visualize(frame, landmarks, result)
            else:
                # 얼굴 미감지
                cv2.putText(
                    frame,
                    "Face not detected",
                    (50, 50),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.0,
                    (0, 0, 255),
                    2
                )
            
            # 화면 표시
            cv2.imshow(window_name, frame)
            
            # 키 입력
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key in [ord('q'), ord('Q')]:
                break
    
    except KeyboardInterrupt:
        print("\n⚠️  중단됨")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✓ 종료")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

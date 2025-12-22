"""
Willis 안면 계측법 전문 모듈 (MediaPipe 0.10.31 호환)
동공-구열 거리 vs 비저부-턱끝 거리 비교를 통한 수직 고경 평가
"""

import cv2
import numpy as np
from datetime import datetime
import json
import os

# macOS OpenCV GUI 스레딩 이슈 방지
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
if hasattr(cv2, 'setNumThreads'):
    cv2.setNumThreads(1)

# MediaPipe 임포트 (새 API)
try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    from mediapipe import solutions
    from mediapipe.framework.formats import landmark_pb2
    HAS_MEDIAPIPE = True
except ImportError:
    print("오류: MediaPipe를 불러올 수 없습니다.")
    print("해결: pip install mediapipe")
    HAS_MEDIAPIPE = False


class WillisMeasurement:
    """Willis 안면 계측법 구현 클래스"""
    
    def __init__(self):
        if not HAS_MEDIAPIPE:
            raise RuntimeError("MediaPipe가 설치되지 않았습니다.")
        
        # FaceLandmarker 모델 다운로드 URL
        model_url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        model_path = "face_landmarker.task"
        
        # 모델 파일이 없으면 다운로드
        if not os.path.exists(model_path):
            print("Face Landmarker 모델 다운로드 중...")
            import urllib.request
            urllib.request.urlretrieve(model_url, model_path)
            print("다운로드 완료!")
        
        # FaceLandmarker 초기화
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        
        # Willis 계측법 랜드마크 인덱스
        self.NOSE_BASE = 2
        self.CHIN_BOTTOM = 152
        self.MOUTH_CENTER_TOP = 13
        self.MOUTH_CENTER_BOTTOM = 14
        
        # 눈 랜드마크 (동공 추정용)
        self.LEFT_EYE_POINTS = [33, 133, 160, 159, 158, 157, 173]
        self.RIGHT_EYE_POINTS = [362, 263, 387, 386, 385, 384, 398]
        
        # 입 랜드마크
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        
        # 측정 히스토리
        self.measurements = {
            'pupil_to_mouth': [],
            'nose_to_chin': [],
            'ratio': [],
            'classification': [],
            'timestamps': []
        }
        
        # Willis 계측법 정상 기준
        self.NORMAL_RATIO_MIN = 0.95
        self.NORMAL_RATIO_MAX = 1.05
        
    def calculate_distance(self, point1, point2):
        """두 점 사이의 유클리드 거리 계산"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def get_pupil_center(self, landmarks, image_shape):
        """양쪽 동공의 중심점 계산"""
        h, w = image_shape[:2]
        
        # 왼쪽 눈 중심
        left_x = np.mean([landmarks[i].x * w for i in self.LEFT_EYE_POINTS])
        left_y = np.mean([landmarks[i].y * h for i in self.LEFT_EYE_POINTS])
        
        # 오른쪽 눈 중심
        right_x = np.mean([landmarks[i].x * w for i in self.RIGHT_EYE_POINTS])
        right_y = np.mean([landmarks[i].y * h for i in self.RIGHT_EYE_POINTS])
        
        # 양쪽 눈의 중심
        center_x = (left_x + right_x) / 2
        center_y = (left_y + right_y) / 2
        
        return (center_x, center_y), (left_x, left_y), (right_x, right_y)
    
    def get_mouth_line_center(self, landmarks, image_shape):
        """구열(입술 라인) 중심점 계산"""
        h, w = image_shape[:2]
        
        # 입술 중앙점의 수직 위치
        mouth_y = (landmarks[self.MOUTH_CENTER_TOP].y + landmarks[self.MOUTH_CENTER_BOTTOM].y) / 2 * h
        mouth_x = (landmarks[self.MOUTH_LEFT].x + landmarks[self.MOUTH_RIGHT].x) / 2 * w
        
        return (mouth_x, mouth_y)
    
    def calculate_willis_measurements(self, landmarks, image_shape):
        """Willis 안면 계측법에 따른 측정"""
        h, w = image_shape[:2]
        
        # 1. 동공 중심점
        pupil_center, left_pupil, right_pupil = self.get_pupil_center(landmarks, image_shape)
        
        # 2. 구열(입) 중심점
        mouth_center = self.get_mouth_line_center(landmarks, image_shape)
        
        # 3. 비저부 (코 아래)
        nose_point = (landmarks[self.NOSE_BASE].x * w, landmarks[self.NOSE_BASE].y * h)
        
        # 4. 턱 끝
        chin_point = (landmarks[self.CHIN_BOTTOM].x * w, landmarks[self.CHIN_BOTTOM].y * h)
        
        # Willis 계측법 거리 계산
        pupil_to_mouth = self.calculate_distance(pupil_center, mouth_center)
        nose_to_chin = self.calculate_distance(nose_point, chin_point)
        
        # 비율 계산
        ratio = nose_to_chin / pupil_to_mouth if pupil_to_mouth > 0 else 0
        
        # 분류
        if ratio >= self.NORMAL_RATIO_MIN and ratio <= self.NORMAL_RATIO_MAX:
            classification = 'NORMAL'
            classification_kr = '정상'
            color = (0, 255, 0)
        elif ratio < self.NORMAL_RATIO_MIN:
            classification = 'BELOW_AVERAGE'
            classification_kr = '평균 이하 (수직고경 감소)'
            color = (0, 0, 255)
        else:
            classification = 'ABOVE_AVERAGE'
            classification_kr = '평균 이상'
            color = (255, 165, 0)
        
        return {
            'pupil_center': pupil_center,
            'left_pupil': left_pupil,
            'right_pupil': right_pupil,
            'mouth_center': mouth_center,
            'nose_point': nose_point,
            'chin_point': chin_point,
            'pupil_to_mouth': pupil_to_mouth,
            'nose_to_chin': nose_to_chin,
            'ratio': ratio,
            'classification': classification,
            'classification_kr': classification_kr,
            'color': color
        }
    
    def draw_willis_landmarks(self, image, measurements):
        """Willis 계측법 주요 포인트와 측정선 그리기"""
        
        # 주요 포인트 그리기
        points = {
            '동공 중심': measurements['pupil_center'],
            '왼쪽 동공': measurements['left_pupil'],
            '오른쪽 동공': measurements['right_pupil'],
            '구열(입)': measurements['mouth_center'],
            '비저부': measurements['nose_point'],
            '턱끝': measurements['chin_point']
        }
        
        for name, point in points.items():
            x, y = int(point[0]), int(point[1])
            cv2.circle(image, (x, y), 5, (255, 255, 0), -1)
            cv2.circle(image, (x, y), 7, (0, 0, 0), 2)
        
        # 측정선 그리기
        cv2.line(image,
                (int(measurements['pupil_center'][0]), int(measurements['pupil_center'][1])),
                (int(measurements['mouth_center'][0]), int(measurements['mouth_center'][1])),
                (255, 0, 0), 3)
        
        cv2.line(image,
                (int(measurements['nose_point'][0]), int(measurements['nose_point'][1])),
                (int(measurements['chin_point'][0]), int(measurements['chin_point'][1])),
                (0, 0, 255), 3)
        
        cv2.line(image,
                (int(measurements['left_pupil'][0]), int(measurements['left_pupil'][1])),
                (int(measurements['right_pupil'][0]), int(measurements['right_pupil'][1])),
                (0, 255, 255), 2)
        
        # 거리 텍스트
        mid_y = int((measurements['pupil_center'][1] + measurements['mouth_center'][1]) / 2)
        mid_x = int(measurements['pupil_center'][0]) + 20
        cv2.putText(image, f"{measurements['pupil_to_mouth']:.1f}px",
                   (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        mid_y2 = int((measurements['nose_point'][1] + measurements['chin_point'][1]) / 2)
        mid_x2 = int(measurements['nose_point'][0]) + 20
        cv2.putText(image, f"{measurements['nose_to_chin']:.1f}px",
                   (mid_x2, mid_y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return image
    
    def draw_classification_panel(self, image, measurements):
        """Willis 분류 결과 패널 그리기"""
        h, w = image.shape[:2]
        
        panel_width = 500
        panel_height = 220
        panel_x = (w - panel_width) // 2
        panel_y = 10
        
        overlay = image.copy()
        cv2.rectangle(overlay, (panel_x, panel_y),
                     (panel_x + panel_width, panel_y + panel_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        cv2.rectangle(image, (panel_x, panel_y),
                     (panel_x + panel_width, panel_y + panel_height),
                     measurements['color'], 3)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = panel_y + 35
        
        cv2.putText(image, "=== Willis 안면 계측법 ===",
                   (panel_x + 120, y_offset), font, 0.7, (255, 255, 255), 2)
        y_offset += 40
        
        cv2.putText(image, f"동공-구열 거리: {measurements['pupil_to_mouth']:.1f}px",
                   (panel_x + 20, y_offset), font, 0.6, (255, 200, 0), 2)
        y_offset += 35
        
        cv2.putText(image, f"비저부-턱끝 거리: {measurements['nose_to_chin']:.1f}px",
                   (panel_x + 20, y_offset), font, 0.6, (255, 100, 100), 2)
        y_offset += 35
        
        cv2.putText(image, f"비율: {measurements['ratio']:.3f}",
                   (panel_x + 20, y_offset), font, 0.6, (200, 200, 255), 2)
        y_offset += 40
        
        cv2.putText(image, f"판정: {measurements['classification_kr']}",
                   (panel_x + 20, y_offset), font, 0.7, measurements['color'], 3)
        
        legend_y = h - 100
        cv2.putText(image, "기준: 동공-구열 ≈ 비저부-턱끝 (1.0) 이면 정상",
                   (20, legend_y), font, 0.5, (255, 255, 255), 1)
        cv2.putText(image, "비율 < 0.95: 수직 고경 감소 가능성",
                   (20, legend_y + 25), font, 0.5, (0, 100, 255), 1)
        cv2.putText(image, "파란선: 동공-구열 | 빨간선: 비저부-턱끝",
                   (20, legend_y + 50), font, 0.5, (200, 200, 200), 1)
        
        return image
    
    def process_frame(self, frame):
        """프레임 처리 및 Willis 계측"""
        # MediaPipe는 RGB 이미지 필요
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = python.vision.Image(image_format=python.vision.ImageFormat.SRGB, data=rgb_frame)
        
        # 얼굴 감지
        detection_result = self.detector.detect(mp_image)
        
        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            
            # Willis 계측
            measurements = self.calculate_willis_measurements(landmarks, frame.shape)
            
            # 시각화
            frame = self.draw_willis_landmarks(frame, measurements)
            frame = self.draw_classification_panel(frame, measurements)
            
            # 히스토리 저장
            self.measurements['pupil_to_mouth'].append(measurements['pupil_to_mouth'])
            self.measurements['nose_to_chin'].append(measurements['nose_to_chin'])
            self.measurements['ratio'].append(measurements['ratio'])
            self.measurements['classification'].append(measurements['classification'])
            self.measurements['timestamps'].append(datetime.now())
            
            # 최근 30프레임만 유지
            for key in self.measurements:
                if len(self.measurements[key]) > 30:
                    self.measurements[key].pop(0)
        else:
            cv2.putText(frame, "얼굴을 감지할 수 없습니다. 정면을 봐주세요.",
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def save_measurement_report(self, filename="willis_report.json"):
        """Willis 계측 리포트 저장"""
        if len(self.measurements['timestamps']) == 0:
            print("저장할 데이터가 없습니다.")
            return
        
        ratios = self.measurements['ratio']
        classifications = self.measurements['classification']
        
        normal_count = classifications.count('NORMAL')
        below_count = classifications.count('BELOW_AVERAGE')
        above_count = classifications.count('ABOVE_AVERAGE')
        total = len(classifications)
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_frames': total,
            'willis_method': {
                'description': 'Willis 안면 계측법: 동공-구열 거리와 비저부-턱끝 거리 비교',
                'normal_criteria': f'{self.NORMAL_RATIO_MIN} <= ratio <= {self.NORMAL_RATIO_MAX}'
            },
            'statistics': {
                'pupil_to_mouth': {
                    'mean': float(np.mean(self.measurements['pupil_to_mouth'])),
                    'std': float(np.std(self.measurements['pupil_to_mouth']))
                },
                'nose_to_chin': {
                    'mean': float(np.mean(self.measurements['nose_to_chin'])),
                    'std': float(np.std(self.measurements['nose_to_chin']))
                },
                'ratio': {
                    'mean': float(np.mean(ratios)),
                    'min': float(np.min(ratios)),
                    'max': float(np.max(ratios)),
                    'std': float(np.std(ratios))
                }
            },
            'classification_summary': {
                'normal': {
                    'count': normal_count,
                    'percentage': f'{normal_count/total*100:.1f}%'
                },
                'below_average': {
                    'count': below_count,
                    'percentage': f'{below_count/total*100:.1f}%',
                    'note': '수직 고경 감소 가능성'
                },
                'above_average': {
                    'count': above_count,
                    'percentage': f'{above_count/total*100:.1f}%'
                }
            },
            'recommendation': self._get_recommendation(np.mean(ratios))
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Willis 계측 리포트 저장: {filename}")
        return report
    
    def _get_recommendation(self, mean_ratio):
        """평균 비율에 따른 권장사항"""
        if mean_ratio < 0.90:
            return "심각한 수직 고경 감소 의심. 전문의 상담 권장."
        elif mean_ratio < 0.95:
            return "수직 고경 감소 가능성. 추가 검사 고려."
        elif mean_ratio <= 1.05:
            return "정상 범위. 현재 안모 비율 양호."
        else:
            return "평균 이상. 추가 평가 고려."


def main():
    """Willis 계측법 전용 프로그램 실행"""
    willis = WillisMeasurement()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return
    
    print("\n" + "="*70)
    print("Willis 안면 계측법 - 수직 고경 평가 프로그램")
    print("="*70)
    print("\n키보드 단축키:")
    print("  'q' 또는 'ESC' : 종료")
    print("  's' : 스크린샷 저장")
    print("  'r' : 리포트 저장 (JSON)")
    print("="*70 + "\n")
    
    window_name = 'Willis 안면 계측법'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break
        
        try:
            processed_frame = willis.process_frame(frame)
            cv2.imshow(window_name, processed_frame)
        except Exception as e:
            print(f"프레임 처리 오류: {e}")
            continue
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27:
            break
        elif key == ord('s'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"willis_measurement_{timestamp}.png"
            cv2.imwrite(filename, processed_frame)
            print(f"✓ 스크린샷 저장: {filename}")
        elif key == ord('r'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"willis_report_{timestamp}.json"
            willis.save_measurement_report(filename)
    
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    # 종료 시 통계
    if len(willis.measurements['ratio']) > 0:
        mean_ratio = np.mean(willis.measurements['ratio'])
        print(f"\n평균 비율: {mean_ratio:.3f}")
        print(willis._get_recommendation(mean_ratio))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n프로그램 종료")
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        cv2.destroyAllWindows()

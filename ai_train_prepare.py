#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis AI 모델 학습 데이터 준비
- 논문 기준: 500+ 라벨링된 사진 필요 (90% 정확도 목표)
"""

import cv2
import numpy as np
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from src.core import FaceLandmarker, WillisAnalyzer


@dataclass
class TrainingData:
    """학습 데이터 항목"""
    image_path: str
    willis_ratio: float
    pupil_to_mouth: float
    nose_to_chin: float
    face_symmetry: float
    classification: str  # 정상, 평균 이하, 평균 이상
    is_frontal: bool  # 정면 여부
    landmarks: List[Tuple[float, float]]  # 468개 랜드마크
    image_width: int
    image_height: int
    timestamp: str


class TrainingDataCollector:
    """학습 데이터 수집기"""
    
    def __init__(self, output_dir: str = "data/training"):
        """초기화"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = self.output_dir / "images"
        self.labels_dir = self.output_dir / "labels"
        self.images_dir.mkdir(exist_ok=True)
        self.labels_dir.mkdir(exist_ok=True)
        
        self.landmarker = FaceLandmarker()
        self.analyzer = WillisAnalyzer()
        
        self.dataset = []
        self.load_existing_dataset()
    
    def load_existing_dataset(self):
        """기존 데이터셋 로드"""
        dataset_path = self.output_dir / "dataset.json"
        if dataset_path.exists():
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.dataset = data.get('items', [])
            print(f"✓ 기존 데이터셋 로드: {len(self.dataset)}건")
        else:
            print("✓ 새 데이터셋 시작")
    
    def save_dataset(self):
        """데이터셋 저장"""
        dataset_path = self.output_dir / "dataset.json"
        data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'total_count': len(self.dataset),
            'items': self.dataset
        }
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 데이터셋 저장: {len(self.dataset)}건")
    
    def process_image(self, image_path: str, copy_image: bool = True) -> TrainingData:
        """이미지 처리 및 데이터 추출"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")
        
        h, w = image.shape[:2]
        landmarks = self.landmarker.get_landmarks(image)
        
        if not landmarks:
            raise ValueError(f"얼굴을 찾을 수 없습니다: {image_path}")
        
        result = self.analyzer.analyze(landmarks, w, h)
        
        # 랜드마크를 리스트로 변환
        landmarks_list = [(lm.x * w, lm.y * h) for lm in landmarks]
        
        # 이미지 복사
        if copy_image:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(image_path)}"
            new_image_path = self.images_dir / filename
            cv2.imwrite(str(new_image_path), image)
            rel_image_path = str(new_image_path.relative_to(self.output_dir))
        else:
            rel_image_path = image_path
        
        return TrainingData(
            image_path=rel_image_path,
            willis_ratio=result.ratio,
            pupil_to_mouth=result.pupil_to_mouth_distance,
            nose_to_chin=result.nose_to_chin_distance,
            face_symmetry=result.face_symmetry,
            classification=result.classification.value,
            is_frontal=result.face_symmetry >= 0.85,
            landmarks=landmarks_list,
            image_width=w,
            image_height=h,
            timestamp=datetime.now().isoformat()
        )
    
    def add_image(self, image_path: str, copy_image: bool = True):
        """이미지 추가"""
        try:
            data = self.process_image(image_path, copy_image)
            self.dataset.append(asdict(data))
            print(f"✓ 추가: {image_path} (비율: {data.willis_ratio:.3f}, {data.classification})")
        except Exception as e:
            print(f"✗ 실패: {image_path} - {e}")
    
    def batch_add(self, image_paths: List[str], copy_images: bool = True):
        """배치 추가"""
        print(f"\n📦 {len(image_paths)}개 이미지 처리 중...\n")
        for path in image_paths:
            self.add_image(path, copy_images)
        self.save_dataset()
    
    def get_statistics(self) -> Dict:
        """데이터셋 통계"""
        if not self.dataset:
            return {}
        
        classifications = [item['classification'] for item in self.dataset]
        ratios = [item['willis_ratio'] for item in self.dataset]
        frontals = [item['is_frontal'] for item in self.dataset]
        
        return {
            'total_count': len(self.dataset),
            'normal_count': classifications.count('정상'),
            'below_count': classifications.count('평균 이하'),
            'above_count': classifications.count('평균 이상'),
            'frontal_count': sum(frontals),
            'non_frontal_count': len(frontals) - sum(frontals),
            'avg_ratio': np.mean(ratios),
            'min_ratio': np.min(ratios),
            'max_ratio': np.max(ratios),
            'std_ratio': np.std(ratios)
        }
    
    def print_statistics(self):
        """통계 출력"""
        stats = self.get_statistics()
        if not stats:
            print("데이터가 없습니다")
            return
        
        print("\n" + "=" * 60)
        print("학습 데이터 통계")
        print("=" * 60)
        print(f"총 데이터: {stats['total_count']}건")
        print(f"  - 정상: {stats['normal_count']}건 ({stats['normal_count']/stats['total_count']*100:.1f}%)")
        print(f"  - 평균 이하: {stats['below_count']}건 ({stats['below_count']/stats['total_count']*100:.1f}%)")
        print(f"  - 평균 이상: {stats['above_count']}건 ({stats['above_count']/stats['total_count']*100:.1f}%)")
        print()
        print(f"정면 사진: {stats['frontal_count']}건 ({stats['frontal_count']/stats['total_count']*100:.1f}%)")
        print(f"측면/비정면: {stats['non_frontal_count']}건")
        print()
        print(f"Willis 비율 평균: {stats['avg_ratio']:.3f} ± {stats['std_ratio']:.3f}")
        print(f"  - 최소값: {stats['min_ratio']:.3f}")
        print(f"  - 최대값: {stats['max_ratio']:.3f}")
        print("=" * 60)
        
        # 논문 기준 체크
        target = 500
        remaining = max(0, target - stats['total_count'])
        print(f"\n📊 논문 기준 (500건) 달성률: {stats['total_count']/target*100:.1f}%")
        if remaining > 0:
            print(f"   ⚠️  {remaining}건 더 필요")
        else:
            print(f"   ✅ 목표 달성!")
    
    def export_for_training(self):
        """학습용 데이터 내보내기 (CSV, NumPy)"""
        if not self.dataset:
            print("데이터가 없습니다")
            return
        
        # CSV 내보내기
        csv_path = self.output_dir / "training_data.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("image_path,willis_ratio,classification,pupil_to_mouth,nose_to_chin,symmetry,is_frontal\n")
            for item in self.dataset:
                f.write(f"{item['image_path']},{item['willis_ratio']},{item['classification']},"
                       f"{item['pupil_to_mouth']},{item['nose_to_chin']},{item['face_symmetry']},{item['is_frontal']}\n")
        print(f"✅ CSV 내보내기: {csv_path}")
        
        # NumPy 배열 내보내기
        features = np.array([[
            item['willis_ratio'],
            item['pupil_to_mouth'],
            item['nose_to_chin'],
            item['face_symmetry'],
            1.0 if item['is_frontal'] else 0.0
        ] for item in self.dataset])
        
        labels = np.array([
            0 if item['classification'] == '평균 이하' 
            else 1 if item['classification'] == '정상'
            else 2
            for item in self.dataset
        ])
        
        np.save(self.output_dir / "features.npy", features)
        np.save(self.output_dir / "labels.npy", labels)
        print(f"✅ NumPy 배열 내보내기: features.npy, labels.npy")
        print(f"   Features shape: {features.shape}")
        print(f"   Labels shape: {labels.shape}")


def main():
    """메인 실행"""
    import sys
    import glob
    
    collector = TrainingDataCollector()
    
    if len(sys.argv) < 2:
        print("\n" + "=" * 60)
        print("Willis AI 학습 데이터 준비")
        print("=" * 60)
        print("\n사용법:")
        print("  python ai_train_prepare.py <command> [args]")
        print("\n명령어:")
        print("  add <image_path>          - 단일 이미지 추가")
        print("  batch <pattern>           - 여러 이미지 일괄 추가")
        print("  stats                     - 통계 보기")
        print("  export                    - 학습용 데이터 내보내기")
        print("\n예시:")
        print("  python ai_train_prepare.py add data/input/정면1.jpeg")
        print("  python ai_train_prepare.py batch 'data/input/*.jpeg'")
        print("  python ai_train_prepare.py stats")
        print("  python ai_train_prepare.py export")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("❌ 이미지 경로를 지정하세요")
            sys.exit(1)
        collector.add_image(sys.argv[2])
        collector.save_dataset()
        collector.print_statistics()
    
    elif command == "batch":
        if len(sys.argv) < 3:
            print("❌ 이미지 패턴을 지정하세요")
            sys.exit(1)
        pattern = sys.argv[2]
        image_paths = glob.glob(pattern)
        if not image_paths:
            print(f"❌ 매칭되는 파일이 없습니다: {pattern}")
            sys.exit(1)
        collector.batch_add(image_paths)
        collector.print_statistics()
    
    elif command == "stats":
        collector.print_statistics()
    
    elif command == "export":
        collector.export_for_training()
        collector.print_statistics()
    
    else:
        print(f"❌ 알 수 없는 명령어: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

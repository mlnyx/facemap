#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis 분석 비교 - 여러 사진 비교 및 리포트 생성
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

from src.core import FaceLandmarker, WillisAnalyzer


@dataclass
class ComparisonItem:
    """비교 항목"""
    name: str
    image_path: str
    ratio: float
    classification: str
    pupil_to_mouth: float
    nose_to_chin: float
    symmetry: float


class WillisComparator:
    """Willis 분석 비교기"""
    
    def __init__(self):
        """초기화"""
        self.landmarker = FaceLandmarker()
        self.analyzer = WillisAnalyzer()
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        font_paths = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        ]
        for path in font_paths:
            if os.path.exists(path):
                font_manager.fontManager.addfont(path)
                plt.rcParams['font.family'] = font_manager.FontProperties(fname=path).get_name()
                break
        plt.rcParams['axes.unicode_minus'] = False
    
    def analyze_single(self, image_path: str, name: str) -> ComparisonItem:
        """단일 이미지 분석"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")
        
        h, w = image.shape[:2]
        landmarks = self.landmarker.get_landmarks(image)
        
        if not landmarks:
            raise ValueError(f"얼굴을 찾을 수 없습니다: {image_path}")
        
        result = self.analyzer.analyze(landmarks, w, h)
        
        return ComparisonItem(
            name=name,
            image_path=image_path,
            ratio=result.ratio,
            classification=result.classification.value,
            pupil_to_mouth=result.pupil_to_mouth_distance,
            nose_to_chin=result.nose_to_chin_distance,
            symmetry=result.face_symmetry
        )
    
    def compare_multiple(self, image_paths: List[str], names: List[str] = None) -> List[ComparisonItem]:
        """여러 이미지 비교 분석"""
        if names is None:
            names = [f"사진 {i+1}" for i in range(len(image_paths))]
        
        results = []
        for path, name in zip(image_paths, names):
            try:
                result = self.analyze_single(path, name)
                results.append(result)
                print(f"✓ {name} 분석 완료")
            except Exception as e:
                print(f"✗ {name} 분석 실패: {e}")
        
        return results
    
    def create_comparison_chart(self, items: List[ComparisonItem], output_path: str = "data/output/comparison_chart.png"):
        """비교 차트 생성"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Willis 안면 계측법 비교 분석', fontsize=16, fontweight='bold')
        
        names = [item.name for item in items]
        ratios = [item.ratio for item in items]
        pupil_distances = [item.pupil_to_mouth for item in items]
        nose_distances = [item.nose_to_chin for item in items]
        symmetries = [item.symmetry * 100 for item in items]
        
        colors = ['#28a745' if 0.90 <= r <= 1.10 else '#dc3545' for r in ratios]
        
        # Willis 비율
        axes[0, 0].bar(names, ratios, color=colors)
        axes[0, 0].axhline(y=0.90, color='orange', linestyle='--', label='정상 하한')
        axes[0, 0].axhline(y=1.10, color='orange', linestyle='--', label='정상 상한')
        axes[0, 0].axhline(y=1.00, color='green', linestyle='-', alpha=0.3, label='이상값')
        axes[0, 0].set_ylabel('비율')
        axes[0, 0].set_title('Willis 비율 비교')
        axes[0, 0].legend()
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # 거리 비교
        x = np.arange(len(names))
        width = 0.35
        axes[0, 1].bar(x - width/2, pupil_distances, width, label='동공-구열', color='#667eea')
        axes[0, 1].bar(x + width/2, nose_distances, width, label='비저부-턱끝', color='#764ba2')
        axes[0, 1].set_ylabel('거리 (px)')
        axes[0, 1].set_title('측정 거리 비교')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(names)
        axes[0, 1].legend()
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # 대칭도
        axes[1, 0].bar(names, symmetries, color='#17a2b8')
        axes[1, 0].axhline(y=85, color='red', linestyle='--', label='비정면 기준')
        axes[1, 0].set_ylabel('대칭도 (%)')
        axes[1, 0].set_title('얼굴 대칭도 (정면도)')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)
        
        # 개선도 (첫 번째 대비)
        if len(items) > 1:
            improvements = [(item.ratio - items[0].ratio) / items[0].ratio * 100 for item in items]
            improvement_colors = ['#28a745' if imp > 0 else '#dc3545' for imp in improvements]
            axes[1, 1].bar(names, improvements, color=improvement_colors)
            axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            axes[1, 1].set_ylabel('변화율 (%)')
            axes[1, 1].set_title(f'{names[0]} 대비 개선도')
            axes[1, 1].grid(axis='y', alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, '비교 대상이 없습니다', 
                          ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('개선도')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n✅ 차트 저장: {output_path}")
        plt.show()
    
    def create_report(self, items: List[ComparisonItem], output_path: str = "data/output/willis_report.txt"):
        """텍스트 리포트 생성"""
        report = []
        report.append("=" * 60)
        report.append("Willis 안면 계측법 비교 분석 리포트")
        report.append("=" * 60)
        report.append(f"분석 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
        report.append(f"총 분석 수: {len(items)}건")
        report.append("=" * 60)
        report.append("")
        
        for i, item in enumerate(items, 1):
            report.append(f"[{i}] {item.name}")
            report.append("-" * 60)
            report.append(f"  파일: {os.path.basename(item.image_path)}")
            report.append(f"  동공-구열 거리: {item.pupil_to_mouth:.1f}px")
            report.append(f"  비저부-턱끝 거리: {item.nose_to_chin:.1f}px")
            report.append(f"  Willis 비율: {item.ratio:.3f}")
            report.append(f"  대칭도: {item.symmetry*100:.1f}%")
            report.append(f"  판정: {item.classification}")
            report.append("")
        
        # 통계
        report.append("=" * 60)
        report.append("통계")
        report.append("=" * 60)
        ratios = [item.ratio for item in items]
        report.append(f"평균 Willis 비율: {np.mean(ratios):.3f}")
        report.append(f"최소값: {np.min(ratios):.3f} ({items[np.argmin(ratios)].name})")
        report.append(f"최대값: {np.max(ratios):.3f} ({items[np.argmax(ratios)].name})")
        report.append(f"표준편차: {np.std(ratios):.3f}")
        
        # 개선도
        if len(items) > 1:
            report.append("")
            report.append("=" * 60)
            report.append(f"{items[0].name} 대비 개선도")
            report.append("=" * 60)
            base_ratio = items[0].ratio
            for item in items[1:]:
                improvement = (item.ratio - base_ratio) / base_ratio * 100
                report.append(f"{item.name}: {improvement:+.1f}%")
        
        report.append("")
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"✅ 리포트 저장: {output_path}")
        print("\n" + report_text)


def main():
    """메인 실행"""
    import sys
    
    if len(sys.argv) < 2:
        print("\n사용법:")
        print("  python willis_compare.py <image1> <image2> [image3] ...")
        print("\n예시:")
        print("  python willis_compare.py data/input/구의치.jpeg data/input/신의치.jpeg")
        print("  python willis_compare.py data/input/*.jpeg")
        sys.exit(1)
    
    print("=" * 60)
    print("Willis 안면 계측법 비교 분석")
    print("=" * 60)
    print()
    
    image_paths = sys.argv[1:]
    names = [os.path.splitext(os.path.basename(p))[0] for p in image_paths]
    
    comparator = WillisComparator()
    
    print(f"📊 {len(image_paths)}개 이미지 분석 중...\n")
    items = comparator.compare_multiple(image_paths, names)
    
    if not items:
        print("❌ 분석 가능한 이미지가 없습니다")
        sys.exit(1)
    
    print(f"\n✅ {len(items)}개 분석 완료\n")
    
    # 차트 생성
    comparator.create_comparison_chart(items)
    
    # 리포트 생성
    comparator.create_report(items)


if __name__ == "__main__":
    main()

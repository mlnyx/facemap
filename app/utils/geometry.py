"""기하학 계산 유틸리티"""
import numpy as np


def calculate_distance(p1, p2):
    """
    두 점 사이의 유클리드 거리 계산
    
    Args:
        p1: (x, y) 첫 번째 점
        p2: (x, y) 두 번째 점
    
    Returns:
        float: 거리
    """
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def calculate_angle(p1, p2):
    """
    두 점 사이의 각도 계산 (도)
    
    Args:
        p1: (x, y) 시작점
        p2: (x, y) 끝점
    
    Returns:
        float: 각도 (0-180도)
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return abs(np.degrees(np.arctan2(dy, dx)))

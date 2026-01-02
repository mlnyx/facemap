"""이미지 처리 유틸리티"""
import cv2
import numpy as np
from base64 import b64encode, b64decode
import re


def encode_image_to_base64(image):
    """
    이미지를 base64 문자열로 인코딩
    
    Args:
        image: OpenCV 이미지 (numpy array)
    
    Returns:
        str: base64 인코딩된 문자열
    """
    _, buffer = cv2.imencode('.jpg', image)
    return b64encode(buffer).decode('utf-8')


def decode_base64_to_image(base64_string):
    """
    base64 문자열을 OpenCV 이미지로 디코딩
    
    Args:
        base64_string: base64 인코딩된 이미지 문자열
    
    Returns:
        numpy.ndarray: OpenCV 이미지 또는 None (실패 시)
    """
    try:
        # data:image 헤더 제거
        frame_data = re.sub('^data:image/.+;base64,', '', base64_string)
        frame_bytes = b64decode(frame_data)
        
        # NumPy 배열로 변환
        nparr = np.frombuffer(frame_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception:
        return None


def read_image_from_file(file_storage):
    """
    Flask FileStorage 객체에서 이미지 읽기
    
    Args:
        file_storage: Flask request.files의 파일 객체
    
    Returns:
        numpy.ndarray: OpenCV 이미지 또는 None (실패 시)
    """
    try:
        file_bytes = np.frombuffer(file_storage.read(), np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    except Exception:
        return None

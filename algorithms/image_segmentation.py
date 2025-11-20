"""
图像分割算法模块
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': '图像分割',
        'description': '使用阈值分割或边缘检测进行图像分割',
        'inputs': ['image'],
        'outputs': ['image'],
        'parameters': {
            'method': {
                'type': 'select',
                'options': ['threshold', 'canny', 'watershed'],
                'default': 'threshold',
                'label': '分割方法'
            },
            'threshold_value': {
                'type': 'number',
                'default': 127,
                'min': 0,
                'max': 255,
                'label': '阈值'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行图像分割"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    method = parameters.get('method', 'threshold')
    threshold_value = int(parameters.get('threshold_value', 127))
    
    # 转换为灰度图
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    if method == 'threshold':
        # 阈值分割
        _, result = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    elif method == 'canny':
        # Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    elif method == 'watershed':
        # 分水岭算法（简化版）
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        result = cv2.cvtColor(opening, cv2.COLOR_GRAY2RGB)
    else:
        result = image
    
    return {'image': result, 'output': result}


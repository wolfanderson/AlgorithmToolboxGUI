"""
ROI提取算法模块
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': 'ROI提取',
        'description': '提取图像中的感兴趣区域',
        'inputs': ['image'],
        'outputs': ['image'],
        'parameters': {
            'x': {
                'type': 'number',
                'default': 0,
                'min': 0,
                'label': 'X坐标'
            },
            'y': {
                'type': 'number',
                'default': 0,
                'min': 0,
                'label': 'Y坐标'
            },
            'width': {
                'type': 'number',
                'default': 100,
                'min': 1,
                'label': '宽度'
            },
            'height': {
                'type': 'number',
                'default': 100,
                'min': 1,
                'label': '高度'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行ROI提取"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    x = int(parameters.get('x', 0))
    y = int(parameters.get('y', 0))
    width = int(parameters.get('width', 100))
    height = int(parameters.get('height', 100))
    
    h, w = image.shape[:2]
    
    # 确保坐标在图像范围内
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))
    width = min(width, w - x)
    height = min(height, h - y)
    
    # 提取ROI
    roi = image[y:y+height, x:x+width]
    
    # 如果ROI太小，返回原图
    if roi.size == 0:
        return {'image': image, 'output': image}
    
    # 在原图上标记ROI区域
    result = image.copy()
    cv2.rectangle(result, (x, y), (x + width, y + height), (0, 255, 0), 2)
    
    # 也可以只返回ROI区域
    # result = roi
    
    return {'image': result, 'output': result, 'roi': roi}


"""
图像配准算法模块
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': '图像配准',
        'description': '对图像进行配准和校正',
        'inputs': ['image'],
        'outputs': ['image'],
        'parameters': {
            'angle': {
                'type': 'number',
                'default': 0,
                'min': -180,
                'max': 180,
                'label': '旋转角度'
            },
            'scale': {
                'type': 'number',
                'default': 1.0,
                'min': 0.5,
                'max': 2.0,
                'step': 0.1,
                'label': '缩放比例'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行图像配准"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    angle = float(parameters.get('angle', 0))
    scale = float(parameters.get('scale', 1.0))
    
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    # 旋转矩阵
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
    
    # 应用变换
    result = cv2.warpAffine(image, rotation_matrix, (width, height), 
                            flags=cv2.INTER_LINEAR, 
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(255, 255, 255))
    
    return {'image': result, 'output': result}


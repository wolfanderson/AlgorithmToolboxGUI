"""
图像滤波算法模块
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': '图像滤波',
        'description': '对图像进行各种滤波处理',
        'inputs': ['image'],
        'outputs': ['image'],
        'parameters': {
            'filter_type': {
                'type': 'select',
                'options': ['blur', 'gaussian', 'median', 'bilateral'],
                'default': 'gaussian',
                'label': '滤波类型'
            },
            'kernel_size': {
                'type': 'number',
                'default': 5,
                'min': 3,
                'max': 21,
                'step': 2,
                'label': '核大小'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行图像滤波"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    filter_type = parameters.get('filter_type', 'gaussian')
    kernel_size = int(parameters.get('kernel_size', 5))
    
    # 确保核大小为奇数
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    if filter_type == 'blur':
        result = cv2.blur(image, (kernel_size, kernel_size))
    elif filter_type == 'gaussian':
        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    elif filter_type == 'median':
        result = cv2.medianBlur(image, kernel_size)
    elif filter_type == 'bilateral':
        result = cv2.bilateralFilter(image, kernel_size, 80, 80)
    else:
        result = image
    
    return {'image': result, 'output': result}


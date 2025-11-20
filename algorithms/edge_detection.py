"""
边缘检测算法模块
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': '边缘检测',
        'description': '检测图像边缘',
        'inputs': ['image'],
        'outputs': ['image'],
        'parameters': {
            'method': {
                'type': 'select',
                'options': ['canny', 'sobel', 'laplacian'],
                'default': 'canny',
                'label': '检测方法'
            },
            'threshold1': {
                'type': 'number',
                'default': 50,
                'min': 0,
                'max': 255,
                'label': '阈值1'
            },
            'threshold2': {
                'type': 'number',
                'default': 150,
                'min': 0,
                'max': 255,
                'label': '阈值2'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行边缘检测"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    method = parameters.get('method', 'canny')
    threshold1 = int(parameters.get('threshold1', 50))
    threshold2 = int(parameters.get('threshold2', 150))
    
    # 转换为灰度图
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    if method == 'canny':
        edges = cv2.Canny(gray, threshold1, threshold2)
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    elif method == 'sobel':
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        edges = np.uint8(np.absolute(edges))
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    elif method == 'laplacian':
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        edges = np.uint8(np.absolute(laplacian))
        result = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    else:
        result = image
    
    return {'image': result, 'output': result}


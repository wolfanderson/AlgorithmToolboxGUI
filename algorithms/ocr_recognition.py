"""
OCR识别算法模块（模拟）
"""
import cv2
import numpy as np
from typing import Dict, Any

def get_info():
    """返回算法信息"""
    return {
        'name': 'OCR识别',
        'description': '识别图像中的文字（模拟实现）',
        'inputs': ['image'],
        'outputs': ['image', 'text'],
        'parameters': {
            'preprocess': {
                'type': 'checkbox',
                'default': True,
                'label': '预处理图像'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行OCR识别"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    preprocess = parameters.get('preprocess', True)
    
    # 复制图像用于显示结果
    result = image.copy()
    
    # 预处理
    if preprocess:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # 二值化
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 在结果图像上绘制识别区域（模拟）
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours[:10]:  # 只处理前10个轮廓
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 20:  # 过滤小区域
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # 模拟识别的文字
    text = "模拟OCR识别结果: 检测到文字区域"
    
    return {'image': result, 'output': result, 'text': text}


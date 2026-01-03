"""
OCR识别算法模块（支持多种OCR方案：PaddleOCR、DeepSeekOCR等）
"""
import cv2
import numpy as np
from typing import Dict, Any, Optional

# 导入OCR提供者抽象层
try:
    from .ocr_providers import OCRProviderFactory, OCRResult
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from algorithms.ocr_providers import OCRProviderFactory, OCRResult
    except ImportError:
        OCRProviderFactory = None
        OCRResult = None
        print("警告: OCR提供者模块未找到，将使用PaddleOCR作为默认方案")

# 导入中文文本绘制工具
try:
    from .cv2_utils import put_text_safe
except ImportError:
    try:
        from algorithms.cv2_utils import put_text_safe
    except ImportError:
        # 如果导入失败，使用OpenCV默认方法（不支持中文）
        def put_text_safe(img, text, position, font_size=20, color=(0, 255, 0)):
            return cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                              font_size / 30.0, color, 2)

def get_info():
    """返回算法信息"""
    # 获取可用的OCR提供者列表
    available_providers = ['paddleocr']
    if OCRProviderFactory:
        try:
            available_providers = OCRProviderFactory.list_available_providers()
        except:
            pass
    
    return {
        'name': 'OCR识别',
        'description': '识别图像中的文字，支持多种OCR方案（PaddleOCR、DeepSeekOCR等）',
        'inputs': ['image'],
        'outputs': ['image', 'text'],
        'parameters': {
            'ocr_provider': {
                'type': 'select',
                'options': available_providers,
                'default': 'paddleocr' if 'paddleocr' in available_providers else (available_providers[0] if available_providers else 'paddleocr'),
                'label': 'OCR方案'
            },
            'show_boxes': {
                'type': 'checkbox',
                'default': True,
                'label': '显示识别框'
            },
            'use_angle_cls': {
                'type': 'checkbox',
                'default': True,
                'label': '使用角度分类（仅PaddleOCR）'
            },
            'api_key': {
                'type': 'text',
                'default': '',
                'label': 'API密钥（DeepSeekOCR需要）',
                'placeholder': '输入DeepSeek API密钥'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行OCR识别"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    # 获取参数
    ocr_provider_name = parameters.get('ocr_provider', 'paddleocr').lower()
    show_boxes = parameters.get('show_boxes', True)
    use_angle_cls = parameters.get('use_angle_cls', True)
    api_key = parameters.get('api_key', '')
    
    # 复制图像用于显示结果
    result = image.copy()
    
    try:
        # 使用OCR提供者抽象层
        if OCRProviderFactory is None:
            raise RuntimeError("OCR提供者模块未加载，请检查ocr_providers.py文件")
        
        # 获取OCR提供者
        provider_kwargs = {}
        if ocr_provider_name == 'paddleocr':
            provider_kwargs['use_angle_cls'] = use_angle_cls
            provider_kwargs['lang'] = 'ch'
        elif ocr_provider_name == 'deepseekocr':
            if api_key:
                provider_kwargs['api_key'] = api_key
            else:
                import os
                api_key = os.getenv('DEEPSEEK_API_KEY')
                if not api_key:
                    raise ValueError("DeepSeekOCR需要API密钥，请在参数中配置或设置环境变量DEEPSEEK_API_KEY")
                provider_kwargs['api_key'] = api_key
        
        provider = OCRProviderFactory.get_provider(ocr_provider_name, **provider_kwargs)
        
        if not provider.is_available():
            raise RuntimeError(f"{provider.get_name()}不可用，请检查配置和依赖")
        
        # 确保图像是BGR格式（OCR提供者内部会处理）
        if len(image.shape) == 3:
            if image.shape[2] == 3:
                # 假设是RGB，转换为BGR
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
        else:
            # 灰度图转BGR
            image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # 执行OCR识别
        ocr_result: OCRResult = provider.recognize(image_bgr)
        
        # 处理识别结果
        all_text = []
        print(f"使用{provider.get_name()}识别到 {len(ocr_result)} 个文本")
        
        for i, item in enumerate(ocr_result):
            text = item['text']
            score = item['score']
            box = item['box']
            poly = item['poly']
            
            if not text:
                continue
            
            # 添加到文本列表
            all_text.append(f"{text} ({score:.2f})")
            
            # 在图像上绘制识别框和文字
            if show_boxes and box:
                try:
                    if poly is not None:
                        # 使用多边形坐标
                        cv2.polylines(result, [poly], True, (0, 255, 0), 2)
                        if len(poly) > 0:
                            top_left = tuple(poly[0])
                            display_text = text[:20] if len(text) > 20 else text
                            # 使用支持中文的文本绘制函数
                            result = put_text_safe(result, display_text, top_left, 
                                                 font_size=18, color=(0, 255, 0))
                    elif len(box) >= 4:
                        # 使用边界框坐标
                        # box格式: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                        box_array = np.array(box, dtype=np.int32)
                        cv2.polylines(result, [box_array], True, (0, 255, 0), 2)
                        if len(box_array) > 0:
                            top_left = tuple(box_array[0])
                            display_text = text[:20] if len(text) > 20 else text
                            # 使用支持中文的文本绘制函数
                            result = put_text_safe(result, display_text, top_left, 
                                                 font_size=18, color=(0, 255, 0))
                except Exception as e:
                    print(f"绘制识别框失败: {e}")
                    continue
        
        # 合并所有识别的文字
        recognized_text = "\n".join(all_text) if all_text else "未识别到文字"
        
    except Exception as e:
        # 如果OCR识别失败，返回错误信息
        error_msg = f"OCR识别失败: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        recognized_text = error_msg
        # 在图像上显示错误信息（使用支持中文的函数）
        result = put_text_safe(result, "OCR识别失败", (10, 30), 
                               font_size=30, color=(0, 0, 255))
    
    return {'image': result, 'output': result, 'text': recognized_text}


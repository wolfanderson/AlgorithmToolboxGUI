"""
OCR识别算法模块（使用PaddleOCR）
"""
import cv2
import numpy as np
from typing import Dict, Any

try:
    import paddle
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError as e:
    PADDLEOCR_AVAILABLE = False
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if python_version >= "3.12":
        print(f"警告: PaddleOCR需要PaddlePaddle，但Python {python_version}可能不被支持。")
        print("建议使用Python 3.11或更低版本。")
        print("或者尝试安装: pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple/")
    else:
        print(f"警告: PaddleOCR未正确安装。错误: {e}")
        print("请运行: pip install paddlepaddle paddleocr")

# 全局OCR实例（延迟初始化，支持不同配置）
_ocr_instances = {}  # 使用字典存储不同配置的实例

def get_ocr_instance(use_angle_cls=True):
    """获取OCR实例（根据配置缓存）"""
    global _ocr_instances
    
    if not PADDLEOCR_AVAILABLE:
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        error_msg = (
            "PaddleOCR未正确安装。\n"
            f"当前Python版本: {python_version}\n"
            "PaddlePaddle可能不支持Python 3.14，建议使用Python 3.11或3.12。\n"
            "安装步骤：\n"
            "1. pip install paddlepaddle\n"
            "2. pip install paddleocr"
        )
        raise ImportError(error_msg)
    
    # 使用配置作为键来缓存实例
    config_key = f"angle_cls_{use_angle_cls}"
    
    if config_key not in _ocr_instances:
        # 初始化PaddleOCR，使用中文和英文
        # use_angle_cls 在初始化时设置，不在调用时设置
        _ocr_instances[config_key] = PaddleOCR(use_angle_cls=use_angle_cls, lang='ch')
    
    return _ocr_instances[config_key]

def get_info():
    """返回算法信息"""
    return {
        'name': 'OCR识别',
        'description': '使用PaddleOCR识别图像中的文字',
        'inputs': ['image'],
        'outputs': ['image', 'text'],
        'parameters': {
            'show_boxes': {
                'type': 'checkbox',
                'default': True,
                'label': '显示识别框'
            },
            'use_angle_cls': {
                'type': 'checkbox',
                'default': True,
                'label': '使用角度分类'
            }
        }
    }

def execute(inputs: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行OCR识别"""
    image = inputs.get('image')
    if image is None:
        raise ValueError('缺少输入图像')
    
    if not PADDLEOCR_AVAILABLE:
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        error_msg = (
            "PaddleOCR未正确安装。\n"
            f"当前Python版本: {python_version}\n"
            "PaddlePaddle可能不支持Python 3.14，建议使用Python 3.11或3.12。\n"
            "安装步骤：\n"
            "1. pip install paddlepaddle\n"
            "2. pip install paddleocr"
        )
        raise ImportError(error_msg)
    
    show_boxes = parameters.get('show_boxes', True)
    
    # 复制图像用于显示结果
    result = image.copy()
    
    try:
        # 获取 use_angle_cls 参数（在初始化时使用）
        use_angle_cls = parameters.get('use_angle_cls', True)
        
        # 获取OCR实例（根据参数重新初始化，如果需要）
        # 注意：如果参数改变，需要重新创建实例
        ocr = get_ocr_instance(use_angle_cls=use_angle_cls)
        
        # PaddleOCR需要BGR格式的图像
        if len(image.shape) == 3:
            # 如果是RGB，转换为BGR
            if image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
        else:
            # 灰度图转BGR
            image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # 执行OCR识别
        # 注意：新版本的 PaddleOCR，ocr() 方法不接受 cls 参数
        # use_angle_cls 已经在初始化时设置
        ocr_result = ocr.ocr(image_bgr)
        
        # 处理识别结果
        all_text = []
        if ocr_result and isinstance(ocr_result, list) and len(ocr_result) > 0:
            # 新版本 PaddleOCR 返回格式: [OCRResult对象或字典]
            result_dict = ocr_result[0]
            
            # OCRResult 对象是字典类型，可以直接使用
            if isinstance(result_dict, dict):
                # 新版本格式：字典格式
                rec_texts = result_dict.get('rec_texts', [])
                rec_scores = result_dict.get('rec_scores', [])
                rec_polys = result_dict.get('rec_polys', [])
                rec_boxes = result_dict.get('rec_boxes', [])
                
                # 调试信息
                print(f"识别到 {len(rec_texts) if rec_texts else 0} 个文本")
                
                # 处理识别结果
                # 确保 rec_texts, rec_scores, rec_polys, rec_boxes 都是列表
                if isinstance(rec_texts, np.ndarray):
                    rec_texts = rec_texts.tolist()
                if isinstance(rec_scores, np.ndarray):
                    rec_scores = rec_scores.tolist()
                if isinstance(rec_polys, np.ndarray):
                    rec_polys = rec_polys.tolist()
                if isinstance(rec_boxes, np.ndarray):
                    # rec_boxes 可能是 2D 数组，需要转换为列表
                    if rec_boxes.ndim == 2:
                        rec_boxes = rec_boxes.tolist()
                    else:
                        rec_boxes = []
                
                for i, text in enumerate(rec_texts):
                    if not text:
                        continue
                    
                    # 获取置信度
                    confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                    
                    # 添加到文本列表
                    all_text.append(f"{text} ({confidence:.2f})")
                    
                    # 在图像上绘制识别框和文字
                    if show_boxes:
                        # 获取多边形或边界框
                        if i < len(rec_polys) and rec_polys[i] is not None:
                            # 使用多边形坐标
                            poly = rec_polys[i]
                            if isinstance(poly, (list, np.ndarray)):
                                if isinstance(poly, np.ndarray):
                                    poly = poly.tolist()
                                if len(poly) >= 4:
                                    box_array = np.array(poly, dtype=np.int32)
                                    cv2.polylines(result, [box_array], True, (0, 255, 0), 2)
                                    
                                    # 在框的左上角显示文字
                                    if len(box_array) > 0:
                                        top_left = tuple(box_array[0])
                                        display_text = text[:20] if len(text) > 20 else text
                                        cv2.putText(result, display_text, top_left, 
                                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        elif isinstance(rec_boxes, (list, np.ndarray)) and len(rec_boxes) > i:
                            # 使用边界框坐标 [x1, y1, x2, y2]
                            try:
                                box = rec_boxes[i]
                                if isinstance(box, np.ndarray):
                                    box = box.tolist()
                                if isinstance(box, (list, tuple)) and len(box) >= 4:
                                    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                                    cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    cv2.putText(result, text[:20], (x1, y1 - 5), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            except (IndexError, TypeError, ValueError) as e:
                                print(f"绘制边界框失败: {e}")
                                continue
            else:
                # 旧版本格式：列表格式 [[[[x1, y1], ...], (text, confidence)], ...]
                result_list = result_dict if isinstance(result_dict, list) else []
                
                for line in result_list:
                    if not line or len(line) < 2:
                        continue
                    
                    try:
                        # line格式: [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], (text, confidence)]
                        box = line[0]  # 四个点的坐标
                        text_info = line[1]  # (文字, 置信度)
                        
                        # 检查 text_info 格式
                        if not text_info or len(text_info) < 2:
                            continue
                        
                        text = text_info[0] if isinstance(text_info, (list, tuple)) else str(text_info)
                        confidence = text_info[1] if isinstance(text_info, (list, tuple)) and len(text_info) > 1 else 0.0
                        
                        # 确保 text 是字符串
                        if not isinstance(text, str):
                            text = str(text) if text else ""
                        
                        if text:  # 只处理非空文本
                            all_text.append(f"{text} ({confidence:.2f})")
                            
                            # 在图像上绘制识别框和文字
                            if show_boxes:
                                # 检查 box 格式
                                if box and len(box) >= 4:
                                    # 绘制文本框（多边形）
                                    box_array = np.array(box, dtype=np.int32)
                                    cv2.polylines(result, [box_array], True, (0, 255, 0), 2)
                                    
                                    # 在框的左上角显示文字
                                    if len(box_array) > 0:
                                        top_left = tuple(box_array[0])
                                        # 限制文字长度，避免显示过长
                                        display_text = text[:20] if len(text) > 20 else text
                                        cv2.putText(result, display_text, top_left, 
                                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    except (IndexError, TypeError, ValueError) as e:
                        # 跳过格式不正确的行
                        print(f"跳过格式不正确的OCR结果行: {e}")
                        continue
        
        # 合并所有识别的文字
        recognized_text = "\n".join(all_text) if all_text else "未识别到文字"
        
    except Exception as e:
        # 如果OCR识别失败，返回错误信息
        error_msg = f"OCR识别失败: {str(e)}"
        print(error_msg)
        recognized_text = error_msg
        # 在图像上显示错误信息
        cv2.putText(result, "OCR识别失败", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return {'image': result, 'output': result, 'text': recognized_text}


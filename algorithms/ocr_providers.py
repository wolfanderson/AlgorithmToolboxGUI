"""
OCR提供者抽象层
支持多种OCR方案：PaddleOCR、DeepSeekOCR等
"""
import cv2
import numpy as np
import os
import base64
import io
from typing import Dict, Any, List, Tuple, Optional
from abc import ABC, abstractmethod
from PIL import Image

# ==================== OCR结果数据类 ====================

class OCRResult:
    """OCR识别结果"""
    def __init__(self, texts: List[str], scores: List[float], 
                 boxes: List[List[Tuple[int, int]]], 
                 polys: Optional[List[np.ndarray]] = None):
        """
        Args:
            texts: 识别的文本列表
            scores: 置信度列表
            boxes: 边界框列表，每个框为 [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            polys: 多边形坐标列表（可选）
        """
        self.texts = texts
        self.scores = scores
        self.boxes = boxes
        self.polys = polys or []
    
    def __len__(self):
        return len(self.texts)
    
    def __iter__(self):
        for i in range(len(self)):
            yield {
                'text': self.texts[i],
                'score': self.scores[i] if i < len(self.scores) else 0.0,
                'box': self.boxes[i] if i < len(self.boxes) else None,
                'poly': self.polys[i] if i < len(self.polys) else None
            }

# ==================== OCR提供者接口 ====================

class OCRProvider(ABC):
    """OCR提供者抽象基类"""
    
    @abstractmethod
    def recognize(self, image: np.ndarray, **kwargs) -> OCRResult:
        """
        识别图像中的文字
        
        Args:
            image: 输入图像（numpy数组，BGR格式）
            **kwargs: 其他参数
            
        Returns:
            OCRResult: 识别结果
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查OCR提供者是否可用"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取OCR提供者名称"""
        pass

# ==================== PaddleOCR提供者 ====================

class PaddleOCRProvider(OCRProvider):
    """PaddleOCR提供者"""
    
    def __init__(self, use_angle_cls: bool = True, lang: str = 'ch'):
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self._ocr_instance = None
        self._available = False
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            self._ocr_instance = PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.lang,
                show_log=False
            )
            self._available = True
        except ImportError as e:
            self._available = False
            print(f"PaddleOCR未安装: {e}")
    
    def is_available(self) -> bool:
        return self._available
    
    def get_name(self) -> str:
        return "PaddleOCR"
    
    def recognize(self, image: np.ndarray, **kwargs) -> OCRResult:
        """使用PaddleOCR识别"""
        if not self._available or not self._ocr_instance:
            raise RuntimeError("PaddleOCR未正确初始化")
        
        # 确保图像是BGR格式
        if len(image.shape) == 2:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 3:
            # 检查是否为RGB，如果是则转换为BGR
            image_bgr = image.copy()
        else:
            image_bgr = image
        
        # 执行OCR
        ocr_result = self._ocr_instance.ocr(image_bgr)
        
        # 解析结果
        texts = []
        scores = []
        boxes = []
        polys = []
        
        if ocr_result and isinstance(ocr_result, list) and len(ocr_result) > 0:
            result_dict = ocr_result[0]
            
            if isinstance(result_dict, dict):
                # 新版本格式
                rec_texts = result_dict.get('rec_texts', [])
                rec_scores = result_dict.get('rec_scores', [])
                rec_polys = result_dict.get('rec_polys', [])
                rec_boxes = result_dict.get('rec_boxes', [])
                
                # 转换为列表
                if isinstance(rec_texts, np.ndarray):
                    rec_texts = rec_texts.tolist()
                if isinstance(rec_scores, np.ndarray):
                    rec_scores = rec_scores.tolist()
                if isinstance(rec_polys, np.ndarray):
                    rec_polys = rec_polys.tolist()
                if isinstance(rec_boxes, np.ndarray):
                    if rec_boxes.ndim == 2:
                        rec_boxes = rec_boxes.tolist()
                    else:
                        rec_boxes = []
                
                texts = [str(t) for t in rec_texts if t]
                scores = [float(s) for s in rec_scores[:len(texts)]]
                
                # 处理边界框
                for i in range(len(texts)):
                    if i < len(rec_polys) and rec_polys[i] is not None:
                        poly = rec_polys[i]
                        if isinstance(poly, np.ndarray):
                            poly = poly.tolist()
                        if isinstance(poly, (list, tuple)) and len(poly) >= 4:
                            # 转换为 [(x,y), ...] 格式
                            box_points = [(int(p[0]), int(p[1])) for p in poly[:4]]
                            boxes.append(box_points)
                            polys.append(np.array(poly, dtype=np.int32))
                        else:
                            boxes.append(None)
                            polys.append(None)
                    elif i < len(rec_boxes) and len(rec_boxes[i]) >= 4:
                        # 使用边界框 [x1, y1, x2, y2]
                        box = rec_boxes[i]
                        if isinstance(box, np.ndarray):
                            box = box.tolist()
                        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                        boxes.append([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
                        polys.append(None)
                    else:
                        boxes.append(None)
                        polys.append(None)
            else:
                # 旧版本格式
                result_list = result_dict if isinstance(result_dict, list) else []
                for line in result_list:
                    if not line or len(line) < 2:
                        continue
                    try:
                        box_data = line[0]
                        text_info = line[1]
                        
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            text = str(text_info[0])
                            confidence = float(text_info[1])
                            
                            if text:
                                texts.append(text)
                                scores.append(confidence)
                                
                                if isinstance(box_data, list) and len(box_data) >= 4:
                                    box_points = [(int(p[0]), int(p[1])) for p in box_data[:4]]
                                    boxes.append(box_points)
                                    polys.append(np.array(box_data, dtype=np.int32))
                                else:
                                    boxes.append(None)
                                    polys.append(None)
                    except (IndexError, TypeError, ValueError):
                        continue
        
        return OCRResult(texts, scores, boxes, polys)

# ==================== DeepSeekOCR提供者 ====================

class DeepSeekOCRProvider(OCRProvider):
    """DeepSeekOCR提供者（通过API调用）"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        Args:
            api_key: DeepSeek API密钥
            api_base: API基础URL（可选，默认使用DeepSeek官方API）
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
        self.api_base = api_base or 'https://api.deepseek.com/v1/chat/completions'
        self._available = bool(self.api_key)
    
    def is_available(self) -> bool:
        return self._available
    
    def get_name(self) -> str:
        return "DeepSeekOCR"
    
    def recognize(self, image: np.ndarray, **kwargs) -> OCRResult:
        """使用DeepSeekOCR API识别"""
        if not self._available:
            raise RuntimeError("DeepSeekOCR API密钥未配置")
        
        try:
            import requests
            
            # 将图像转换为base64
            if len(image.shape) == 2:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            pil_image = Image.fromarray(image_rgb)
            buffered = io.BytesIO()
            pil_image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # 调用DeepSeek API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 构建请求（使用视觉模型）
            payload = {
                "model": "deepseek-chat",  # 或使用支持视觉的模型
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的所有文字，返回JSON格式：{\"texts\": [\"文本1\", \"文本2\"], \"boxes\": [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ...], \"scores\": [0.95, 0.92]}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1
            }
            
            response = requests.post(self.api_base, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            
            # 解析响应
            # 注意：DeepSeek API的响应格式可能需要根据实际API调整
            content = result_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 尝试解析JSON响应
            import json
            try:
                # 提取JSON部分
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    ocr_data = json.loads(content[json_start:json_end])
                    
                    texts = ocr_data.get('texts', [])
                    scores = ocr_data.get('scores', [1.0] * len(texts))
                    boxes_data = ocr_data.get('boxes', [])
                    
                    boxes = []
                    polys = []
                    for box_data in boxes_data:
                        if isinstance(box_data, list) and len(box_data) >= 4:
                            box_points = [(int(p[0]), int(p[1])) for p in box_data[:4]]
                            boxes.append(box_points)
                            polys.append(np.array(box_data, dtype=np.int32))
                        else:
                            boxes.append(None)
                            polys.append(None)
                    
                    return OCRResult(texts, scores, boxes, polys)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"解析DeepSeekOCR响应失败: {e}")
                print(f"响应内容: {content[:500]}")
            
            # 如果JSON解析失败，尝试提取纯文本
            texts = [content.strip()] if content.strip() else []
            return OCRResult(texts, [0.9] * len(texts), [None] * len(texts))
            
        except ImportError:
            raise RuntimeError("需要安装requests库: pip install requests")
        except Exception as e:
            raise RuntimeError(f"DeepSeekOCR API调用失败: {str(e)}")

# ==================== OCR提供者工厂 ====================

class OCRProviderFactory:
    """OCR提供者工厂"""
    
    _providers: Dict[str, OCRProvider] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider: OCRProvider):
        """注册OCR提供者"""
        cls._providers[name] = provider
    
    @classmethod
    def get_provider(cls, name: str, **kwargs) -> OCRProvider:
        """
        获取OCR提供者实例
        
        Args:
            name: 提供者名称 ('paddleocr', 'deepseekocr')
            **kwargs: 提供者特定参数
        """
        name_lower = name.lower()
        
        if name_lower == 'paddleocr':
            use_angle_cls = kwargs.get('use_angle_cls', True)
            lang = kwargs.get('lang', 'ch')
            cache_key = f"paddleocr_{use_angle_cls}_{lang}"
            if cache_key not in cls._providers:
                cls._providers[cache_key] = PaddleOCRProvider(use_angle_cls=use_angle_cls, lang=lang)
            return cls._providers[cache_key]
        
        elif name_lower == 'deepseekocr':
            api_key = kwargs.get('api_key')
            api_base = kwargs.get('api_base')
            cache_key = f"deepseekocr_{api_key or 'default'}"
            if cache_key not in cls._providers:
                cls._providers[cache_key] = DeepSeekOCRProvider(api_key=api_key, api_base=api_base)
            return cls._providers[cache_key]
        
        else:
            raise ValueError(f"未知的OCR提供者: {name}")
    
    @classmethod
    def list_available_providers(cls) -> List[str]:
        """列出所有可用的OCR提供者"""
        available = []
        
        # 检查PaddleOCR
        try:
            provider = PaddleOCRProvider()
            if provider.is_available():
                available.append('paddleocr')
        except:
            pass
        
        # 检查DeepSeekOCR
        try:
            if os.getenv('DEEPSEEK_API_KEY'):
                available.append('deepseekocr')
        except:
            pass
        
        return available


"""
OpenCV工具函数，支持中文字符绘制
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional

def put_chinese_text(img: np.ndarray, text: str, position: Tuple[int, int], 
                    font_size: int = 20, color: Tuple[int, int, int] = (0, 255, 0),
                    font_path: Optional[str] = None) -> np.ndarray:
    """
    在图像上绘制中文文本（支持中文）
    
    Args:
        img: 输入图像（numpy数组，BGR格式）
        text: 要绘制的文本
        position: 文本位置 (x, y)
        font_size: 字体大小
        color: 颜色 (B, G, R)
        font_path: 字体文件路径（可选，默认使用系统字体）
    
    Returns:
        绘制后的图像
    """
    # 转换为PIL Image
    if len(img.shape) == 2:
        img_pil = Image.fromarray(img, mode='L')
        img_pil = img_pil.convert('RGB')
    elif img.shape[2] == 3:
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        img_pil = Image.fromarray(img)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(img_pil)
    
    # 尝试加载字体
    font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = None
    
    # 如果没有指定字体或加载失败，尝试使用系统字体
    if font is None:
        try:
            # Windows系统字体
            import platform
            if platform.system() == 'Windows':
                font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', font_size)  # 微软雅黑
            elif platform.system() == 'Darwin':  # macOS
                font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', font_size)
            else:  # Linux
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', font_size)
        except:
            # 如果都失败，使用默认字体（可能不支持中文）
            try:
                font = ImageFont.load_default()
            except:
                font = None
    
    # 绘制文本
    # PIL使用RGB颜色，需要转换
    rgb_color = (color[2], color[1], color[0])  # BGR -> RGB
    
    if font:
        draw.text(position, text, font=font, fill=rgb_color)
    else:
        # 如果没有字体，使用默认字体（可能不支持中文）
        draw.text(position, text, fill=rgb_color)
    
    # 转换回OpenCV格式
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    return img_cv

def put_text_safe(img: np.ndarray, text: str, position: Tuple[int, int],
                 font_size: int = 20, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """
    安全地绘制文本（自动检测是否为中文，选择合适的方法）
    
    Args:
        img: 输入图像
        text: 要绘制的文本
        position: 文本位置
        font_size: 字体大小
        color: 颜色
    
    Returns:
        绘制后的图像
    """
    # 检查是否包含中文字符
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    
    if has_chinese:
        # 使用PIL绘制中文
        return put_chinese_text(img, text, position, font_size, color)
    else:
        # 使用OpenCV绘制英文（更快）
        return cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                          font_size / 30.0, color, 2)


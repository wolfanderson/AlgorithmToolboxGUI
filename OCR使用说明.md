# OCR识别模块使用说明

## 概述

OCR识别模块现已支持多种OCR方案，包括：
- **PaddleOCR**: 本地OCR引擎，支持中英文识别
- **DeepSeekOCR**: 基于DeepSeek大模型的OCR服务（通过API调用）

## 功能特性

1. **多OCR方案支持**: 可在配置面板中选择不同的OCR方案
2. **统一接口**: 所有OCR方案使用统一的接口，结果格式一致
3. **可扩展架构**: 易于添加新的OCR方案

## 使用方法

### 1. PaddleOCR（默认方案）

#### 安装依赖
```bash
# 安装PaddlePaddle（根据Python版本选择）
pip install paddlepaddle

# 安装PaddleOCR
pip install paddleocr
```

#### 配置参数
- **OCR方案**: 选择 `paddleocr`
- **显示识别框**: 是否在图像上绘制识别框
- **使用角度分类**: 是否启用角度分类（提高倾斜文本识别准确率）

### 2. DeepSeekOCR

#### 获取API密钥
1. 访问 [DeepSeek官网](https://www.deepseek.com/)
2. 注册账号并获取API密钥

#### 配置方式

**方式一：通过环境变量（推荐）**
```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here

# Linux/Mac
export DEEPSEEK_API_KEY=your_api_key_here
```

**方式二：通过节点参数**
1. 在OCR节点配置面板中
2. 选择OCR方案为 `deepseekocr`
3. 在"API密钥"输入框中填入您的API密钥

#### 配置参数
- **OCR方案**: 选择 `deepseekocr`
- **API密钥**: 输入DeepSeek API密钥（如果未设置环境变量）
- **显示识别框**: 是否在图像上绘制识别框

## 架构设计

### OCR提供者抽象层

系统使用抽象层设计，所有OCR方案都实现统一的接口：

```python
class OCRProvider(ABC):
    @abstractmethod
    def recognize(self, image: np.ndarray, **kwargs) -> OCRResult:
        """识别图像中的文字"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查OCR提供者是否可用"""
        pass
```

### 当前支持的提供者

1. **PaddleOCRProvider**: 本地OCR引擎
2. **DeepSeekOCRProvider**: 大模型OCR服务

### 添加新的OCR方案

要添加新的OCR方案，只需：

1. 在 `algorithms/ocr_providers.py` 中创建新的提供者类
2. 继承 `OCRProvider` 基类
3. 实现 `recognize()`, `is_available()`, `get_name()` 方法
4. 在 `OCRProviderFactory.get_provider()` 中添加新方案的创建逻辑

示例：
```python
class MyOCRProvider(OCRProvider):
    def __init__(self, **kwargs):
        # 初始化代码
        pass
    
    def is_available(self) -> bool:
        # 检查是否可用
        return True
    
    def get_name(self) -> str:
        return "MyOCR"
    
    def recognize(self, image: np.ndarray, **kwargs) -> OCRResult:
        # 实现识别逻辑
        # 返回OCRResult对象
        pass
```

## 性能对比

| OCR方案 | 识别速度 | 准确率 | 成本 | 适用场景 |
|---------|---------|--------|------|---------|
| PaddleOCR | 快 | 高 | 免费 | 本地部署，大批量处理 |
| DeepSeekOCR | 中等 | 很高 | 按量付费 | 高精度需求，复杂场景 |

## 注意事项

1. **PaddleOCR**:
   - 需要安装PaddlePaddle，Python 3.14可能不支持
   - 建议使用Python 3.11或3.12
   - 首次运行会下载模型文件

2. **DeepSeekOCR**:
   - 需要网络连接
   - API调用有延迟（取决于网络速度）
   - 需要有效的API密钥
   - 可能有调用频率限制

3. **API密钥安全**:
   - 建议使用环境变量存储API密钥
   - 不要将API密钥提交到代码仓库

## 故障排查

### PaddleOCR无法使用
1. 检查是否安装了paddlepaddle和paddleocr
2. 检查Python版本是否兼容
3. 查看控制台错误信息

### DeepSeekOCR无法使用
1. 检查API密钥是否正确
2. 检查网络连接
3. 检查API密钥是否有效
4. 查看控制台错误信息

### 识别结果为空
1. 检查输入图像是否清晰
2. 尝试调整图像预处理
3. 尝试不同的OCR方案

## 更新日志

### v2.0 (2024-12-01)
- 新增多OCR方案支持
- 添加DeepSeekOCR集成
- 重构OCR提供者抽象层
- 改进错误处理和提示

---

**提示**: 如果遇到问题，请查看控制台的错误信息，或参考 `安装说明_PaddleOCR.md` 获取更多帮助。


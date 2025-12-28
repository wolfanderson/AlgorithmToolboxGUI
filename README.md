# 工业质检算法组合平台

一个支持"拖拉拽"的可视化算法组合平台，用于工业质检领域的图像处理算法验证。

## 功能特性

- 🎨 **可视化节点编辑器**：通过拖拽方式组合不同的算法模块
- 🔗 **节点连接系统**：支持算法之间的数据流连接
- 🖼️ **实时预览**：上传图片后实时查看处理结果
- 📦 **可扩展算法库**：支持自定义算法模块
- 🔄 **工作流执行**：自动按拓扑顺序执行算法组合

## 内置算法模块

- **图像分割**：支持阈值分割、Canny边缘检测、分水岭算法
- **OCR识别**：文字识别（模拟实现）
- **图像配准**：图像旋转和缩放校正
- **ROI提取**：感兴趣区域提取
- **图像滤波**：支持多种滤波算法（模糊、高斯、中值、双边）
- **边缘检测**：Canny、Sobel、Laplacian边缘检测

## 安装与运行

### 快速开始

**Windows用户**:
1. 双击 `install.bat` 安装依赖
2. 双击 `run.bat` 启动服务
3. 浏览器访问 `http://localhost:5000`

**Linux/Mac用户**:
```bash
chmod +x install.sh && ./install.sh
python app.py
```

### 详细步骤

#### 1. 安装依赖

```bash
# 使用虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

#### 2. 启动服务

```bash
python app.py
```

#### 3. 访问平台

打开浏览器访问：`http://localhost:5000`

### 📖 详细运行指南

更多安装和运行说明，请查看 **[运行指南.md](运行指南.md)**

## 使用说明

1. **上传图片**：点击"上传图片"按钮，选择要处理的图像
2. **添加算法节点**：从左侧算法库中拖拽算法到画布
3. **连接节点**：点击节点的输出端口，拖拽到另一个节点的输入端口
4. **执行工作流**：点击"执行工作流"按钮，查看处理结果
5. **查看结果**：在右侧预览面板查看输入和输出图像

## 添加自定义算法

在 `algorithms/` 目录下创建新的Python文件，实现以下接口：

```python
def get_info():
    """返回算法信息"""
    return {
        'name': '算法名称',
        'description': '算法描述',
        'inputs': ['image'],  # 输入列表
        'outputs': ['image'],  # 输出列表
        'parameters': {}  # 参数定义
    }

def execute(inputs, parameters):
    """执行算法"""
    image = inputs.get('image')
    # 处理逻辑
    return {'image': result, 'output': result}
```

## 项目结构

```
AlgorithmToolboxGUI/
├── app.py                 # Flask后端服务
├── algorithms/            # 算法模块目录
│   ├── __init__.py
│   ├── image_segmentation.py
│   ├── ocr_recognition.py
│   ├── image_registration.py
│   ├── roi_extraction.py
│   ├── image_filter.py
│   └── edge_detection.py
├── static/                # 前端静态文件
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt       # Python依赖
└── README.md
```

## 技术栈

- **后端**：Flask + OpenCV + NumPy + PIL
- **前端**：HTML + CSS + JavaScript (原生)
- **图像处理**：OpenCV

## 注意事项

- **OCR功能**: 支持PaddleOCR（本地）和DeepSeekOCR（大模型API），详见 [OCR使用说明.md](OCR使用说明.md)
- **算法模块**: 支持热加载，修改后重启服务即可生效
- **工作流执行**: 采用拓扑排序，确保按正确顺序执行
- **Python版本**: 推荐使用Python 3.8-3.11（PaddleOCR在Python 3.14可能不支持）

## 相关文档

- 📖 [运行指南.md](运行指南.md) - 详细的安装和运行说明
- 📖 [架构设计文档.md](架构设计文档.md) - 系统架构设计
- 📖 [OCR使用说明.md](OCR使用说明.md) - OCR功能使用指南
- 📖 [安装说明.md](安装说明.md) - 依赖安装问题排查

## 许可证

MIT License

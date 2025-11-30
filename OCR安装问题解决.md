# OCR识别模块安装问题解决方案

## 错误：No module named 'paddle'

### 问题原因
PaddleOCR 依赖于 PaddlePaddle 核心库，但：
1. **Python 3.14 太新**：PaddlePaddle 目前不支持 Python 3.14，最高支持到 Python 3.11
2. **缺少 paddlepaddle**：需要单独安装 PaddlePaddle 核心库

### 解决方案

#### 方案1：使用 Python 3.11 或 3.12（强烈推荐）

这是最简单可靠的方案：

1. **安装 Python 3.11 或 3.12**
   - 从 https://www.python.org/downloads/ 下载
   - 建议使用 Python 3.11，兼容性最好

2. **创建新的虚拟环境**
   ```bash
   python3.11 -m venv venv
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install paddlepaddle
   pip install paddleocr
   pip install -r requirements.txt
   ```

#### 方案2：尝试安装 PaddlePaddle（Python 3.14）

虽然可能不成功，但可以尝试：

```bash
# 方法1：使用官方源
pip install paddlepaddle

# 方法2：使用百度镜像
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple/

# 方法3：使用CPU版本
pip install paddlepaddle==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果安装失败，说明 Python 3.14 确实不支持，请使用方案1。

#### 方案3：使用 Docker（如果已安装 Docker）

```bash
# 使用官方PaddlePaddle镜像
docker pull paddlepaddle/paddle:latest-gpu-cuda11.2-cudnn8
# 或CPU版本
docker pull paddlepaddle/paddle:latest
```

### 验证安装

安装完成后，验证是否成功：

```python
python -c "import paddle; print(paddle.__version__)"
python -c "from paddleocr import PaddleOCR; print('PaddleOCR安装成功')"
```

### 当前状态检查

运行以下命令检查当前环境：

```bash
python --version
pip list | findstr -i paddle
```

### 推荐方案

**强烈建议使用 Python 3.11**，因为：
- PaddlePaddle 官方支持
- 所有依赖包都有预编译版本
- 安装简单，无需编译

### 临时解决方案

如果暂时无法安装 PaddleOCR，可以：
1. 注释掉 OCR 识别节点
2. 使用其他算法节点
3. 其他功能不受影响



# PaddleOCR 安装问题解决方案

## 问题：pyclipper 构建失败

### 原因
- 缺少 Microsoft Visual C++ 14.0 或更高版本的构建工具
- Python 3.14.0 版本较新，可能缺少预编译的 wheel 包

## 解决方案

### 方案1：安装 Visual C++ Build Tools（推荐）

1. 下载并安装 Microsoft C++ Build Tools：
   - 访问：https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - 下载 "Build Tools for Visual Studio"
   - 安装时选择 "C++ build tools" 工作负载

2. 安装完成后，重新运行：
   ```bash
   pip install paddleocr
   ```

### 方案2：使用预编译的 wheel 包

如果不想安装构建工具，可以尝试：

```bash
# 方法1：使用 conda（如果有 conda 环境）
conda install -c conda-forge paddleocr

# 方法2：手动下载预编译的 wheel
# 访问 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyclipper
# 下载对应 Python 版本的 pyclipper wheel 文件
pip install pyclipper-1.3.0.post6-cp314-cp314-win_amd64.whl
```

### 方案3：使用较低版本的 Python（最简单）

Python 3.14.0 太新，建议使用 Python 3.11 或 3.12：

1. 安装 Python 3.11 或 3.12
2. 创建新的虚拟环境：
   ```bash
   python3.11 -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### 方案4：使用 Docker（如果已安装 Docker）

```bash
docker pull paddlepaddle/paddle:latest
# 然后在容器中运行应用
```

## 快速检查

运行以下命令检查是否已安装构建工具：

```bash
where cl
```

如果有输出，说明已安装；如果没有，需要安装 Visual C++ Build Tools。

## 推荐方案

**最简单的方法**：使用 Python 3.11 或 3.12，这些版本有更多预编译的包可用。



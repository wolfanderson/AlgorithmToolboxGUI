@echo off
chcp 65001 >nul
echo ========================================
echo 工业质检算法组合平台 - 依赖安装脚本
echo ========================================
echo.

echo 正在升级pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 正在安装依赖包（使用清华镜像源）...
echo.

pip install Flask -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo Flask 安装失败！
    pause
    exit /b 1
)

pip install flask-cors -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo flask-cors 安装失败！
    pause
    exit /b 1
)

pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo numpy 安装失败！
    pause
    exit /b 1
)

pip install Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo Pillow 安装失败！
    pause
    exit /b 1
)

pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo opencv-python 安装失败！
    echo 尝试安装 opencv-python-headless...
    pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo opencv-python-headless 也安装失败！
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 所有依赖安装完成！
echo ========================================
echo.
pause


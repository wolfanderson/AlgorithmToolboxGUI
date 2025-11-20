#!/bin/bash

echo "========================================"
echo "工业质检算法组合平台 - 依赖安装脚本"
echo "========================================"
echo ""

echo "正在升级pip..."
python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "正在安装依赖包（使用清华镜像源）..."
echo ""

pip3 install Flask -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "Flask 安装失败！"
    exit 1
}

pip3 install flask-cors -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "flask-cors 安装失败！"
    exit 1
}

pip3 install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "numpy 安装失败！"
    exit 1
}

pip3 install Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "Pillow 安装失败！"
    exit 1
}

pip3 install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "opencv-python 安装失败！"
    echo "尝试安装 opencv-python-headless..."
    pip3 install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple || {
        echo "opencv-python-headless 也安装失败！"
        exit 1
    }
}

echo ""
echo "========================================"
echo "所有依赖安装完成！"
echo "========================================"
echo ""


#!/bin/bash
echo "安装视频分析系统依赖项..."
echo

python3 --version
if [ $? -ne 0 ]; then
    echo "错误: Python3未安装"
    exit 1
fi

echo
echo "安装核心依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install requests>=2.25.0
python3 -m pip install numpy>=1.20.0
python3 -m pip install opencv-python>=4.5.0
python3 -m pip install Pillow>=8.0.0
python3 -m pip install PyYAML>=5.4.0
python3 -m pip install loguru>=0.6.0

echo
echo "验证安装..."
python3 -c "import requests, numpy, cv2, PIL, yaml, loguru; print('所有依赖安装成功!')"

if [ $? -ne 0 ]; then
    echo
    echo "部分依赖安装失败，尝试备用方案..."
    python3 install_dependencies_safe.py
fi

echo
echo "安装完成！"

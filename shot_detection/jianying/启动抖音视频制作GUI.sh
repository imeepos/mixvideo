#!/bin/bash

echo ""
echo "🎵 启动抖音视频制作工作流程GUI"
echo "================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.7+"
    echo "💡 Ubuntu/Debian: sudo apt install python3"
    echo "💡 CentOS/RHEL: sudo yum install python3"
    echo "💡 macOS: brew install python3"
    exit 1
fi

echo "✅ Python环境检查通过"
echo "🚀 启动GUI应用..."
echo ""

python3 douyin_workflow_gui.py

echo ""
echo "📋 GUI应用已关闭"
read -p "按回车键退出..."

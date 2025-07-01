#!/bin/bash

echo ""
echo "🎬 抖音视频制作工作流程 - Linux/Mac 启动脚本"
echo "================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.7+"
    echo "💡 Ubuntu/Debian: sudo apt install python3"
    echo "💡 CentOS/RHEL: sudo yum install python3"
    echo "💡 macOS: brew install python3"
    exit 1
fi

# 检查当前目录结构
if [ ! -d "resources" ]; then
    echo "❌ 错误: 当前目录下没有找到 resources 文件夹"
    echo "💡 请确保在包含 resources 和 templates 文件夹的目录中运行此脚本"
    echo ""
    echo "📁 期望的目录结构:"
    echo "   your_project/"
    echo "   ├── resources/     (视频素材目录)"
    echo "   ├── templates/     (抖音项目模板目录)"
    echo "   └── outputs/       (输出目录，自动创建)"
    echo ""
    exit 1
fi

if [ ! -d "templates" ]; then
    echo "❌ 错误: 当前目录下没有找到 templates 文件夹"
    echo "💡 请确保在包含 resources 和 templates 文件夹的目录中运行此脚本"
    exit 1
fi

echo "✅ 目录结构检查通过"
echo ""

# 询问用户运行模式
echo "请选择运行模式:"
echo "1. 预览模式 (只分析，不生成文件)"
echo "2. 完整运行 (生成所有项目)"
echo ""
read -p "请输入选择 (1 或 2): " choice

case $choice in
    1)
        echo ""
        echo "🔍 启动预览模式..."
        python3 douyin_workflow.py --preview -v
        ;;
    2)
        echo ""
        echo "🚀 启动完整工作流程..."
        python3 douyin_workflow.py -v
        ;;
    *)
        echo "❌ 无效选择，默认使用预览模式"
        echo ""
        python3 douyin_workflow.py --preview -v
        ;;
esac

echo ""
echo "📋 工作流程完成！"
read -p "按回车键退出..."

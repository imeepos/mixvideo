#!/bin/bash
echo "🎬 智能镜头检测与分段系统 - 安装程序"
echo "========================================"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

echo "📁 创建安装目录..."
mkdir -p /opt/ShotDetectionGUI

echo "📋 复制文件..."
cp -r ShotDetectionGUI_dist/* /opt/ShotDetectionGUI/

echo "🔗 创建可执行链接..."
ln -sf /opt/ShotDetectionGUI/ShotDetectionGUI /usr/local/bin/shot-detection-gui

echo "📋 创建桌面文件..."
cat > /usr/share/applications/shot-detection-gui.desktop << EOF
[Desktop Entry]
Name=智能镜头检测
Name[en]=Shot Detection GUI
Comment=智能视频镜头检测与分段系统
Comment[en]=Intelligent Video Shot Detection and Segmentation System
Exec=/opt/ShotDetectionGUI/ShotDetectionGUI
Icon=/opt/ShotDetectionGUI/icon.ico
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF

echo "🔧 设置权限..."
chmod +x /opt/ShotDetectionGUI/ShotDetectionGUI
chmod +x /usr/share/applications/shot-detection-gui.desktop

echo "✅ 安装完成！"
echo "📱 您可以在应用程序菜单中找到'智能镜头检测'"

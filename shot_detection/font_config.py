#!/usr/bin/env python3
"""
字体配置工具
检测和配置GUI界面的中文字体支持
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.system = platform.system()
        self.available_fonts = []
        self.chinese_fonts = []
        self.recommended_fonts = []
        
    def detect_system_fonts(self) -> List[str]:
        """检测系统可用字体"""
        fonts = []
        
        try:
            if self.system == "Linux":
                # 使用fc-list命令检测字体
                result = subprocess.run(['fc-list'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            # 提取字体名称
                            parts = line.split(':')
                            if len(parts) >= 2:
                                font_name = parts[1].strip()
                                if font_name:
                                    fonts.append(font_name)
            
            elif self.system == "Windows":
                # Windows字体检测
                import winreg
                try:
                    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                                "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts")
                    i = 0
                    while True:
                        try:
                            font_name, _, _ = winreg.EnumValue(registry_key, i)
                            fonts.append(font_name)
                            i += 1
                        except WindowsError:
                            break
                    winreg.CloseKey(registry_key)
                except:
                    pass
            
            elif self.system == "Darwin":  # macOS
                # macOS字体检测
                result = subprocess.run(['system_profiler', 'SPFontsDataType'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # 解析字体信息
                    for line in result.stdout.split('\n'):
                        if 'Full Name:' in line:
                            font_name = line.split('Full Name:')[1].strip()
                            fonts.append(font_name)
        
        except Exception as e:
            print(f"字体检测失败: {e}")
        
        self.available_fonts = list(set(fonts))
        return self.available_fonts
    
    def detect_chinese_fonts(self) -> List[str]:
        """检测中文字体"""
        chinese_font_keywords = [
            'noto', 'cjk', 'chinese', 'zh', 'han', 'song', 'kai', 'hei',
            'wqy', 'wenquanyi', 'simsun', 'simhei', 'microsoft yahei',
            'pingfang', 'hiragino', 'source han', 'adobe', 'fangzheng'
        ]
        
        chinese_fonts = []
        
        for font in self.available_fonts:
            font_lower = font.lower()
            for keyword in chinese_font_keywords:
                if keyword in font_lower:
                    chinese_fonts.append(font)
                    break
        
        self.chinese_fonts = list(set(chinese_fonts))
        return self.chinese_fonts
    
    def get_recommended_fonts(self) -> List[str]:
        """获取推荐的中文字体"""
        # 按优先级排序的推荐字体
        priority_fonts = [
            'Noto Sans CJK SC',
            'Noto Sans CJK TC', 
            'Noto Sans CJK',
            'Source Han Sans',
            'WenQuanYi Zen Hei',
            'WenQuanYi Micro Hei',
            'Microsoft YaHei',
            'SimHei',
            'SimSun',
            'PingFang SC',
            'Hiragino Sans GB'
        ]
        
        recommended = []
        
        for priority_font in priority_fonts:
            for available_font in self.chinese_fonts:
                if priority_font.lower() in available_font.lower():
                    recommended.append(available_font)
                    break
        
        # 如果没有找到优先字体，添加所有中文字体
        if not recommended:
            recommended = self.chinese_fonts[:5]  # 最多5个
        
        self.recommended_fonts = recommended
        return recommended
    
    def get_best_font(self) -> Optional[str]:
        """获取最佳中文字体"""
        recommended = self.get_recommended_fonts()
        return recommended[0] if recommended else None
    
    def install_fonts_linux(self) -> bool:
        """在Linux上安装中文字体"""
        try:
            print("正在安装中文字体...")
            
            # 检查是否有sudo权限
            result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
            if result.returncode != 0:
                print("需要sudo权限来安装字体")
                return False
            
            # 安装字体包
            font_packages = [
                'fonts-noto-cjk',
                'fonts-wqy-zenhei', 
                'fonts-wqy-microhei',
                'fonts-arphic-ukai',
                'fonts-arphic-uming'
            ]
            
            for package in font_packages:
                print(f"安装 {package}...")
                result = subprocess.run(['sudo', 'apt', 'install', '-y', package],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {package} 安装成功")
                else:
                    print(f"⚠️ {package} 安装失败")
            
            # 更新字体缓存
            print("更新字体缓存...")
            subprocess.run(['fc-cache', '-fv'], capture_output=True)
            
            return True
            
        except Exception as e:
            print(f"字体安装失败: {e}")
            return False
    
    def generate_font_config(self) -> Dict[str, str]:
        """生成字体配置"""
        best_font = self.get_best_font()
        
        config = {
            'default_font': best_font or 'DejaVu Sans',
            'title_font': best_font or 'DejaVu Sans',
            'heading_font': best_font or 'DejaVu Sans',
            'info_font': best_font or 'DejaVu Sans',
            'fallback_fonts': ['DejaVu Sans', 'Liberation Sans', 'Arial']
        }
        
        return config
    
    def test_font_rendering(self, font_name: str) -> bool:
        """测试字体渲染"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            # 创建测试窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 测试中文文本
            test_text = "测试中文字体渲染：智能镜头检测与分段系统"
            
            # 创建测试标签
            label = ttk.Label(root, text=test_text, font=(font_name, 12))
            label.pack()
            
            # 更新显示
            root.update()
            
            # 获取文本尺寸
            width = label.winfo_reqwidth()
            height = label.winfo_reqheight()
            
            root.destroy()
            
            # 如果尺寸合理，说明字体可用
            return width > 100 and height > 10
            
        except Exception as e:
            print(f"字体测试失败: {e}")
            return False
    
    def generate_report(self) -> str:
        """生成字体检测报告"""
        self.detect_system_fonts()
        self.detect_chinese_fonts()
        recommended = self.get_recommended_fonts()
        best_font = self.get_best_font()
        
        report = f"""
# 字体检测报告

## 系统信息
- 操作系统: {self.system}
- Python版本: {sys.version}

## 字体统计
- 总字体数量: {len(self.available_fonts)}
- 中文字体数量: {len(self.chinese_fonts)}
- 推荐字体数量: {len(recommended)}

## 推荐字体列表
"""
        
        if recommended:
            for i, font in enumerate(recommended, 1):
                status = "✅ 可用" if self.test_font_rendering(font) else "⚠️ 可能有问题"
                report += f"{i}. {font} - {status}\n"
        else:
            report += "❌ 未找到推荐的中文字体\n"
        
        report += f"""
## 最佳字体
{best_font if best_font else "❌ 未找到合适的中文字体"}

## 所有中文字体
"""
        
        if self.chinese_fonts:
            for font in self.chinese_fonts[:10]:  # 只显示前10个
                report += f"- {font}\n"
            if len(self.chinese_fonts) > 10:
                report += f"... 还有 {len(self.chinese_fonts) - 10} 个字体\n"
        else:
            report += "❌ 未检测到中文字体\n"
        
        return report.strip()


def main():
    """主函数"""
    print("🔍 字体检测和配置工具")
    print("=" * 40)
    
    font_manager = FontManager()
    
    # 生成检测报告
    report = font_manager.generate_report()
    print(report)
    
    # 保存报告
    with open('font_detection_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存到: font_detection_report.txt")
    
    # 如果是Linux且没有中文字体，提供安装选项
    if font_manager.system == "Linux" and not font_manager.chinese_fonts:
        print("\n⚠️ 未检测到中文字体")
        response = input("是否安装中文字体? (y/N): ")
        if response.lower() == 'y':
            font_manager.install_fonts_linux()
            print("字体安装完成，请重新运行检测")
    
    # 生成字体配置
    config = font_manager.generate_font_config()
    print(f"\n🎨 推荐字体配置:")
    for key, value in config.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

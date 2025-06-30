#!/usr/bin/env python3
"""
剪映草稿管理器启动脚本

启动剪映草稿管理器GUI界面
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from draft_manager_gui import main
    
    if __name__ == "__main__":
        print("启动剪映草稿管理器...")
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖文件都在正确位置")
    sys.exit(1)
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)

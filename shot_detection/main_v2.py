#!/usr/bin/env python3
"""
Shot Detection v2.0 Main Entry Point
镜头检测v2.0主程序入口
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import init_config, get_config


def setup_environment():
    """设置运行环境"""
    # 初始化配置
    config = init_config()
    
    # 设置基础日志
    logger.add(
        "logs/shot_detection_v2.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO"
    )
    
    logger.info("Shot Detection v2.0 starting...")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Config path: {config.config_path}")
    
    return config


def run_gui():
    """运行GUI应用"""
    try:
        # 尝试使用新的GUI
        from gui.main_window import MainWindow
        import tkinter as tk

        logger.info("Starting new GUI application")

        root = tk.Tk()
        app = MainWindow(root)
        app.run()

    except ImportError as e:
        logger.warning(f"New GUI not available, falling back to legacy: {e}")
        try:
            # 回退到原有的GUI应用
            from gui_app import main as gui_main

            logger.info("Starting legacy GUI application")
            gui_main()

        except ImportError as e2:
            logger.error(f"GUI dependencies not available: {e2}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting GUI: {e}")
        sys.exit(1)


def run_cli(args):
    """运行命令行应用"""
    try:
        logger.info("CLI mode not yet implemented in v2.0")
        logger.info("Please use GUI mode for now")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error in CLI mode: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Shot Detection v2.0 - Advanced video shot boundary detection tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Run in command line mode (not yet implemented)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Shot Detection v2.0.0'
    )
    
    args = parser.parse_args()
    
    # 设置环境
    if args.config:
        config = init_config(args.config)
    else:
        config = setup_environment()
    
    # 设置调试模式
    if args.debug:
        config.set('advanced.debug_mode', True)
        logger.info("Debug mode enabled")
    
    try:
        if args.cli:
            run_cli(args)
        else:
            run_gui()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

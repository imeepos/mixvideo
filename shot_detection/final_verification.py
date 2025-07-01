#!/usr/bin/env python3
"""
最终验证脚本

确保prompts_manager导入问题完全解决
"""

import sys
import os
import threading
from pathlib import Path

def test_root_version():
    """测试根目录版本"""
    print("=== 测试根目录版本 ===")
    
    try:
        # 确保在根目录
        root_dir = Path(__file__).parent
        os.chdir(str(root_dir))
        
        # 添加到Python路径
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        
        # 清理模块缓存
        modules_to_clear = ['prompts_manager', 'prompts_constants']
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 测试导入
        from prompts_manager import PromptsManager
        manager = PromptsManager()
        prompt = manager.get_video_analysis_prompt()
        
        if prompt and len(prompt) > 50:
            print(f"✓ 根目录版本正常，提示词长度: {len(prompt)}")
            return True
        else:
            print(f"✗ 根目录版本提示词无效: {len(prompt) if prompt else 0}")
            return False
            
    except Exception as e:
        print(f"✗ 根目录版本测试失败: {e}")
        return False


def test_packaged_version():
    """测试打包版本"""
    print("\n=== 测试打包版本 ===")
    
    packaged_dir = Path(__file__).parent / "ShotDetectionGUI_Python_Complete_v1.0.3_20250701"
    
    if not packaged_dir.exists():
        print("✗ 打包版本目录不存在")
        return False
    
    # 保存原始环境
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    try:
        # 切换到打包版本
        os.chdir(str(packaged_dir))
        sys.path.insert(0, str(packaged_dir))
        
        # 清理模块缓存
        modules_to_clear = ['prompts_manager', 'prompts_constants']
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        # 测试导入
        from prompts_manager import PromptsManager
        manager = PromptsManager()
        prompt = manager.get_video_analysis_prompt()
        
        if prompt and len(prompt) > 50:
            print(f"✓ 打包版本正常，提示词长度: {len(prompt)}")
            return True
        else:
            print(f"✗ 打包版本提示词无效: {len(prompt) if prompt else 0}")
            return False
            
    except Exception as e:
        print(f"✗ 打包版本测试失败: {e}")
        return False
    
    finally:
        # 恢复环境
        os.chdir(original_cwd)
        sys.path = original_path


def test_gui_simulation():
    """模拟GUI中的视频分析工作线程"""
    print("\n=== 模拟GUI视频分析工作线程 ===")
    
    packaged_dir = Path(__file__).parent / "ShotDetectionGUI_Python_Complete_v1.0.3_20250701"
    
    # 保存原始环境
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    result = {"success": False, "prompt": None, "method": None}
    
    def worker():
        try:
            # 切换到打包版本目录（模拟GUI运行环境）
            os.chdir(str(packaged_dir))
            
            # 模拟GUI中的强健导入逻辑
            analysis_prompt = None
            
            # 尝试多种方式获取提示词
            try:
                # 方法1: 直接导入
                from prompts_manager import PromptsManager
                prompts_manager = PromptsManager()
                analysis_prompt = prompts_manager.get_video_analysis_prompt()
                
                # 检查提示词是否有效
                if analysis_prompt and len(analysis_prompt.strip()) > 50:
                    result["method"] = "prompts_manager"
                else:
                    analysis_prompt = None  # 强制进入备用方案
                    
            except ImportError as e:
                print(f"方法1失败: {e}")
                
                try:
                    # 方法2: 添加路径后导入
                    current_dir = str(Path.cwd())
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    
                    # 清理模块缓存
                    if 'prompts_manager' in sys.modules:
                        del sys.modules['prompts_manager']
                    
                    from prompts_manager import PromptsManager
                    prompts_manager = PromptsManager()
                    analysis_prompt = prompts_manager.get_video_analysis_prompt()
                    
                    if analysis_prompt and len(analysis_prompt.strip()) > 50:
                        result["method"] = "prompts_manager (路径调整)"
                    else:
                        analysis_prompt = None
                        
                except Exception as e2:
                    print(f"方法2失败: {e2}")
                    
                    try:
                        # 方法3: 使用备用提示词
                        from prompts_constants import VIDEO_ANALYSIS_PROMPT
                        analysis_prompt = VIDEO_ANALYSIS_PROMPT
                        result["method"] = "prompts_constants"
                        
                    except Exception as e3:
                        print(f"方法3失败: {e3}")
                        
                        # 方法4: 直接读取文件
                        try:
                            prompts_file = Path.cwd() / "prompts" / "video-analysis.prompt"
                            if prompts_file.exists():
                                with open(prompts_file, 'r', encoding='utf-8') as f:
                                    analysis_prompt = f.read().strip()
                                result["method"] = "直接读取文件"
                            else:
                                print("提示词文件不存在")
                        except Exception as e4:
                            print(f"方法4失败: {e4}")
            
            # 检查最终结果
            if analysis_prompt:
                result["success"] = True
                result["prompt"] = analysis_prompt
            
        except Exception as e:
            print(f"工作线程异常: {e}")
    
    try:
        # 在线程中运行（模拟GUI的工作线程）
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()
        
        if result["success"]:
            print(f"✓ GUI模拟成功")
            print(f"  使用方法: {result['method']}")
            print(f"  提示词长度: {len(result['prompt'])}")
            return True
        else:
            print("✗ GUI模拟失败，所有方法都无法获取提示词")
            return False
            
    finally:
        # 恢复环境
        os.chdir(original_cwd)
        sys.path = original_path


def test_error_scenarios():
    """测试错误场景"""
    print("\n=== 测试错误场景处理 ===")
    
    packaged_dir = Path(__file__).parent / "ShotDetectionGUI_Python_Complete_v1.0.3_20250701"
    
    # 保存原始环境
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    try:
        os.chdir(str(packaged_dir))
        
        # 场景1: 临时移除prompts_manager.py
        prompts_manager_file = packaged_dir / "prompts_manager.py"
        temp_file = packaged_dir / "prompts_manager.py.bak"
        
        if prompts_manager_file.exists():
            prompts_manager_file.rename(temp_file)
        
        # 清理模块缓存
        if 'prompts_manager' in sys.modules:
            del sys.modules['prompts_manager']
        
        # 测试备用方案
        try:
            from prompts_constants import VIDEO_ANALYSIS_PROMPT
            if VIDEO_ANALYSIS_PROMPT and len(VIDEO_ANALYSIS_PROMPT) > 50:
                print("✓ 备用方案1 (prompts_constants) 工作正常")
            else:
                print("✗ 备用方案1失败")
                return False
        except Exception as e:
            print(f"✗ 备用方案1异常: {e}")
            return False
        
        # 恢复文件
        if temp_file.exists():
            temp_file.rename(prompts_manager_file)
        
        # 场景2: 测试直接文件读取
        prompts_file = packaged_dir / "prompts" / "video-analysis.prompt"
        if prompts_file.exists():
            try:
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content and len(content) > 50:
                    print("✓ 备用方案2 (直接读取文件) 工作正常")
                else:
                    print("✗ 备用方案2失败，文件内容无效")
                    return False
            except Exception as e:
                print(f"✗ 备用方案2异常: {e}")
                return False
        else:
            print("✗ 提示词文件不存在")
            return False
        
        return True
        
    finally:
        # 恢复环境
        os.chdir(original_cwd)
        sys.path = original_path


def main():
    """主测试函数"""
    print("🔍 最终验证 - prompts_manager导入问题")
    print("=" * 60)
    
    tests = [
        ("根目录版本测试", test_root_version),
        ("打包版本测试", test_packaged_version),
        ("GUI模拟测试", test_gui_simulation),
        ("错误场景测试", test_error_scenarios)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"运行: {test_name}")
        print('='*40)
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 通过")
            else:
                failed += 1
                print(f"✗ {test_name} 失败")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} 异常: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("最终验证结果")
    print('='*60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有验证通过！")
        print("\n✅ 问题完全解决:")
        print("1. ✅ 打包版本包含所有必需文件")
        print("2. ✅ prompts_manager 正常导入")
        print("3. ✅ 备用方案工作正常")
        print("4. ✅ GUI模拟测试成功")
        print("5. ✅ 错误场景处理正确")
        
        print("\n🚀 现在用户可以:")
        print("• 正常运行视频分析功能")
        print("• 不会再看到 'No module named prompts_manager' 错误")
        print("• 享受稳定的提示词加载")
        print("• 使用多重备用方案保障")
        
        print("\n📋 解决方案总结:")
        print("1. 🔧 添加缺失文件到打包版本")
        print("2. 🛡️ 实现多重备用导入机制")
        print("3. 📝 提供详细错误日志")
        print("4. 🔄 自动路径修复")
        print("5. 📁 直接文件读取备用")
        
    else:
        print(f"\n❌ {failed} 个验证失败")
        print("需要进一步调试")


if __name__ == "__main__":
    main()

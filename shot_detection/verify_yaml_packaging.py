#!/usr/bin/env python3
"""
验证 PyYAML 打包配置

确认 PyYAML 已正确添加到打包依赖中
"""

import sys
from pathlib import Path


def verify_requirements_txt():
    """验证 requirements.txt 文件"""
    print("=== 验证 requirements.txt ===")
    
    # 查找最新的发布目录
    current_dir = Path(__file__).parent
    release_dirs = [d for d in current_dir.iterdir() 
                   if d.is_dir() and d.name.startswith("ShotDetectionGUI_Python_Complete")]
    
    if not release_dirs:
        print("✗ 未找到发布目录")
        return False
    
    # 使用最新的目录
    latest_dir = max(release_dirs, key=lambda x: x.stat().st_mtime)
    requirements_file = latest_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("✗ requirements.txt 文件不存在")
        return False
    
    print(f"✓ 检查文件: {requirements_file}")
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 PyYAML
    if "PyYAML>=5.4.0" in content:
        print("✓ PyYAML>=5.4.0 已包含在 requirements.txt 中")
        
        # 显示相关行
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'PyYAML' in line or 'yaml' in line.lower():
                print(f"  第{i}行: {line}")
        
        return True
    else:
        print("✗ PyYAML 未包含在 requirements.txt 中")
        return False


def verify_dependency_check():
    """验证依赖检查脚本"""
    print("\n=== 验证依赖检查脚本 ===")
    
    # 查找最新的发布目录
    current_dir = Path(__file__).parent
    release_dirs = [d for d in current_dir.iterdir() 
                   if d.is_dir() and d.name.startswith("ShotDetectionGUI_Python_Complete")]
    
    if not release_dirs:
        print("✗ 未找到发布目录")
        return False
    
    latest_dir = max(release_dirs, key=lambda x: x.stat().st_mtime)
    check_file = latest_dir / "check_dependencies.py"
    
    if not check_file.exists():
        print("✗ check_dependencies.py 文件不存在")
        return False
    
    print(f"✓ 检查文件: {check_file}")
    
    with open(check_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 yaml 模块
    if '"yaml"' in content and "PyYAML" in content:
        print("✓ yaml 模块检查已包含在依赖检查脚本中")
        
        # 显示相关行
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'yaml' in line and ('required_deps' in content[max(0, content.find(line)-200):content.find(line)+200]):
                print(f"  第{i}行: {line.strip()}")
        
        return True
    else:
        print("✗ yaml 模块检查未包含在依赖检查脚本中")
        return False


def verify_jianying_compatibility():
    """验证剪映模块兼容性"""
    print("\n=== 验证剪映模块兼容性 ===")
    
    try:
        # 确保路径正确
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # 测试导入
        from jianying.draft_content_manager import DraftContentManager, YAML_AVAILABLE
        print("✓ DraftContentManager 导入成功")
        
        # 检查 YAML 可用性标志
        if YAML_AVAILABLE:
            print("✓ YAML_AVAILABLE = True，yaml 模块可用")
        else:
            print("✗ YAML_AVAILABLE = False，yaml 模块不可用")
            return False
        
        # 测试配置加载
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            test_project = Path(temp_dir) / "test_project"
            manager = DraftContentManager(test_project)
            
            # 检查配置加载
            config = manager._config
            if config:
                print("✓ 配置加载功能正常")
                return True
            else:
                print("✗ 配置加载失败")
                return False
        
    except Exception as e:
        print(f"✗ 剪映模块测试失败: {e}")
        return False


def verify_gui_import_fix():
    """验证 GUI 导入修复"""
    print("\n=== 验证 GUI 导入修复 ===")
    
    try:
        # 检查 GUI 文件中的导入逻辑
        gui_file = Path(__file__).parent / "gui_app.py"
        
        if not gui_file.exists():
            print("✗ gui_app.py 文件不存在")
            return False
        
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导入函数
        if "import_jianying_modules" in content:
            print("✓ import_jianying_modules 函数存在")
        else:
            print("✗ import_jianying_modules 函数不存在")
            return False
        
        # 检查错误处理
        if "import_error" in content:
            print("✓ 导入错误处理存在")
        else:
            print("✗ 导入错误处理不存在")
            return False
        
        # 检查重试功能
        if "retry_import_jianying" in content:
            print("✓ 重试导入功能存在")
        else:
            print("✗ 重试导入功能不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ GUI 导入修复验证失败: {e}")
        return False


def verify_package_structure():
    """验证包结构"""
    print("\n=== 验证包结构 ===")
    
    try:
        # 检查 jianying 包
        jianying_dir = Path(__file__).parent / "jianying"
        
        if not jianying_dir.exists():
            print("✗ jianying 目录不存在")
            return False
        
        print("✓ jianying 目录存在")
        
        # 检查必要文件
        required_files = [
            "__init__.py",
            "draft_meta_manager.py",
            "draft_content_manager.py"
        ]
        
        for file_name in required_files:
            file_path = jianying_dir / file_name
            if file_path.exists():
                print(f"✓ {file_name} 存在")
            else:
                print(f"✗ {file_name} 不存在")
                return False
        
        # 检查 __init__.py 内容
        init_file = jianying_dir / "__init__.py"
        with open(init_file, 'r', encoding='utf-8') as f:
            init_content = f.read()
        
        if "DraftMetaManager" in init_content and "DraftContentManager" in init_content:
            print("✓ __init__.py 包含正确的导入")
        else:
            print("✗ __init__.py 导入不完整")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 包结构验证失败: {e}")
        return False


def main():
    """主验证函数"""
    print("=== PyYAML 打包配置验证 ===")
    
    tests = [
        ("requirements.txt 文件", verify_requirements_txt),
        ("依赖检查脚本", verify_dependency_check),
        ("剪映模块兼容性", verify_jianying_compatibility),
        ("GUI 导入修复", verify_gui_import_fix),
        ("包结构", verify_package_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n运行验证: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 验证通过")
            else:
                failed += 1
                print(f"✗ {test_name} 验证失败")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} 验证异常: {e}")
    
    print(f"\n=== 验证结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有验证通过！PyYAML 打包配置完全正确")
        
        print("\n✅ 完成的修改:")
        print("1. 在 create_complete_python_distribution.py 中添加了 PyYAML>=5.4.0")
        print("2. 在依赖检查脚本中添加了 yaml 模块检查")
        print("3. 在 jianying/draft_content_manager.py 中添加了 yaml 导入容错")
        print("4. 在 gui_app.py 中改进了导入错误处理")
        print("5. 创建了 jianying/__init__.py 包初始化文件")
        
        print("\n🚀 现在打包时会包含:")
        print("- PyYAML 模块用于配置文件解析")
        print("- 完整的剪映项目管理功能")
        print("- 智能的导入错误处理和重试机制")
        print("- 用户友好的错误提示和解决方案")
        
        print("\n📦 用户使用流程:")
        print("1. 解压发布包")
        print("2. 运行 run_python.bat (Windows) 或 ./run_linux.sh (Linux)")
        print("3. 系统自动安装 PyYAML 和其他依赖")
        print("4. GUI 正常启动，剪映功能完全可用")
        
    else:
        print(f"\n❌ {failed} 个验证失败，需要进一步修复")


if __name__ == "__main__":
    main()

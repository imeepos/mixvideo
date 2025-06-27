#!/usr/bin/env python3
"""
测试 import_to_jianying.py 中的路径是否正确
"""

import os
import sys


def test_template_paths():
    """测试模板文件路径是否存在"""
    print("🔍 测试剪映模板文件路径...")

    # 获取脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"脚本目录: {current_dir}")

    # 测试 draft_content.json 路径
    draft_content_path = os.path.join(current_dir, "jianying", "draft_content.json")
    print(f"draft_content.json 路径: {draft_content_path}")

    if os.path.exists(draft_content_path):
        print("✅ draft_content.json 文件存在")
        # 检查文件大小
        file_size = os.path.getsize(draft_content_path)
        print(f"   文件大小: {file_size:,} 字节")
    else:
        print("❌ draft_content.json 文件不存在")
        return False

    # 测试 draft_meta_info.json 路径
    meta_info_path = os.path.join(current_dir, "jianying", "draft_meta_info.json")
    print(f"draft_meta_info.json 路径: {meta_info_path}")

    if os.path.exists(meta_info_path):
        print("✅ draft_meta_info.json 文件存在")
        # 检查文件大小
        file_size = os.path.getsize(meta_info_path)
        print(f"   文件大小: {file_size:,} 字节")
    else:
        print("❌ draft_meta_info.json 文件不存在")
        return False

    return True


def test_json_validity():
    """测试 JSON 文件是否有效"""
    print("\n📋 测试 JSON 文件有效性...")

    import json

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 测试 draft_content.json
    try:
        draft_content_path = os.path.join(current_dir, "jianying", "draft_content.json")
        with open(draft_content_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ draft_content.json JSON 格式有效")
        print(f"   包含键: {list(data.keys())[:5]}...")  # 显示前5个键
    except json.JSONDecodeError as e:
        print(f"❌ draft_content.json JSON 格式无效: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取 draft_content.json 失败: {e}")
        return False

    # 测试 draft_meta_info.json
    try:
        meta_info_path = os.path.join(current_dir, "jianying", "draft_meta_info.json")
        with open(meta_info_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ draft_meta_info.json JSON 格式有效")
        print(f"   包含键: {list(data.keys())}")
    except json.JSONDecodeError as e:
        print(f"❌ draft_meta_info.json JSON 格式无效: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取 draft_meta_info.json 失败: {e}")
        return False

    return True


def test_import_functionality():
    """测试导入功能的核心函数"""
    print("\n🔧 测试导入功能...")

    try:
        # 导入主模块
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import import_to_jianying

        print("✅ 成功导入 import_to_jianying 模块")

        # 测试函数是否存在
        functions_to_test = [
            "get_video_metadata",
            "create_new_project_json",
            "generate_random_draft_id",
            "copy_to_jianying_draft",
        ]

        for func_name in functions_to_test:
            if hasattr(import_to_jianying, func_name):
                print(f"✅ 函数 {func_name} 存在")
            else:
                print(f"❌ 函数 {func_name} 不存在")
                return False

        # 测试生成随机草稿ID
        draft_id = import_to_jianying.generate_random_draft_id()
        print(f"✅ 生成草稿ID: {draft_id}")

        return True

    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试导入功能失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🎬 剪映导入工具路径测试")
    print("=" * 50)

    all_tests_passed = True

    # 测试模板文件路径
    if not test_template_paths():
        all_tests_passed = False

    # 测试 JSON 文件有效性
    if not test_json_validity():
        all_tests_passed = False

    # 测试导入功能
    if not test_import_functionality():
        all_tests_passed = False

    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有测试通过！路径修复成功。")
        print("\n📝 使用说明:")
        print("1. 确保安装了 ffprobe (FFmpeg)")
        print("2. 运行: python3 scripts/import_to_jianying.py")
        print("3. 选择要导入的 MP4 视频文件")
        print("4. 点击'导入到剪映'按钮")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

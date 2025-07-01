#!/usr/bin/env python3
"""
剪映项目管理系统测试

测试所有组件的功能
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import unittest

# 导入要测试的模块
from jianying.jianying_project_manager import JianyingProjectManager
from jianying.draft_meta_manager import DraftMetaManager
from jianying.draft_content_manager import DraftContentManager


class TestJianyingManager(unittest.TestCase):
    """剪映管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时测试目录
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = JianyingProjectManager(self.test_dir)
        
        # 创建测试项目目录
        self.valid_project_dir = self.test_dir / "valid_project"
        self.invalid_project_dir = self.test_dir / "invalid_project"
        
        self.valid_project_dir.mkdir()
        self.invalid_project_dir.mkdir()
        
        # 创建有效项目的JSON文件
        self.create_valid_project_files()
        
        # 创建无效项目（缺少文件）
        (self.invalid_project_dir / "draft_content.json").write_text("{}")
        # 故意不创建其他文件
    
    def tearDown(self):
        """测试后清理"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_valid_project_files(self):
        """创建有效项目的JSON文件"""
        # draft_content.json
        content_data = {
            "duration": 30000000,
            "materials": {
                "videos": [],
                "audios": [],
                "images": []
            },
            "tracks": []
        }
        
        with open(self.valid_project_dir / "draft_content.json", 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2)
        
        # draft_meta_info.json
        meta_data = {
            "draft_materials": [[], [], [], [], [], [], []],
            "draft_root": str(self.valid_project_dir),
            "create_time": 1640995200000000,
            "update_time": 1640995200000000
        }
        
        with open(self.valid_project_dir / "draft_meta_info.json", 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2)
        
        # draft_virtual_store.json
        store_data = {
            "store_data": {}
        }
        
        with open(self.valid_project_dir / "draft_virtual_store.json", 'w', encoding='utf-8') as f:
            json.dump(store_data, f, indent=2)
    
    def test_scan_projects(self):
        """测试项目扫描"""
        projects = self.manager.scan_projects()
        
        # 应该发现2个项目
        self.assertEqual(len(projects), 2)
        
        # 检查项目名称
        project_names = [p.name for p in projects]
        self.assertIn("valid_project", project_names)
        self.assertIn("invalid_project", project_names)
        
        # 检查有效性
        valid_projects = [p for p in projects if p.is_valid]
        invalid_projects = [p for p in projects if not p.is_valid]
        
        self.assertEqual(len(valid_projects), 1)
        self.assertEqual(len(invalid_projects), 1)
        
        self.assertEqual(valid_projects[0].name, "valid_project")
        self.assertEqual(invalid_projects[0].name, "invalid_project")
    
    def test_get_project(self):
        """测试获取项目"""
        self.manager.scan_projects()
        
        # 获取存在的项目
        project = self.manager.get_project("valid_project")
        self.assertIsNotNone(project)
        self.assertTrue(project.is_valid)
        
        # 获取不存在的项目
        project = self.manager.get_project("nonexistent")
        self.assertIsNone(project)
    
    def test_get_valid_projects(self):
        """测试获取有效项目"""
        self.manager.scan_projects()
        
        valid_projects = self.manager.get_valid_projects()
        self.assertEqual(len(valid_projects), 1)
        self.assertEqual(valid_projects[0].name, "valid_project")
    
    def test_create_new_project(self):
        """测试创建新项目"""
        project_name = "new_test_project"
        
        # 创建项目
        success = self.manager.create_new_project(project_name)
        self.assertTrue(success)
        
        # 验证项目已创建
        project_dir = self.test_dir / project_name
        self.assertTrue(project_dir.exists())
        
        # 验证JSON文件已创建
        self.assertTrue((project_dir / "draft_content.json").exists())
        self.assertTrue((project_dir / "draft_meta_info.json").exists())
        self.assertTrue((project_dir / "draft_virtual_store.json").exists())
        
        # 重新扫描并验证项目有效
        projects = self.manager.scan_projects()
        new_project = self.manager.get_project(project_name)
        self.assertIsNotNone(new_project)
        self.assertTrue(new_project.is_valid)
    
    def test_delete_project(self):
        """测试删除项目"""
        self.manager.scan_projects()
        
        # 删除项目
        success = self.manager.delete_project("valid_project")
        self.assertTrue(success)
        
        # 验证项目目录已删除
        self.assertFalse(self.valid_project_dir.exists())
        
        # 验证项目不再存在于管理器中
        project = self.manager.get_project("valid_project")
        self.assertIsNone(project)
    
    def test_get_project_summary(self):
        """测试获取项目摘要"""
        self.manager.scan_projects()
        
        summary = self.manager.get_project_summary()
        
        # 检查摘要结构
        self.assertIn("base_directory", summary)
        self.assertIn("total_projects", summary)
        self.assertIn("valid_projects", summary)
        self.assertIn("invalid_projects", summary)
        self.assertIn("valid_project_names", summary)
        self.assertIn("invalid_project_info", summary)
        
        # 检查数值
        self.assertEqual(summary["total_projects"], 2)
        self.assertEqual(summary["valid_projects"], 1)
        self.assertEqual(summary["invalid_projects"], 1)
        
        # 检查项目名称
        self.assertIn("valid_project", summary["valid_project_names"])
    
    def test_get_project_managers(self):
        """测试获取项目管理器"""
        self.manager.scan_projects()
        
        # 获取有效项目的管理器
        content_mgr = self.manager.get_project_content_manager("valid_project")
        meta_mgr = self.manager.get_project_meta_manager("valid_project")
        
        self.assertIsNotNone(content_mgr)
        self.assertIsNotNone(meta_mgr)
        self.assertIsInstance(content_mgr, DraftContentManager)
        self.assertIsInstance(meta_mgr, DraftMetaManager)
        
        # 获取无效项目的管理器
        content_mgr = self.manager.get_project_content_manager("invalid_project")
        meta_mgr = self.manager.get_project_meta_manager("invalid_project")
        
        self.assertIsNone(content_mgr)
        self.assertIsNone(meta_mgr)
        
        # 获取不存在项目的管理器
        content_mgr = self.manager.get_project_content_manager("nonexistent")
        meta_mgr = self.manager.get_project_meta_manager("nonexistent")
        
        self.assertIsNone(content_mgr)
        self.assertIsNone(meta_mgr)


def run_integration_test():
    """运行集成测试"""
    print("🧪 运行剪映管理系统集成测试")
    print("=" * 50)
    
    # 创建临时测试环境
    test_dir = Path(tempfile.mkdtemp())
    print(f"测试目录: {test_dir}")
    
    try:
        # 1. 测试项目管理器
        print("\n1. 测试项目管理器...")
        manager = JianyingProjectManager(test_dir)
        
        # 2. 创建测试项目
        print("2. 创建测试项目...")
        success = manager.create_new_project("test_project_1")
        print(f"   创建项目1: {'成功' if success else '失败'}")
        
        success = manager.create_new_project("test_project_2")
        print(f"   创建项目2: {'成功' if success else '失败'}")
        
        # 3. 扫描项目
        print("3. 扫描项目...")
        projects = manager.scan_projects()
        print(f"   发现项目: {len(projects)} 个")
        
        for project in projects:
            status = "有效" if project.is_valid else "无效"
            print(f"   - {project.name}: {status}")
        
        # 4. 测试项目管理器
        print("4. 测试项目管理器...")
        for project in manager.get_valid_projects():
            print(f"   处理项目: {project.name}")
            
            # 获取内容管理器
            content_mgr = manager.get_project_content_manager(project.name)
            if content_mgr:
                info = content_mgr.get_project_info()
                print(f"     内容管理器: 可用，时长 {info.get('duration', 0) / 1000000:.2f} 秒")
            
            # 获取元数据管理器
            meta_mgr = manager.get_project_meta_manager(project.name)
            if meta_mgr:
                materials = meta_mgr.get_all_materials()
                print(f"     元数据管理器: 可用，素材 {len(materials)} 个")
        
        # 5. 测试项目摘要
        print("5. 测试项目摘要...")
        summary = manager.get_project_summary()
        print(f"   总项目数: {summary['total_projects']}")
        print(f"   有效项目: {summary['valid_projects']}")
        print(f"   无效项目: {summary['invalid_projects']}")
        
        # 6. 测试删除项目
        print("6. 测试删除项目...")
        success = manager.delete_project("test_project_1")
        print(f"   删除项目1: {'成功' if success else '失败'}")
        
        # 重新扫描验证
        projects = manager.scan_projects()
        print(f"   删除后剩余项目: {len(projects)} 个")
        
        print("\n✅ 集成测试完成")
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理测试目录
        if test_dir.exists():
            shutil.rmtree(test_dir)
        print(f"已清理测试目录: {test_dir}")


def main():
    """主函数"""
    print("🔧 剪映项目管理系统测试")
    print("=" * 60)
    
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 60)
    
    # 运行集成测试
    run_integration_test()


if __name__ == "__main__":
    main()

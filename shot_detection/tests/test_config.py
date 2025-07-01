"""
Unit Tests for Config Module
配置模块单元测试
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
import yaml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import ConfigManager, get_config


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
        
        # 创建测试配置文件
        test_config = {
            "app": {
                "name": "Test App",
                "version": "1.0.0",
                "log_level": "INFO"
            },
            "detection": {
                "default_detector": "frame_difference",
                "frame_difference": {
                    "threshold": 0.3
                }
            },
            "processing": {
                "output": {
                    "format": "mp4",
                    "quality": "high"
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_config(self):
        """测试加载配置"""
        config_manager = ConfigManager(self.config_file)
        
        self.assertEqual(config_manager.get('app.name'), "Test App")
        self.assertEqual(config_manager.get('app.version'), "1.0.0")
        self.assertEqual(config_manager.get('detection.default_detector'), "frame_difference")
    
    def test_get_with_default(self):
        """测试获取配置值（带默认值）"""
        config_manager = ConfigManager(self.config_file)
        
        # 存在的键
        self.assertEqual(config_manager.get('app.name'), "Test App")
        
        # 不存在的键，使用默认值
        self.assertEqual(config_manager.get('nonexistent.key', 'default'), 'default')
        
        # 不存在的键，无默认值
        self.assertIsNone(config_manager.get('nonexistent.key'))
    
    def test_set_config(self):
        """测试设置配置值"""
        config_manager = ConfigManager(self.config_file)
        
        # 设置新值
        config_manager.set('app.name', 'New App Name')
        self.assertEqual(config_manager.get('app.name'), 'New App Name')
        
        # 设置嵌套值
        config_manager.set('new.nested.key', 'nested_value')
        self.assertEqual(config_manager.get('new.nested.key'), 'nested_value')
    
    def test_save_config(self):
        """测试保存配置"""
        config_manager = ConfigManager(self.config_file)
        
        # 修改配置
        config_manager.set('app.name', 'Modified App')
        
        # 保存配置
        config_manager.save_config()
        
        # 重新加载验证
        new_config_manager = ConfigManager(self.config_file)
        self.assertEqual(new_config_manager.get('app.name'), 'Modified App')
    
    def test_get_detection_config(self):
        """测试获取检测配置"""
        config_manager = ConfigManager(self.config_file)
        
        detection_config = config_manager.get_detection_config()
        
        self.assertIsInstance(detection_config, dict)
        self.assertEqual(detection_config['default_detector'], 'frame_difference')
        self.assertIn('frame_difference', detection_config)
    
    def test_get_processing_config(self):
        """测试获取处理配置"""
        config_manager = ConfigManager(self.config_file)
        
        processing_config = config_manager.get_processing_config()
        
        self.assertIsInstance(processing_config, dict)
        self.assertIn('output', processing_config)
        self.assertEqual(processing_config['output']['format'], 'mp4')
    
    def test_get_gui_config(self):
        """测试获取GUI配置"""
        config_manager = ConfigManager(self.config_file)
        
        gui_config = config_manager.get_gui_config()
        
        self.assertIsInstance(gui_config, dict)
        # GUI配置可能为空，但应该返回字典
    
    def test_get_jianying_config(self):
        """测试获取剪映配置"""
        config_manager = ConfigManager(self.config_file)
        
        jianying_config = config_manager.get_jianying_config()
        
        self.assertIsInstance(jianying_config, dict)
        # 剪映配置可能为空，但应该返回字典
    
    def test_validate_config(self):
        """测试配置验证"""
        config_manager = ConfigManager(self.config_file)
        
        # 测试有效配置
        is_valid, errors = config_manager.validate_config()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_reset_to_defaults(self):
        """测试重置为默认值"""
        config_manager = ConfigManager(self.config_file)
        
        # 修改配置
        config_manager.set('app.name', 'Modified')
        
        # 重置为默认值
        config_manager.reset_to_defaults()
        
        # 验证重置结果
        self.assertEqual(config_manager.get('app.name'), 'Shot Detection')
    
    def test_backup_and_restore(self):
        """测试备份和恢复"""
        config_manager = ConfigManager(self.config_file)
        
        # 创建备份
        backup_file = config_manager.create_backup()
        self.assertTrue(Path(backup_file).exists())
        
        # 修改配置
        config_manager.set('app.name', 'Modified')
        
        # 恢复备份
        success = config_manager.restore_backup(backup_file)
        self.assertTrue(success)
        self.assertEqual(config_manager.get('app.name'), 'Test App')
        
        # 清理备份文件
        Path(backup_file).unlink()
    
    def test_config_file_not_exists(self):
        """测试配置文件不存在的情况"""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.yaml"
        
        config_manager = ConfigManager(nonexistent_file)
        
        # 应该使用默认配置
        self.assertEqual(config_manager.get('app.name'), 'Shot Detection')
    
    def test_invalid_config_file(self):
        """测试无效配置文件"""
        invalid_file = Path(self.temp_dir) / "invalid.yaml"
        
        # 创建无效的YAML文件
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # 应该能够处理无效文件并使用默认配置
        config_manager = ConfigManager(invalid_file)
        self.assertEqual(config_manager.get('app.name'), 'Shot Detection')


class TestGlobalConfig(unittest.TestCase):
    """全局配置测试"""
    
    def test_get_config_singleton(self):
        """测试全局配置单例"""
        config1 = get_config()
        config2 = get_config()
        
        # 应该返回同一个实例
        self.assertIs(config1, config2)
    
    def test_config_properties(self):
        """测试配置属性"""
        config = get_config()
        
        # 测试基本属性
        self.assertIsInstance(config.get('app.name'), str)
        self.assertIsInstance(config.get('app.version'), str)
        
        # 测试配置方法
        detection_config = config.get_detection_config()
        self.assertIsInstance(detection_config, dict)
        
        processing_config = config.get_processing_config()
        self.assertIsInstance(processing_config, dict)


class TestConfigValidation(unittest.TestCase):
    """配置验证测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_config(self):
        """测试有效配置"""
        valid_config = {
            "app": {
                "name": "Test App",
                "version": "1.0.0",
                "log_level": "INFO"
            },
            "detection": {
                "default_detector": "frame_difference",
                "frame_difference": {
                    "threshold": 0.3
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(valid_config, f)
        
        config_manager = ConfigManager(self.config_file)
        is_valid, errors = config_manager.validate_config()
        
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_threshold(self):
        """测试无效阈值"""
        invalid_config = {
            "detection": {
                "frame_difference": {
                    "threshold": 2.0  # 无效值，应该在0-1之间
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(invalid_config, f)
        
        config_manager = ConfigManager(self.config_file)
        is_valid, errors = config_manager.validate_config()
        
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        incomplete_config = {
            "app": {
                # 缺少name字段
                "version": "1.0.0"
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(incomplete_config, f)
        
        config_manager = ConfigManager(self.config_file)
        is_valid, errors = config_manager.validate_config()
        
        # 由于使用了默认值合并，应该仍然有效
        self.assertTrue(is_valid)


class TestConfigEnvironment(unittest.TestCase):
    """配置环境测试"""
    
    @patch.dict('os.environ', {'SHOT_DETECTION_LOG_LEVEL': 'DEBUG'})
    def test_environment_override(self):
        """测试环境变量覆盖"""
        # 这个测试需要ConfigManager支持环境变量覆盖
        # 目前的实现可能不支持，这是一个扩展功能
        pass
    
    def test_config_paths(self):
        """测试配置路径"""
        config = get_config()
        
        # 配置路径应该存在
        self.assertTrue(config.config_path.exists())
        
        # 配置路径应该是绝对路径
        self.assertTrue(config.config_path.is_absolute())


if __name__ == '__main__':
    unittest.main()

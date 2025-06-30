#!/usr/bin/env python3
"""
测试JSON修复功能
验证JSON文件的完整性和可读性
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation
from utils.json_utils import safe_json_dump, safe_json_dumps, sanitize_for_json
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def test_json_serialization():
    """测试JSON序列化功能"""
    logger.info("🧪 测试JSON序列化功能")
    
    # 测试数据包含各种可能的类型
    import numpy as np
    
    test_data = {
        "string": "测试字符串",
        "integer": 42,
        "float": 3.14159,
        "boolean": True,
        "none": None,
        "list": [1, 2, 3],
        "numpy_int": np.int32(123),
        "numpy_float": np.float32(456.789),
        "numpy_array": np.array([1, 2, 3, 4, 5]),
        "numpy_bool": np.bool_(True),
        "nested": {
            "inner_numpy": np.float64(999.999),
            "inner_list": [np.int64(111), np.float32(222.333)]
        }
    }
    
    # 测试清理函数
    logger.info("测试数据清理...")
    cleaned_data = sanitize_for_json(test_data)
    
    # 测试JSON字符串转换
    logger.info("测试JSON字符串转换...")
    json_str = safe_json_dumps(cleaned_data)
    
    # 验证可以重新解析
    try:
        parsed_data = json.loads(json_str)
        logger.info("✅ JSON字符串转换和解析成功")
        
        # 显示部分结果
        logger.info(f"原始numpy_int类型: {type(test_data['numpy_int'])}")
        logger.info(f"清理后类型: {type(cleaned_data['numpy_int'])}")
        logger.info(f"解析后值: {parsed_data['numpy_int']}")
        
    except Exception as e:
        logger.error(f"❌ JSON解析失败: {e}")
        return False
    
    # 测试文件导出
    test_file = "test_json_output.json"
    logger.info(f"测试文件导出: {test_file}")
    
    if safe_json_dump(cleaned_data, test_file):
        logger.info("✅ JSON文件导出成功")
        
        # 验证文件内容
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            logger.info("✅ JSON文件读取成功")
            
            # 清理测试文件
            os.remove(test_file)
            
        except Exception as e:
            logger.error(f"❌ JSON文件读取失败: {e}")
            return False
    else:
        logger.error("❌ JSON文件导出失败")
        return False
    
    return True


def test_video_processing_json():
    """测试视频处理后的JSON输出"""
    logger.info("🎬 测试视频处理JSON输出")
    
    video_path = "test_video.mp4"
    output_dir = "json_test_output"
    
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 执行视频处理
    logger.info("执行视频处理...")
    success = process_video_segmentation(
        video_path,
        output_dir,
        "duration",
        "medium"
    )
    
    if not success:
        logger.error("视频处理失败")
        return False
    
    # 检查生成的JSON文件
    output_path = Path(output_dir)
    json_files = [
        "detection_results.json",
        "quality_metrics.json"
    ]
    
    all_valid = True
    
    for json_file in json_files:
        file_path = output_path / json_file
        
        if not file_path.exists():
            logger.error(f"❌ JSON文件不存在: {json_file}")
            all_valid = False
            continue
        
        logger.info(f"验证JSON文件: {json_file}")
        
        try:
            # 读取并解析JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查文件大小
            file_size = file_path.stat().st_size
            logger.info(f"  文件大小: {file_size} bytes")
            
            if file_size < 100:  # 文件太小可能不完整
                logger.warning(f"  ⚠️ 文件可能不完整 (< 100 bytes)")
            
            # 检查数据结构
            if isinstance(data, dict):
                logger.info(f"  ✅ JSON结构有效，包含 {len(data)} 个顶级键")
                
                # 显示主要键
                main_keys = list(data.keys())[:5]  # 显示前5个键
                logger.info(f"  主要键: {main_keys}")
                
                # 递归检查数据完整性
                def check_completeness(obj, path="root", max_depth=3):
                    if max_depth <= 0:
                        return True
                    
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if value is None:
                                logger.debug(f"    发现null值: {path}.{key}")
                            elif isinstance(value, (dict, list)):
                                check_completeness(value, f"{path}.{key}", max_depth-1)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj[:3]):  # 只检查前3个元素
                            check_completeness(item, f"{path}[{i}]", max_depth-1)
                    
                    return True
                
                check_completeness(data)
                
            else:
                logger.error(f"  ❌ JSON根对象不是字典类型")
                all_valid = False
            
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON解析错误: {e}")
            all_valid = False
        except Exception as e:
            logger.error(f"  ❌ 文件读取错误: {e}")
            all_valid = False
    
    return all_valid


def validate_json_content():
    """验证JSON内容的完整性"""
    logger.info("🔍 验证JSON内容完整性")
    
    output_dir = "json_test_output"
    detection_file = Path(output_dir) / "detection_results.json"
    quality_file = Path(output_dir) / "quality_metrics.json"
    
    if not detection_file.exists():
        logger.error("检测结果文件不存在")
        return False
    
    try:
        # 验证检测结果文件
        with open(detection_file, 'r', encoding='utf-8') as f:
            detection_data = json.load(f)
        
        logger.info("检测结果文件内容验证:")
        
        # 检查必需的字段
        required_fields = ["metadata", "detection_info", "boundaries", "segments", "summary"]
        for field in required_fields:
            if field in detection_data:
                logger.info(f"  ✅ {field}: 存在")
                
                if field == "boundaries" and isinstance(detection_data[field], list):
                    logger.info(f"    边界数量: {len(detection_data[field])}")
                elif field == "segments" and isinstance(detection_data[field], list):
                    logger.info(f"    分段数量: {len(detection_data[field])}")
                elif field == "summary" and isinstance(detection_data[field], dict):
                    summary = detection_data[field]
                    logger.info(f"    总时长: {summary.get('total_duration', 'N/A')}s")
                    logger.info(f"    平均分段时长: {summary.get('average_segment_duration', 'N/A')}s")
            else:
                logger.error(f"  ❌ {field}: 缺失")
        
        # 验证质量指标文件
        if quality_file.exists():
            with open(quality_file, 'r', encoding='utf-8') as f:
                quality_data = json.load(f)
            
            logger.info("质量指标文件内容验证:")
            quality_fields = ["detection_metrics", "segment_metrics", "quality_thresholds"]
            for field in quality_fields:
                if field in quality_data:
                    logger.info(f"  ✅ {field}: 存在")
                else:
                    logger.error(f"  ❌ {field}: 缺失")
        
        return True
        
    except Exception as e:
        logger.error(f"验证过程中出错: {e}")
        return False


def main():
    """主测试函数"""
    setup_logging()
    
    logger.info("🧪 JSON修复功能测试")
    logger.info("=" * 50)
    
    tests = [
        ("JSON序列化功能", test_json_serialization),
        ("视频处理JSON输出", test_video_processing_json),
        ("JSON内容完整性", validate_json_content)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔬 执行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: 通过")
            else:
                logger.error(f"❌ {test_name}: 失败")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果汇总:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
    
    logger.info(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过，JSON修复功能正常！")
        return True
    else:
        logger.error("⚠️ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

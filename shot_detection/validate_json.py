#!/usr/bin/env python3
"""
JSON文件验证工具
验证生成的JSON文件的完整性和正确性
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def validate_detection_results_json(file_path: str) -> bool:
    """验证检测结果JSON文件"""
    logger.info(f"验证检测结果文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查顶级结构
        required_keys = ["metadata", "detection_info", "boundaries", "segments", "summary"]
        missing_keys = []
        
        for key in required_keys:
            if key not in data:
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"缺失必需的键: {missing_keys}")
            return False
        
        # 验证metadata
        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            logger.error("metadata不是字典类型")
            return False
        
        logger.info(f"  版本: {metadata.get('version', 'N/A')}")
        logger.info(f"  视频路径: {metadata.get('video_path', 'N/A')}")
        
        # 验证detection_info
        detection_info = data["detection_info"]
        if not isinstance(detection_info, dict):
            logger.error("detection_info不是字典类型")
            return False
        
        logger.info(f"  算法: {detection_info.get('algorithm', 'N/A')}")
        logger.info(f"  处理时间: {detection_info.get('processing_time', 'N/A')}s")
        logger.info(f"  帧数: {detection_info.get('frame_count', 'N/A')}")
        logger.info(f"  边界数: {detection_info.get('boundaries_count', 'N/A')}")
        
        # 验证置信度统计
        if "confidence_stats" in detection_info:
            stats = detection_info["confidence_stats"]
            logger.info(f"  置信度范围: {stats.get('min', 'N/A')} - {stats.get('max', 'N/A')}")
            logger.info(f"  平均置信度: {stats.get('mean', 'N/A')}")
        
        # 验证boundaries
        boundaries = data["boundaries"]
        if not isinstance(boundaries, list):
            logger.error("boundaries不是列表类型")
            return False
        
        logger.info(f"  边界列表长度: {len(boundaries)}")
        
        # 检查边界数据结构
        if boundaries:
            boundary_keys = ["frame_number", "timestamp", "confidence", "boundary_type"]
            first_boundary = boundaries[0]
            
            for key in boundary_keys:
                if key not in first_boundary:
                    logger.error(f"边界数据缺失键: {key}")
                    return False
            
            # 验证数据类型
            if not isinstance(first_boundary["frame_number"], int):
                logger.error("frame_number不是整数类型")
                return False
            
            if not isinstance(first_boundary["timestamp"], (int, float)):
                logger.error("timestamp不是数值类型")
                return False
            
            if not isinstance(first_boundary["confidence"], (int, float)):
                logger.error("confidence不是数值类型")
                return False
        
        # 验证segments
        segments = data["segments"]
        if not isinstance(segments, list):
            logger.error("segments不是列表类型")
            return False
        
        logger.info(f"  分段列表长度: {len(segments)}")
        
        # 检查分段数据结构
        if segments:
            segment_keys = ["index", "start_time", "end_time", "duration", "start_frame", "end_frame", "file_path"]
            first_segment = segments[0]
            
            for key in segment_keys:
                if key not in first_segment:
                    logger.error(f"分段数据缺失键: {key}")
                    return False
        
        # 验证summary
        summary = data["summary"]
        if not isinstance(summary, dict):
            logger.error("summary不是字典类型")
            return False
        
        logger.info(f"  总分段数: {summary.get('total_segments', 'N/A')}")
        logger.info(f"  总时长: {summary.get('total_duration', 'N/A')}s")
        logger.info(f"  平均分段时长: {summary.get('average_segment_duration', 'N/A')}s")
        
        logger.info("✅ 检测结果JSON文件验证通过")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return False
    except Exception as e:
        logger.error(f"验证过程中出错: {e}")
        return False


def validate_quality_metrics_json(file_path: str) -> bool:
    """验证质量指标JSON文件"""
    logger.info(f"验证质量指标文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查顶级结构
        required_keys = ["detection_metrics", "segment_metrics", "quality_thresholds", "quality_assessment"]
        missing_keys = []
        
        for key in required_keys:
            if key not in data:
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"缺失必需的键: {missing_keys}")
            return False
        
        # 验证detection_metrics
        detection_metrics = data["detection_metrics"]
        logger.info(f"  检测算法: {detection_metrics.get('algorithm', 'N/A')}")
        logger.info(f"  处理时间: {detection_metrics.get('processing_time', 'N/A')}s")
        logger.info(f"  检测边界数: {detection_metrics.get('boundaries_detected', 'N/A')}")
        logger.info(f"  处理速度比: {detection_metrics.get('processing_speed_ratio', 'N/A')}")
        
        # 验证segment_metrics
        segment_metrics = data["segment_metrics"]
        logger.info(f"  总分段数: {segment_metrics.get('total_segments', 'N/A')}")
        logger.info(f"  总时长: {segment_metrics.get('total_duration', 'N/A')}s")
        logger.info(f"  平均分段时长: {segment_metrics.get('avg_segment_duration', 'N/A')}s")
        
        # 验证quality_assessment
        quality_assessment = data["quality_assessment"]
        logger.info(f"  满足时长要求: {quality_assessment.get('meets_duration_requirements', 'N/A')}")
        logger.info(f"  满足速度要求: {quality_assessment.get('meets_speed_requirements', 'N/A')}")
        
        logger.info("✅ 质量指标JSON文件验证通过")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
        return False
    except Exception as e:
        logger.error(f"验证过程中出错: {e}")
        return False


def validate_directory(directory: str) -> bool:
    """验证目录中的所有JSON文件"""
    logger.info(f"验证目录: {directory}")
    
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.error(f"目录不存在: {directory}")
        return False
    
    json_files = list(dir_path.glob("*.json"))
    if not json_files:
        logger.warning(f"目录中没有JSON文件: {directory}")
        return True
    
    logger.info(f"找到 {len(json_files)} 个JSON文件")
    
    all_valid = True
    
    for json_file in json_files:
        logger.info(f"\n验证文件: {json_file.name}")
        
        # 根据文件名选择验证方法
        if "detection_results" in json_file.name:
            valid = validate_detection_results_json(str(json_file))
        elif "quality_metrics" in json_file.name:
            valid = validate_quality_metrics_json(str(json_file))
        else:
            # 通用JSON验证
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                logger.info("✅ JSON格式有效")
                valid = True
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON格式无效: {e}")
                valid = False
        
        if not valid:
            all_valid = False
    
    return all_valid


def compare_json_files(file1: str, file2: str) -> bool:
    """比较两个JSON文件的结构"""
    logger.info(f"比较JSON文件: {file1} vs {file2}")
    
    try:
        with open(file1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        
        with open(file2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        # 比较顶级键
        keys1 = set(data1.keys())
        keys2 = set(data2.keys())
        
        common_keys = keys1 & keys2
        only_in_1 = keys1 - keys2
        only_in_2 = keys2 - keys1
        
        logger.info(f"  共同键: {len(common_keys)}")
        logger.info(f"  仅在文件1中: {len(only_in_1)}")
        logger.info(f"  仅在文件2中: {len(only_in_2)}")
        
        if only_in_1:
            logger.info(f"  文件1独有: {list(only_in_1)}")
        
        if only_in_2:
            logger.info(f"  文件2独有: {list(only_in_2)}")
        
        # 比较数据类型
        type_differences = []
        for key in common_keys:
            if type(data1[key]) != type(data2[key]):
                type_differences.append(f"{key}: {type(data1[key])} vs {type(data2[key])}")
        
        if type_differences:
            logger.warning(f"  类型差异: {type_differences}")
        
        logger.info("✅ JSON文件比较完成")
        return len(only_in_1) == 0 and len(only_in_2) == 0 and len(type_differences) == 0
        
    except Exception as e:
        logger.error(f"比较过程中出错: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="JSON文件验证工具")
    parser.add_argument("path", help="要验证的JSON文件或目录路径")
    parser.add_argument("--compare", help="比较的第二个JSON文件路径")
    parser.add_argument("--type", choices=["detection", "quality", "auto"], 
                       default="auto", help="JSON文件类型")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    logger.info("🔍 JSON文件验证工具")
    logger.info("=" * 40)
    
    success = True
    
    if args.compare:
        # 比较模式
        success = compare_json_files(args.path, args.compare)
    elif os.path.isdir(args.path):
        # 目录验证模式
        success = validate_directory(args.path)
    elif os.path.isfile(args.path):
        # 单文件验证模式
        if args.type == "detection" or "detection" in args.path:
            success = validate_detection_results_json(args.path)
        elif args.type == "quality" or "quality" in args.path:
            success = validate_quality_metrics_json(args.path)
        else:
            # 自动检测
            try:
                with open(args.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "detection_info" in data:
                    success = validate_detection_results_json(args.path)
                elif "detection_metrics" in data:
                    success = validate_quality_metrics_json(args.path)
                else:
                    logger.info("✅ JSON格式有效（通用验证）")
                    success = True
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON格式无效: {e}")
                success = False
    else:
        logger.error(f"路径不存在: {args.path}")
        success = False
    
    if success:
        logger.info("🎉 验证完成，所有检查通过！")
        sys.exit(0)
    else:
        logger.error("❌ 验证失败，发现问题")
        sys.exit(1)


if __name__ == "__main__":
    main()

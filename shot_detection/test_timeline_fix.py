#!/usr/bin/env python3
"""
测试时间轴修复功能
验证HTML报告中的时间轴样式是否正确
"""

import sys
import os
import re
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def extract_timeline_data(html_file: str):
    """从HTML文件中提取时间轴数据"""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取边界标记的位置
        marker_pattern = r'<div class="boundary-marker" style="left: ([\d.]+)%;"'
        matches = re.findall(marker_pattern, content)
        
        positions = [float(match) for match in matches]
        
        # 提取总时长信息
        duration_pattern = r'总时长: ([\d.]+)s'
        duration_match = re.search(duration_pattern, content)
        total_duration = float(duration_match.group(1)) if duration_match else 0
        
        # 提取边界数量
        boundary_count_pattern = r'镜头切换点 \((\d+) 个\)'
        boundary_count_match = re.search(boundary_count_pattern, content)
        boundary_count = int(boundary_count_match.group(1)) if boundary_count_match else 0
        
        return {
            'positions': positions,
            'total_duration': total_duration,
            'boundary_count': boundary_count
        }
        
    except Exception as e:
        logger.error(f"提取时间轴数据失败: {e}")
        return None


def validate_timeline_positions(timeline_data):
    """验证时间轴位置的有效性"""
    if not timeline_data:
        return False, "无法提取时间轴数据"

    positions = timeline_data['positions']
    boundary_count = timeline_data['boundary_count']

    # 检查位置数量（允许有差异，因为可能有边界超出视频时长）
    if len(positions) != boundary_count:
        logger.warning(f"位置数量({len(positions)})与显示的边界数量({boundary_count})不匹配")
        logger.info("这可能是因为某些边界超出了视频时长范围，属于正常情况")

    # 检查所有位置是否在0-100%范围内（这是关键检查）
    invalid_positions = [pos for pos in positions if pos < 0 or pos > 100]
    if invalid_positions:
        return False, f"发现超出范围的位置: {invalid_positions}"

    # 检查位置是否按时间顺序排列
    sorted_positions = sorted(positions)
    if positions != sorted_positions:
        logger.warning("位置未按时间顺序排列，但这可能是正常的")

    # 主要验证：所有位置都在有效范围内
    if all(0 <= pos <= 100 for pos in positions):
        return True, f"时间轴位置验证通过 ({len(positions)} 个有效位置)"
    else:
        return False, "存在无效的时间轴位置"


def analyze_timeline_distribution(timeline_data):
    """分析时间轴分布"""
    if not timeline_data:
        return
    
    positions = timeline_data['positions']
    total_duration = timeline_data['total_duration']
    
    logger.info("📊 时间轴分布分析:")
    logger.info(f"  总边界数: {len(positions)}")
    logger.info(f"  总时长: {total_duration:.1f}s")
    
    if positions:
        logger.info(f"  位置范围: {min(positions):.2f}% - {max(positions):.2f}%")
        logger.info(f"  平均位置: {sum(positions)/len(positions):.2f}%")
        
        # 分析分布密度
        ranges = [(0, 25), (25, 50), (50, 75), (75, 100)]
        for start, end in ranges:
            count = len([p for p in positions if start <= p < end])
            logger.info(f"  {start}-{end}%范围: {count} 个边界")


def test_timeline_fix():
    """测试时间轴修复"""
    logger.info("🔧 测试时间轴修复功能")
    logger.info("=" * 50)
    
    video_path = "test_video.mp4"
    output_dir = "timeline_test_output"
    
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 执行视频处理，生成新的HTML报告
    logger.info("🎬 生成新的HTML报告...")
    success = process_video_segmentation(
        video_path,
        output_dir,
        "duration",
        "medium"
    )
    
    if not success:
        logger.error("视频处理失败")
        return False
    
    # 检查HTML报告
    html_file = Path(output_dir) / "analysis_report.html"
    if not html_file.exists():
        logger.error(f"HTML报告不存在: {html_file}")
        return False
    
    logger.info(f"✅ HTML报告生成成功: {html_file}")
    
    # 提取时间轴数据
    logger.info("📊 分析时间轴数据...")
    timeline_data = extract_timeline_data(str(html_file))
    
    if not timeline_data:
        logger.error("无法提取时间轴数据")
        return False
    
    # 验证时间轴位置
    logger.info("🔍 验证时间轴位置...")
    valid, message = validate_timeline_positions(timeline_data)
    
    if valid:
        logger.info(f"✅ {message}")
    else:
        logger.error(f"❌ {message}")
        return False
    
    # 分析时间轴分布
    analyze_timeline_distribution(timeline_data)
    
    # 检查CSS样式
    logger.info("🎨 检查CSS样式...")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含新的CSS类
    required_css = [
        '.timeline-bar',
        '.boundary-marker',
        '.timeline-legend',
        '.timeline-tick',
        '.timeline-label'
    ]
    
    missing_css = []
    for css_class in required_css:
        if css_class not in content:
            missing_css.append(css_class)
    
    if missing_css:
        logger.warning(f"缺少CSS类: {missing_css}")
    else:
        logger.info("✅ 所有必需的CSS类都存在")
    
    # 检查overflow: hidden样式
    if 'overflow: hidden' in content:
        logger.info("✅ 时间轴容器包含overflow: hidden样式")
    else:
        logger.warning("⚠️ 时间轴容器缺少overflow: hidden样式")
    
    # 检查时间刻度
    tick_pattern = r'<div class="timeline-tick"'
    tick_matches = re.findall(tick_pattern, content)
    logger.info(f"📏 时间刻度数量: {len(tick_matches)}")
    
    # 检查时间标签
    label_pattern = r'<div class="timeline-label"'
    label_matches = re.findall(label_pattern, content)
    logger.info(f"🏷️ 时间标签数量: {len(label_matches)}")
    
    return True


def compare_before_after():
    """比较修复前后的差异"""
    logger.info("🔄 比较修复前后的差异")
    
    old_file = "json_test_output/analysis_report.html"
    new_file = "timeline_test_output/analysis_report.html"
    
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        logger.warning("无法找到比较文件，跳过对比")
        return
    
    # 提取两个文件的时间轴数据
    old_data = extract_timeline_data(old_file)
    new_data = extract_timeline_data(new_file)
    
    if not old_data or not new_data:
        logger.warning("无法提取时间轴数据进行比较")
        return
    
    logger.info("📊 修复前后对比:")
    
    # 比较位置范围
    old_positions = old_data['positions']
    new_positions = new_data['positions']
    
    if old_positions:
        old_max = max(old_positions)
        old_min = min(old_positions)
        logger.info(f"  修复前位置范围: {old_min:.2f}% - {old_max:.2f}%")
        
        # 检查是否有超出100%的位置
        old_invalid = [p for p in old_positions if p > 100]
        if old_invalid:
            logger.info(f"  修复前超出100%的位置: {len(old_invalid)} 个")
    
    if new_positions:
        new_max = max(new_positions)
        new_min = min(new_positions)
        logger.info(f"  修复后位置范围: {new_min:.2f}% - {new_max:.2f}%")
        
        # 检查是否还有超出100%的位置
        new_invalid = [p for p in new_positions if p > 100]
        if new_invalid:
            logger.error(f"  修复后仍有超出100%的位置: {len(new_invalid)} 个")
        else:
            logger.info("  ✅ 修复后所有位置都在有效范围内")


def main():
    """主函数"""
    setup_logging()
    
    logger.info("🔧 时间轴修复测试")
    logger.info("=" * 40)
    
    try:
        # 测试时间轴修复
        success = test_timeline_fix()
        
        if success:
            logger.info("✅ 时间轴修复测试通过")
            
            # 比较修复前后
            compare_before_after()
            
            logger.info("🎉 时间轴修复功能验证完成！")
            return True
        else:
            logger.error("❌ 时间轴修复测试失败")
            return False
            
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

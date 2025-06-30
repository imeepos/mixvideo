#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - 提示词使用示例
展示如何在项目中使用Python格式的提示词
"""

import json
from typing import Dict, List, Any
from pathlib import Path

# 导入提示词模块
from prompts_constants import (
    get_video_analysis_prompt,
    get_folder_matching_prompt,
    PromptType,
    get_prompt_metadata,
    list_available_prompts
)

from prompts_manager import PromptsManager


class VideoAnalysisService:
    """视频分析服务示例"""
    
    def __init__(self):
        self.prompts_manager = PromptsManager()
    
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            分析结果字典
        """
        # 获取视频分析提示词
        analysis_prompt = get_video_analysis_prompt()
        
        print(f"🎬 开始分析视频: {Path(video_path).name}")
        print(f"📝 使用提示词长度: {len(analysis_prompt)} 字符")
        
        # 这里应该调用AI模型进行分析
        # 示例返回模拟的分析结果
        mock_result = {
            "video_path": video_path,
            "analysis": {
                "scenes": [
                    {
                        "start_time": "00:00:00",
                        "end_time": "00:00:15",
                        "description": "产品展示场景，白色背景下的红色连衣裙细节展示"
                    },
                    {
                        "start_time": "00:00:15", 
                        "end_time": "00:00:30",
                        "description": "模特试穿场景，展示连衣裙的穿着效果"
                    }
                ],
                "objects": ["连衣裙", "模特", "白色背景"],
                "summary": "这是一个女装产品展示视频，主要展示红色连衣裙的产品细节和穿着效果",
                "emotion": "优雅、时尚、专业",
                "keywords": ["女装", "连衣裙", "红色", "产品展示", "模特试穿"],
                "product_analysis": {
                    "appearance": {
                        "color": "红色",
                        "style": "连衣裙",
                        "material": "丝质面料"
                    },
                    "target_audience": "25-35岁职业女性",
                    "brand_elements": "简约logo"
                },
                "technical_analysis": {
                    "shooting_style": "专业产品摄影",
                    "composition": "居中构图，多角度展示"
                }
            },
            "confidence": 0.92
        }
        
        return mock_result


class FolderMatchingService:
    """文件夹匹配服务示例"""
    
    def __init__(self):
        self.prompts_manager = PromptsManager()
    
    def recommend_folders(self, content_description: str, available_folders: List[str]) -> Dict[str, Any]:
        """
        推荐合适的文件夹
        
        Args:
            content_description: 视频内容描述
            available_folders: 可选文件夹列表
            
        Returns:
            文件夹推荐结果
        """
        # 获取格式化的文件夹匹配提示词
        matching_prompt = get_folder_matching_prompt(content_description, available_folders)
        
        print(f"📁 开始文件夹匹配分析")
        print(f"📝 内容描述: {content_description}")
        print(f"📂 可选文件夹: {', '.join(available_folders)}")
        print(f"📝 使用提示词长度: {len(matching_prompt)} 字符")
        
        # 这里应该调用AI模型进行分析
        # 示例返回模拟的匹配结果
        mock_result = {
            "content_description": content_description,
            "available_folders": available_folders,
            "matches": [
                {
                    "folderName": "产品展示",
                    "score": 0.85,
                    "reasons": [
                        "视频包含产品细节展示场景",
                        "符合白底背景的展示标准",
                        "多角度特写符合产品展示要求"
                    ]
                },
                {
                    "folderName": "模特试穿", 
                    "score": 0.75,
                    "reasons": [
                        "包含模特试穿展示",
                        "展示了穿着效果",
                        "符合试穿类视频特征"
                    ]
                },
                {
                    "folderName": "使用场景",
                    "score": 0.25,
                    "reasons": [
                        "缺少明显的使用场景展示"
                    ]
                },
                {
                    "folderName": "AI素材",
                    "score": 0.1,
                    "reasons": [
                        "无AI生成痕迹"
                    ]
                }
            ],
            "recommended_folder": "产品展示",
            "confidence": 0.85
        }
        
        return mock_result


class PromptManagementDemo:
    """提示词管理演示"""
    
    def __init__(self):
        self.prompts_manager = PromptsManager()
    
    def demo_prompt_management(self):
        """演示提示词管理功能"""
        print("=== 提示词管理演示 ===")
        
        # 1. 列出所有可用提示词
        print("\n1. 📋 可用提示词列表:")
        available_prompts = list_available_prompts()
        for prompt_type, description in available_prompts.items():
            print(f"   • {prompt_type}: {description}")
        
        # 2. 获取提示词元数据
        print("\n2. 📊 提示词元数据:")
        for prompt_type in [PromptType.VIDEO_ANALYSIS, PromptType.FOLDER_MATCHING]:
            metadata = get_prompt_metadata(prompt_type)
            print(f"   • {prompt_type}:")
            print(f"     - 名称: {metadata.get('name', 'N/A')}")
            print(f"     - 变量: {metadata.get('variables', [])}")
            print(f"     - 输出格式: {metadata.get('output_format', 'N/A')}")
            print(f"     - 用途: {metadata.get('use_case', 'N/A')}")
        
        # 3. 演示提示词使用
        print("\n3. 🎯 提示词使用演示:")
        
        # 视频分析提示词
        video_prompt = get_video_analysis_prompt()
        print(f"   • 视频分析提示词: {len(video_prompt)} 字符")
        
        # 文件夹匹配提示词
        test_description = "女装连衣裙产品展示视频，包含细节特写和模特试穿"
        test_folders = ["产品展示", "模特试穿", "使用场景", "AI素材"]
        folder_prompt = get_folder_matching_prompt(test_description, test_folders)
        print(f"   • 文件夹匹配提示词: {len(folder_prompt)} 字符")
        
        # 4. 演示高级管理功能
        print("\n4. 🔧 高级管理功能:")
        
        # 获取特定提示词配置
        video_config = self.prompts_manager.get_prompt('video_analysis')
        if video_config:
            print(f"   • 视频分析配置: {video_config.name}")
            print(f"     - 描述: {video_config.description}")
            print(f"     - 变量数量: {len(video_config.variables or [])}")
        
        folder_config = self.prompts_manager.get_prompt('folder_matching')
        if folder_config:
            print(f"   • 文件夹匹配配置: {folder_config.name}")
            print(f"     - 描述: {folder_config.description}")
            print(f"     - 变量: {folder_config.variables}")


def main():
    """主函数 - 运行所有示例"""
    print("🎬 智能镜头检测与分段系统 - 提示词使用示例")
    print("=" * 60)
    
    # 1. 提示词管理演示
    demo = PromptManagementDemo()
    demo.demo_prompt_management()
    
    print("\n" + "=" * 60)
    
    # 2. 视频分析服务演示
    print("\n🎥 视频分析服务演示:")
    video_service = VideoAnalysisService()
    analysis_result = video_service.analyze_video("test_video.mp4")
    
    print(f"\n📊 分析结果:")
    print(f"   • 场景数量: {len(analysis_result['analysis']['scenes'])}")
    print(f"   • 识别对象: {', '.join(analysis_result['analysis']['objects'])}")
    print(f"   • 内容总结: {analysis_result['analysis']['summary']}")
    print(f"   • 置信度: {analysis_result['confidence']}")
    
    print("\n" + "=" * 60)
    
    # 3. 文件夹匹配服务演示
    print("\n📁 文件夹匹配服务演示:")
    folder_service = FolderMatchingService()
    
    test_description = "这是一个女装连衣裙产品展示视频，包含白底背景下的产品细节展示和模特试穿效果"
    test_folders = ["产品展示", "模特试穿", "使用场景", "AI素材"]
    
    matching_result = folder_service.recommend_folders(test_description, test_folders)
    
    print(f"\n📊 匹配结果:")
    print(f"   • 推荐文件夹: {matching_result['recommended_folder']}")
    print(f"   • 置信度: {matching_result['confidence']}")
    print(f"   • 详细匹配:")
    
    for match in matching_result['matches']:
        if match['score'] > 0.5:  # 只显示高分匹配
            print(f"     - {match['folderName']}: {match['score']:.2f}")
            for reason in match['reasons'][:2]:  # 只显示前两个原因
                print(f"       * {reason}")
    
    print("\n✅ 所有示例演示完成！")


if __name__ == "__main__":
    main()

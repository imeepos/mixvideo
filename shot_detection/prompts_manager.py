#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - 提示词管理模块
将提示词文件转化为Python格式，提供统一的提示词管理接口
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class PromptConfig:
    """提示词配置类"""
    name: str
    description: str
    content: str
    variables: list = None


class PromptsManager:
    """提示词管理器"""
    
    def __init__(self, prompts_dir: str = None):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词目录路径，默认为当前目录下的prompts文件夹
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self._prompts_cache = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """从本地文件加载所有提示词"""
        # 视频分析提示词
        video_content = self._load_prompt_from_file('video-analysis.prompt')
        if video_content:
            self._prompts_cache['video_analysis'] = PromptConfig(
                name="video_analysis",
                description="女装视频资源管理专家 - 视频分析提示词",
                content=video_content,
                variables=[]
            )

        # 文件夹匹配提示词
        folder_content = self._load_prompt_from_file('folder-matching.prompt')
        if folder_content:
            self._prompts_cache['folder_matching'] = PromptConfig(
                name="folder_matching",
                description="女装视频资源管理专家 - 文件夹匹配提示词",
                content=folder_content,
                variables=['contentDescription', 'folderList']
            )

    def _load_prompt_from_file(self, filename: str) -> Optional[str]:
        """
        从文件加载提示词内容

        Args:
            filename: 提示词文件名

        Returns:
            提示词内容，如果文件不存在则返回None
        """
        try:
            file_path = self.prompts_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    return content
            else:
                print(f"警告: 提示词文件不存在: {file_path}")
                return None
        except Exception as e:
            print(f"错误: 加载提示词文件失败 {filename}: {e}")
            return None




    def get_prompt(self, prompt_name: str) -> Optional[PromptConfig]:
        """
        获取指定的提示词配置
        
        Args:
            prompt_name: 提示词名称 ('video_analysis' 或 'folder_matching')
            
        Returns:
            PromptConfig对象，如果不存在则返回None
        """
        return self._prompts_cache.get(prompt_name)
    
    def get_video_analysis_prompt(self) -> str:
        """获取视频分析提示词内容"""
        prompt_config = self.get_prompt('video_analysis')
        return prompt_config.content if prompt_config else ""
    
    def get_folder_matching_prompt(self, content_description: str = None, folder_list: list = None) -> str:
        """
        获取文件夹匹配提示词

        Args:
            content_description: 视频内容描述（可选）
            folder_list: 可选文件夹列表（可选）

        Returns:
            格式化后的提示词或原始提示词
        """
        prompt_config = self.get_prompt('folder_matching')
        if not prompt_config:
            return ""

        # 如果没有提供参数，返回原始提示词
        if content_description is None:
            return prompt_config.content

        # 如果没有提供文件夹列表，使用默认列表
        if folder_list is None:
            folder_list = ["产品展示", "模特试穿", "使用场景", "AI素材"]

        # 格式化文件夹列表
        formatted_folders = '\n'.join([f"{i+1}. {folder}" for i, folder in enumerate(folder_list)])

        # 替换变量
        try:
            formatted_prompt = prompt_config.content.format(
                contentDescription=content_description,
                folderList=formatted_folders
            )
            return formatted_prompt
        except KeyError:
            # 如果格式化失败，返回原始内容
            return prompt_config.content
    
    def list_prompts(self) -> Dict[str, str]:
        """列出所有可用的提示词"""
        return {name: config.description for name, config in self._prompts_cache.items()}
    
    def reload_prompts(self):
        """重新加载提示词（用于开发时更新）"""
        self._prompts_cache.clear()
        self._load_prompts()


# 创建默认的提示词管理器实例
default_prompts_manager = PromptsManager()

# 便捷函数
def get_video_analysis_prompt() -> str:
    """获取视频分析提示词"""
    return default_prompts_manager.get_video_analysis_prompt()

def get_folder_matching_prompt(content_description: str, folder_list: list) -> str:
    """获取文件夹匹配提示词"""
    return default_prompts_manager.get_folder_matching_prompt(content_description, folder_list)

def list_available_prompts() -> Dict[str, str]:
    """列出所有可用的提示词"""
    return default_prompts_manager.list_prompts()


if __name__ == "__main__":
    # 测试代码
    print("=== 提示词管理器测试 ===")
    
    # 列出所有提示词
    print("\n可用提示词：")
    for name, desc in list_available_prompts().items():
        print(f"- {name}: {desc}")
    
    # 测试视频分析提示词
    print("\n=== 视频分析提示词 ===")
    video_prompt = get_video_analysis_prompt()
    print(f"长度: {len(video_prompt)} 字符")
    print(f"前100字符: {video_prompt[:100]}...")
    
    # 测试文件夹匹配提示词
    print("\n=== 文件夹匹配提示词 ===")
    test_description = "这是一个女装产品展示视频，展示了一件红色连衣裙的细节"
    test_folders = ["产品展示", "模特试穿", "使用场景", "AI素材"]
    
    folder_prompt = get_folder_matching_prompt(test_description, test_folders)
    print(f"长度: {len(folder_prompt)} 字符")
    print(f"包含变量替换: {'contentDescription' not in folder_prompt}")

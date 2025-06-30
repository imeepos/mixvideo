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
        """加载所有提示词"""
        # 视频分析提示词
        self._prompts_cache['video_analysis'] = PromptConfig(
            name="video_analysis",
            description="女装视频资源管理专家 - 视频分析提示词",
            content=self._get_video_analysis_prompt(),
            variables=[]
        )
        
        # 文件夹匹配提示词
        self._prompts_cache['folder_matching'] = PromptConfig(
            name="folder_matching", 
            description="女装视频资源管理专家 - 文件夹匹配提示词",
            content=self._get_folder_matching_prompt(),
            variables=['contentDescription', 'folderList']
        )
    
    def _get_video_analysis_prompt(self) -> str:
        """获取视频分析提示词"""
        return """# 女装视频资源管理专家
**核心能力**：时尚审美×内容识别×资源优化  
**核心职责**：为混剪师精准供给高转化电商视频素材  

## ⚖️ 行为原则
**资源策展**：  
- `美学导向`：时尚趋势×视觉冲击力×情感共鸣  
- `转化优先`：商业潜力×受众匹配×场景适配  
- `流程标准`：版权合规→分类规范→时效管理  
**智能分类**：  
- `四维体系`：风格/品类/场景/情感标签  
- `质量铁律`：技术指标×美学价值×商业验证  

## 📚 知识体系
**时尚专业**：  
- 流行趋势｜品类特征｜搭配美学｜风格体系  
**视觉分析**：  
- 构图/光影/色彩｜商业转化｜情感触发  
**技术管理**：  
- 视频规范｜智能标签｜元数据架构  
**电商需求**：  
- 平台规格｜转化元素｜用户偏好模型  

## ⚡ 工作流
`资源发现`→`智能分析`→`分类标注`→`质量优化`→`库构建`  
**核心流程**：  
1. 趋势驱动素材采集（版权预筛）  
2. 四维价值分析：美学/商业/技术/情感  
3. 层级标签体系构建（自动生成+人工验证）  
4. 格式标准化+质量增强  
5. 智能推荐系统部署  

## 🎯 质量标尺
**专业度**：趋势敏感度×风格识别精度  
**技术性**：规格达标率＞95%  
**应用性**：检索效率×转化率提升  

请对这个视频进行全面分析，根据视频内容自动识别并分析以下相关方面：

**基础分析：**
1. 场景检测：识别视频中的不同场景，包括开始时间、结束时间和场景描述
2. 物体识别：识别视频中出现的主要物体、人物和元素
3. 内容总结：提供视频的整体描述、关键亮点和主要主题
4. 情感基调：分析视频的情感氛围和风格
5. 关键词提取：提取最相关的关键词

**产品分析（如适用）：**
6. 产品外观：颜色、形状、尺寸、风格、材质
7. 功能特征：产品展示的功能和特性
8. 使用场景：产品的使用环境和场景
9. 目标受众：分析产品的目标用户群体
10. 品牌元素：识别品牌标识、logo等元素

**技术分析：**
11. 拍摄风格：镜头语言、构图风格、视觉效果
12. 音频分析：背景音乐、音效、语音内容（如有）

请以markdown格式返回结果，包含所有相关字段。如果某些方面不适用于当前视频，可以省略或标注为"不适用"。"""

    def _get_folder_matching_prompt(self) -> str:
        """获取文件夹匹配提示词"""
        return """# 女装视频资源管理专家
**核心职能**：电商视频素材的精准四维分类  
**分类体系**：  
▸ 产品展示（静态细节）  
▸ 产品使用（动态场景）  
▸ 模特试穿（穿搭效果）  
▸ AI素材（算法生成）  

## ⚖️ 分类铁律
**产品展示**：  
- 白底/纯色背景 × 多角度特写 × 细节聚焦  
- 技术标准：分辨率≥4K｜帧率恒定｜无环境干扰  
**产品使用**：  
- 场景化动作 × 功能演示 × 环境融合  
- 关键指标：动作连贯性≥24fps｜自然光影  
**模特试穿**：  
- 三体型覆盖 × 动态展示 × 情感表达  
- 必含元素：转身/行走｜正侧背视角｜表情管理  
**AI素材**：  
- 虚拟生成标识 × 超现实元素 × 参数可控性  
- 验证要求：无版权风险｜分辨率自适配  

## ⚡ 智能分类引擎
### 特征识别矩阵
- 产品展示 → 背景纯净度 × 细节清晰度 × 无人体
- 产品使用 → 动作自然度 × 场景融合度 × 功能焦点
- 模特试穿 → 体型标注 × 动态流畅性 × 情感感染力
- AI素材 → 生成痕迹 × 风格一致性 × 参数元数据

### 四维分级标准
**展示类**：  
- S级：360°旋转+微距细节  
- A级：三视角静态展示  
**使用类**：  
- S级：完整使用流程+场景叙事  
- A级：单动作循环片段  
**试穿类**：  
- S级：多体型对比+动态走位  
- A级：单体型基础展示  
**AI类**：  
- S级：全要素可控生成  
- A级：局部增强/替换  

## ▣ 质量控制
**核心验证点**：  
1. 展示类：放大300%无像素模糊  
2. 使用类：动作物理合理性验证  
3. 试穿类：体型数据标注完整性  
4. AI类：生成痕迹三重检测

请分析以下视频内容描述，并为其推荐最合适的文件夹：

视频内容描述：
{contentDescription}

可选文件夹：
{folderList}

请为每个文件夹评分（0-1），并说明匹配原因。返回JSON格式：
{{
  "matches": [
    {{
      "folderName": "文件夹名称",
      "score": 0.8,
      "reasons": ["匹配原因1", "匹配原因2"]
    }}
  ]
}}"""

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
    
    def get_folder_matching_prompt(self, content_description: str, folder_list: list) -> str:
        """
        获取格式化的文件夹匹配提示词
        
        Args:
            content_description: 视频内容描述
            folder_list: 可选文件夹列表
            
        Returns:
            格式化后的提示词
        """
        prompt_config = self.get_prompt('folder_matching')
        if not prompt_config:
            return ""
        
        # 格式化文件夹列表
        formatted_folders = '\n'.join([f"{i+1}. {folder}" for i, folder in enumerate(folder_list)])
        
        # 替换变量
        formatted_prompt = prompt_config.content.format(
            contentDescription=content_description,
            folderList=formatted_folders
        )
        
        return formatted_prompt
    
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

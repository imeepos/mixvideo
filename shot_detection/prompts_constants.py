#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - 提示词常量
将提示词文件转化为Python常量，便于直接使用
"""

# 视频分析提示词
VIDEO_ANALYSIS_PROMPT = """# 女装视频资源管理专家
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

请以JSON格式返回结果，包含所有相关字段。如果某些方面不适用于当前视频，可以省略或标注为"不适用"。"""

# 文件夹匹配提示词模板
FOLDER_MATCHING_PROMPT_TEMPLATE = """# 女装视频资源管理专家
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
{content_description}

可选文件夹：
{folder_list}

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

# 提示词类型枚举
class PromptType:
    """提示词类型常量"""
    VIDEO_ANALYSIS = "video_analysis"
    FOLDER_MATCHING = "folder_matching"

# 提示词元数据
PROMPT_METADATA = {
    PromptType.VIDEO_ANALYSIS: {
        "name": "视频分析提示词",
        "description": "女装视频资源管理专家 - 用于分析视频内容的专业提示词",
        "variables": [],
        "output_format": "JSON",
        "use_case": "视频内容分析、特征提取、质量评估"
    },
    PromptType.FOLDER_MATCHING: {
        "name": "文件夹匹配提示词",
        "description": "女装视频资源管理专家 - 用于智能文件夹分类的提示词",
        "variables": ["content_description", "folder_list"],
        "output_format": "JSON",
        "use_case": "视频文件自动分类、文件夹推荐"
    }
}

def get_video_analysis_prompt() -> str:
    """
    获取视频分析提示词
    
    Returns:
        str: 视频分析提示词
    """
    return VIDEO_ANALYSIS_PROMPT

def get_folder_matching_prompt(content_description: str, folder_list: list) -> str:
    """
    获取格式化的文件夹匹配提示词
    
    Args:
        content_description (str): 视频内容描述
        folder_list (list): 可选文件夹列表
        
    Returns:
        str: 格式化后的文件夹匹配提示词
    """
    # 格式化文件夹列表
    formatted_folders = '\n'.join([f"{i+1}. {folder}" for i, folder in enumerate(folder_list)])
    
    # 替换变量
    return FOLDER_MATCHING_PROMPT_TEMPLATE.format(
        content_description=content_description,
        folder_list=formatted_folders
    )

def get_prompt_metadata(prompt_type: str) -> dict:
    """
    获取提示词元数据
    
    Args:
        prompt_type (str): 提示词类型
        
    Returns:
        dict: 提示词元数据
    """
    return PROMPT_METADATA.get(prompt_type, {})

def list_available_prompts() -> dict:
    """
    列出所有可用的提示词
    
    Returns:
        dict: 提示词类型和描述的映射
    """
    return {
        prompt_type: metadata["description"] 
        for prompt_type, metadata in PROMPT_METADATA.items()
    }

# 向后兼容的别名
ANALYSIS_PROMPT = VIDEO_ANALYSIS_PROMPT
CLASSIFICATION_PROMPT_TEMPLATE = FOLDER_MATCHING_PROMPT_TEMPLATE

if __name__ == "__main__":
    # 测试代码
    print("=== 提示词常量测试 ===")
    
    # 测试视频分析提示词
    print(f"\n视频分析提示词长度: {len(get_video_analysis_prompt())} 字符")
    
    # 测试文件夹匹配提示词
    test_description = "这是一个女装产品展示视频，展示了一件红色连衣裙的细节"
    test_folders = ["产品展示", "模特试穿", "使用场景", "AI素材"]
    
    folder_prompt = get_folder_matching_prompt(test_description, test_folders)
    print(f"文件夹匹配提示词长度: {len(folder_prompt)} 字符")
    
    # 测试元数据
    print(f"\n可用提示词: {list_available_prompts()}")
    
    # 测试元数据获取
    video_meta = get_prompt_metadata(PromptType.VIDEO_ANALYSIS)
    print(f"\n视频分析提示词元数据: {video_meta}")
    
    print("\n✅ 所有测试通过！")

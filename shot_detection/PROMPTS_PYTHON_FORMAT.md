# 提示词Python格式转换说明

## 🎯 **概述**

已成功将 `shot_detection/prompts/` 目录中的提示词文件转换为Python格式，提供了更灵活和易于集成的提示词管理方案。

## 📁 **文件结构**

```
shot_detection/
├── prompts/                          # 原始提示词文件
│   ├── video-analysis.prompt         # 视频分析提示词
│   └── folder-matching.prompt        # 文件夹匹配提示词
├── prompts_constants.py              # 提示词常量模块 ⭐
├── prompts_manager.py                # 提示词管理器模块 ⭐
├── prompts_usage_example.py          # 使用示例 ⭐
└── PROMPTS_PYTHON_FORMAT.md          # 本说明文档
```

## 🔧 **核心模块**

### 1. **prompts_constants.py** - 简单直接的常量模块

**特点：**
- 直接定义提示词为Python字符串常量
- 提供便捷的函数接口
- 轻量级，无外部依赖
- 适合简单的使用场景

**使用方法：**
```python
from prompts_constants import (
    get_video_analysis_prompt,
    get_folder_matching_prompt,
    PromptType
)

# 获取视频分析提示词
video_prompt = get_video_analysis_prompt()

# 获取文件夹匹配提示词（带变量替换）
content_desc = "女装连衣裙产品展示视频"
folders = ["产品展示", "模特试穿", "使用场景"]
folder_prompt = get_folder_matching_prompt(content_desc, folders)
```

### 2. **prompts_manager.py** - 高级管理模块 ⭐

**特点：**
- 面向对象的设计
- **从本地文件动态加载提示词** 🔥
- 支持提示词元数据管理
- 支持动态加载和重载
- 提供配置和缓存机制
- 适合复杂的应用场景

**使用方法：**
```python
from prompts_manager import PromptsManager, PromptConfig

# 创建管理器实例
manager = PromptsManager()

# 获取提示词配置
config = manager.get_prompt('video_analysis')
print(f"提示词名称: {config.name}")
print(f"描述: {config.description}")
print(f"内容: {config.content}")

# 列出所有提示词
available = manager.list_prompts()
```

## 🎯 **提示词类型**

### **1. 视频分析提示词 (video_analysis)**

**用途：** 分析视频内容，提取特征和元数据

**特点：**
- 专门针对女装电商视频优化
- 包含时尚审美和商业转化要素
- 支持多维度分析（场景、物体、情感等）
- 输出JSON格式的结构化结果

**使用场景：**
- 视频内容自动分析
- 视频质量评估
- 商业价值评估
- 智能标签生成

### **2. 文件夹匹配提示词 (folder_matching)**

**用途：** 根据视频内容推荐合适的分类文件夹

**特点：**
- 四维分类体系（产品展示/产品使用/模特试穿/AI素材）
- 智能评分机制（0-1分值）
- 详细的匹配原因说明
- 支持自定义文件夹列表

**变量：**
- `content_description`: 视频内容描述
- `folder_list`: 可选文件夹列表

**使用场景：**
- 视频文件自动分类
- 智能文件夹推荐
- 内容匹配度评估

## 🚀 **快速开始**

### **方法1：使用常量模块（推荐简单场景）**

```python
# 1. 导入模块
from shot_detection.prompts_constants import get_video_analysis_prompt

# 2. 获取提示词
prompt = get_video_analysis_prompt()

# 3. 使用提示词调用AI模型
# result = ai_model.analyze(video_data, prompt)
```

### **方法2：使用管理器模块（推荐复杂场景）**

```python
# 1. 导入模块
from shot_detection.prompts_manager import PromptsManager

# 2. 创建管理器
manager = PromptsManager()

# 3. 获取提示词
video_prompt = manager.get_video_analysis_prompt()
folder_prompt = manager.get_folder_matching_prompt(
    content_description="视频描述",
    folder_list=["文件夹1", "文件夹2"]
)

# 4. 使用提示词
# results = process_with_prompts(video_prompt, folder_prompt)
```

## 📊 **集成示例**

### **在视频分析中使用**

```python
def analyze_video_with_ai(video_path: str):
    """使用AI分析视频"""
    from prompts_constants import get_video_analysis_prompt
    
    # 获取专业的视频分析提示词
    prompt = get_video_analysis_prompt()
    
    # 调用AI模型（示例）
    # result = ai_client.analyze_video(
    #     video_path=video_path,
    #     prompt=prompt,
    #     output_format="json"
    # )
    
    return result
```

### **在文件分类中使用**

```python
def classify_video_to_folder(content_description: str, available_folders: list):
    """智能分类视频到文件夹"""
    from prompts_constants import get_folder_matching_prompt
    
    # 获取文件夹匹配提示词
    prompt = get_folder_matching_prompt(content_description, available_folders)
    
    # 调用AI模型进行分类
    # result = ai_client.classify(
    #     prompt=prompt,
    #     output_format="json"
    # )
    
    # 解析结果并返回推荐文件夹
    # return result['matches'][0]['folderName']
```

## 🔄 **文件加载 vs 常量模块**

### **方式1：文件动态加载（推荐）**
```python
# 从本地文件动态加载，支持实时更新
from prompts_manager import PromptsManager
manager = PromptsManager()
prompt = manager.get_video_analysis_prompt()
```

### **方式2：常量模块（快速访问）**
```python
# 使用预定义常量，访问速度快
from prompts_constants import get_video_analysis_prompt
prompt = get_video_analysis_prompt()
```

### **方式3：原始文件读取（传统方式）**
```python
# 直接读取文件（仍然支持）
with open('prompts/video-analysis.prompt', 'r', encoding='utf-8') as f:
    prompt = f.read()
```

### **选择建议：**
- **开发阶段**：使用文件动态加载，便于调试和修改
- **生产环境**：根据性能需求选择文件加载或常量模块
- **简单项目**：使用常量模块，代码更简洁

## ✅ **优势**

1. **灵活加载**：管理器模块支持从本地文件动态加载，常量模块提供快速访问
2. **实时更新**：修改 `.prompt` 文件后可立即生效（管理器模块）
3. **类型安全**：Python类型提示，IDE智能提示
4. **版本控制**：提示词变更可通过Git跟踪
5. **易于测试**：可以轻松进行单元测试
6. **模块化**：支持按需导入，减少内存占用
7. **扩展性**：易于添加新的提示词和功能
8. **向后兼容**：保留原始文件，支持多种使用方式

## 🧪 **测试**

运行测试以验证所有功能正常：

```bash
# 测试常量模块
python3 shot_detection/prompts_constants.py

# 测试管理器模块  
python3 shot_detection/prompts_manager.py

# 运行完整示例
python3 shot_detection/prompts_usage_example.py
```

## 📝 **注意事项**

1. **编码格式**：所有Python文件使用UTF-8编码
2. **向后兼容**：原始`.prompt`文件仍然保留，可以继续使用
3. **变量替换**：文件夹匹配提示词支持动态变量替换
4. **缓存机制**：管理器模块包含缓存，提高性能
5. **错误处理**：包含适当的错误处理和验证

## 🔮 **未来扩展**

- 支持多语言提示词
- 添加提示词版本管理
- 集成提示词性能监控
- 支持动态提示词生成
- 添加提示词A/B测试功能

现在您可以在shot_detection项目中使用这些Python格式的提示词，享受更好的开发体验和性能！🎉

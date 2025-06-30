# 🤖 Gemini智能视频归类功能指南

## ✨ 功能概览

### 🔄 **智能归类流程**
1. **视频分析** → AI分析视频内容和高光时刻
2. **内容描述构建** → 提取关键特征信息
3. **Gemini智能归类** → 使用folder-matching.prompt进行分类
4. **自动文件管理** → 复制到对应目录并重命名
5. **元数据保存** → 记录归类信息和置信度

### 🎯 **核心特性**
- ✅ **AI驱动归类** - 使用Gemini API和专业提示词
- ✅ **多维度分析** - 综合内容、质量、情感等因素
- ✅ **智能文件命名** - 包含质量等级和置信度信息
- ✅ **完整可追溯** - 保存详细的归类元数据
- ✅ **备用机制** - Gemini失败时使用本地逻辑

## 📁 智能归类体系

### **专业分类（基于folder-matching.prompt）**
```
📦 classified/
├── product_display/        # 产品展示 - 白底背景、静态特写
├── product_usage/          # 产品使用 - 场景化、功能演示
├── model_wearing/          # 模特试穿 - 人物展示、动态效果
├── ai_generated/           # AI素材 - 虚拟生成内容
├── premium_highlights/     # 优质高光 - ≥3个精彩时刻
├── good_highlights/        # 良好高光 - 1-2个精彩时刻
├── elegant_style/          # 优雅风格 - 专业、优雅气质
├── active_style/           # 活泼风格 - 动感、活力表现
└── standard/               # 标准分类 - 其他内容
```

### **归类标准**
| 分类 | 关键特征 | 置信度 | 示例场景 |
|------|----------|--------|----------|
| **产品展示** | 白底背景 + 静态展示 + 无模特 | 90% | 360°旋转展示、细节特写 |
| **模特试穿** | 模特 + 试穿/转身/走位 | 85% | T台走秀、试穿效果展示 |
| **产品使用** | 场景化 + 使用/功能/演示 | 80% | 日常穿搭、功能展示 |
| **优质高光** | ≥3个高光时刻 | 95% | 多维度精彩内容 |
| **AI素材** | AI/生成/虚拟关键词 | 85% | 算法生成内容 |

## 🔧 技术实现

### **1. 内容描述构建**
```python
def _build_content_description(analysis_data):
    # 提取关键信息
    - 内容摘要
    - 高光时刻数量和类型
    - 检测物体和动作
    - 整体情感和质量
    - 技术参数
```

### **2. Gemini API调用**
```python
def _gemini_classify_video(analysis_data):
    # 加载folder-matching提示词
    # 构建完整提示（内容描述 + JSON格式要求）
    # 调用Gemini API进行分类
    # 返回结构化结果
```

### **3. 智能文件命名**
```
格式: [质量等级]_[置信度]_[原文件名].mp4

示例:
- S级_高信度_fashion_video.mp4
- A级_中信度_product_demo.mp4
- 多高光_优质_model_show.mp4
```

## 📊 提示词集成

### **folder-matching.prompt 使用**
```python
# 加载提示词
prompts_manager = PromptsManager()
folder_prompt = prompts_manager.get_folder_matching_prompt(
    content_description,  # 视频内容描述
    folder_list          # 可选文件夹列表
)

# 添加JSON格式要求
full_prompt = folder_prompt + json_format_requirements
```

### **JSON输出格式**
```json
{
  "category": "推荐的文件夹名称",
  "confidence": 0.95,
  "reason": "归类原因说明",
  "quality_level": "S级/A级/B级",
  "features": ["关键特征1", "关键特征2"],
  "recommendations": "优化建议"
}
```

## 🎯 归类逻辑优先级

### **智能决策树**
```
1. 高光时刻数量 ≥ 3 → premium_highlights
2. 白底背景 + 静态展示 + 无模特 → product_display  
3. 模特 + (试穿|转身|走位) → model_wearing
4. 场景 + (使用|功能|演示) → product_usage
5. AI/生成/虚拟 → ai_generated
6. 高光时刻数量 1-2 → good_highlights
7. 活力/活泼 → active_style
8. 优雅/专业 → elegant_style
9. 其他 → standard
```

### **特征权重**
- **内容特征** (40%) - 物体、动作、场景
- **质量指标** (30%) - 高光数量、视频质量
- **情感色调** (20%) - 整体情感、氛围
- **技术参数** (10%) - 分辨率、镜头运动

## 📄 元数据记录

### **归类信息文件**
每个归类视频生成对应的 `.classification.json`:
```json
{
  "original_path": "/path/to/original.mp4",
  "classified_path": "/path/to/classified/S级_高信度_original.mp4",
  "classification_time": "2024-01-01 12:00:00",
  "category": "premium_highlights",
  "classification_method": "gemini_ai",
  "analysis_summary": {
    "highlights_count": 4,
    "video_quality": 9,
    "overall_mood": "活力四射",
    "summary": "包含多个精彩高光时刻的优质视频内容"
  },
  "gemini_classification": {
    "confidence": 0.95,
    "reason": "检测到优质高光特征：多个精彩时刻(≥3个)",
    "quality_level": "S级",
    "features": ["多高光", "高质量"],
    "recommendations": "适合作为重点推广素材"
  }
}
```

## 🚀 使用方式

### **GUI操作**
1. 在"🎥 视频分析"标签页选择视频
2. 点击"开始分析"
3. 系统自动完成：
   - AI视频分析
   - Gemini智能归类
   - 文件自动整理
   - 元数据保存

### **归类结果查看**
- 📊 **状态栏显示**: 归类结果和置信度
- 📁 **一键访问**: "打开归类目录"按钮
- 📋 **详细信息**: 查看完整归类元数据

## 🔍 测试验证

### **运行测试**
```bash
python test_gemini_classification.py
```

### **测试覆盖**
- ✅ 内容描述构建准确性
- ✅ Gemini归类逻辑正确性  
- ✅ 文件命名规则验证
- ✅ 元数据保存完整性
- ✅ 提示词加载和集成

## 🎉 功能优势

### **🎯 精准分类**
- 基于专业提示词的AI分析
- 多维度特征综合评估
- 智能优先级决策树

### **🚀 自动化程度**
- 端到端自动处理流程
- 智能文件命名和组织
- 完整的可追溯记录

### **🔧 技术先进**
- Gemini AI模型驱动
- 专业提示词工程
- 结构化数据输出

### **📈 实用价值**
- 大幅提升视频管理效率
- 智能内容分类和检索
- 为后续编辑提供精准素材

现在你的视频分析系统具备了真正的AI智能归类能力！🎬✨

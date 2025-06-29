# Video Analyzer Prompts

这个目录包含了 @mixvideo/video-analyzer 包使用的所有提示词文件。

## 文件说明

### `video-analysis.prompt`
统一的视频分析提示词，包含：
- **基础分析**：场景检测、物体识别、内容总结、情感基调、关键词提取
- **产品分析**：产品外观、功能特征、使用场景、目标受众、品牌元素
- **技术分析**：拍摄风格、音频分析

### `folder-matching.prompt`
文件夹匹配提示词模板，用于：
- 分析视频内容描述
- 推荐最合适的文件夹
- 提供匹配评分和原因

## 设计理念

### 🎯 **简化原则**
- **一个提示词解决所有问题**：不再需要记住11种不同的提示词类型
- **智能分析**：让AI自动判断哪些分析维度适用于当前视频
- **用户友好**：直接修改文件即可自定义提示词

### 📁 **文件优势**
1. **易于修改**：用户可以直接编辑 `.prompt` 文件
2. **版本控制**：提示词变更可以通过Git跟踪
3. **团队协作**：团队成员可以共享和讨论提示词改进
4. **环境隔离**：不同环境可以使用不同的提示词文件

## 使用方法

### 基础使用
```typescript
import { getVideoAnalysisPrompt, formatFolderMatchingPrompt } from '@mixvideo/video-analyzer';

// 获取视频分析提示词
const videoPrompt = getVideoAnalysisPrompt();

// 格式化文件夹匹配提示词
const folderPrompt = formatFolderMatchingPrompt(
  '这是一个产品展示视频',
  ['产品', '营销', '演示']
);
```

### 自定义提示词
1. 直接编辑 `prompts/video-analysis.prompt` 文件
2. 修改 `prompts/folder-matching.prompt` 文件
3. 调用 `reloadPrompts()` 重新加载（开发环境）

### 向后兼容
```typescript
// 旧的API仍然可用，但现在都指向统一的提示词
import { ANALYSIS_PROMPTS, PRODUCT_ANALYSIS_PROMPTS } from '@mixvideo/video-analyzer';

const prompt1 = ANALYSIS_PROMPTS.COMPREHENSIVE;
const prompt2 = PRODUCT_ANALYSIS_PROMPTS.APPEARANCE;
// prompt1 === prompt2 === getVideoAnalysisPrompt()
```

## 最佳实践

### ✅ **推荐做法**
- 使用 `getVideoAnalysisPrompt()` 获取视频分析提示词
- 直接修改 `.prompt` 文件来自定义提示词
- 使用版本控制跟踪提示词变更
- 在不同环境使用不同的提示词文件

### ❌ **避免做法**
- 不要在代码中硬编码提示词
- 不要为每种分析类型创建单独的提示词
- 不要忽略向后兼容性

## 迁移指南

### 从旧版本迁移
如果您之前使用多种提示词类型：

```typescript
// 旧方式（仍然可用）
const scenePrompt = ANALYSIS_PROMPTS.SCENE_DETECTION;
const productPrompt = ANALYSIS_PROMPTS.PRODUCT_FOCUSED;

// 新方式（推荐）
const unifiedPrompt = getVideoAnalysisPrompt();
```

### 自定义提示词迁移
如果您之前有自定义提示词：

1. 将自定义内容合并到 `video-analysis.prompt` 文件中
2. 确保包含所有必要的分析维度
3. 测试新的统一提示词是否满足需求

## 技术细节

- 提示词文件使用 UTF-8 编码
- 支持中文内容
- 自动缓存以提高性能
- 支持运行时重新加载
- 完全向后兼容

## 版本历史

- **v2.0.0**: 引入文件化提示词系统，简化为统一提示词
- **v1.0.0**: 原始的多类型提示词系统

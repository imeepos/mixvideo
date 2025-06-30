# Gemini视频分析器

基于 `@mixvideo/gemini` 包实现模式的Python版本Gemini视频分析器，提供完整的视频内容分析功能。

## 🌟 特性

### 核心功能
- 🎬 **视频内容分析**: 使用Gemini 2.5 Flash模型分析视频内容
- 🔐 **自动认证**: 集成Google Access Token自动获取和刷新
- 🌐 **Cloudflare Gateway**: 通过Cloudflare Gateway访问Vertex AI API
- 💾 **智能缓存**: 本地缓存分析结果，避免重复分析
- 🔄 **重试机制**: 自动重试失败的请求
- 📊 **进度跟踪**: 详细的分析进度回调

### 高级特性
- 🗂️ **缓存管理**: 自动过期清理和缓存统计
- 🔧 **灵活配置**: 支持自定义区域、模型、超时等参数
- 📝 **结构化输出**: 标准化的JSON格式分析结果
- 🛡️ **错误处理**: 完善的异常处理和日志记录

## 📦 安装依赖

```bash
pip install requests
```

## 🚀 快速开始

### 基础使用

```python
from gemini_video_analyzer import create_gemini_analyzer

# 创建分析器
analyzer = create_gemini_analyzer(
    cloudflare_project_id="your_project_id",
    cloudflare_gateway_id="your_gateway_id",
    google_project_id="your_google_project_id"
)

# 分析视频
def progress_callback(progress):
    print(f"{progress.step} ({progress.progress}%)")

result = analyzer.analyze_video(
    video_path="video.mp4",
    prompt="请分析这个视频的内容",
    progress_callback=progress_callback
)

print(result)
```

### 自定义配置

```python
from gemini_video_analyzer import GeminiVideoAnalyzer, GeminiConfig

# 创建自定义配置
config = GeminiConfig(
    cloudflare_project_id="your_project_id",
    cloudflare_gateway_id="your_gateway_id",
    google_project_id="your_google_project_id",
    regions=["us-central1", "europe-west1"],
    model_name="gemini-2.5-flash",
    enable_cache=True,
    cache_dir="./custom_cache",
    max_retries=5,
    timeout=180
)

analyzer = GeminiVideoAnalyzer(config)
```

## 📋 配置选项

### GeminiConfig 参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `cloudflare_project_id` | str | "" | Cloudflare项目ID |
| `cloudflare_gateway_id` | str | "" | Cloudflare网关ID |
| `google_project_id` | str | "" | Google项目ID |
| `regions` | List[str] | ["us-central1", "us-east1", "europe-west1"] | 可用区域列表 |
| `model_name` | str | "gemini-2.5-flash" | 使用的模型名称 |
| `enable_cache` | bool | True | 是否启用缓存 |
| `cache_dir` | str | ".cache/gemini_analysis" | 缓存目录 |
| `cache_expiry` | int | 604800 | 缓存过期时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | int | 5 | 重试延迟（秒） |
| `timeout` | int | 120 | 请求超时时间（秒） |

## 🎯 使用示例

### 1. 基础视频分析

```python
# 运行基础示例
python example_usage.py basic
```

### 2. 批量分析

```python
# 批量分析当前目录下的所有视频
python example_usage.py batch
```

### 3. 缓存管理

```python
# 查看和清理缓存
python example_usage.py cache
```

### 4. 自定义配置

```python
# 查看自定义配置示例
python example_usage.py config
```

## 📊 分析结果格式

```json
{
  "video_info": {
    "file_name": "video.mp4",
    "file_path": "/path/to/video.mp4",
    "file_size": 12345678,
    "analysis_time": "2024-01-01 12:00:00",
    "model_used": "gemini-2.5-flash",
    "config": {
      "cache_enabled": true,
      "regions": ["us-central1"]
    }
  },
  "analysis_result": {
    "summary": "视频内容总结",
    "scenes": [...],
    "objects": [...],
    "quality": {...}
  },
  "metadata": {
    "response_length": 1234,
    "candidates_count": 1,
    "success": true
  },
  "raw_response": {...}
}
```

## 🔧 API 参考

### GeminiVideoAnalyzer

#### 主要方法

- `analyze_video(video_path, prompt, progress_callback=None)`: 分析视频
- `get_cache_stats()`: 获取缓存统计信息
- `clean_expired_cache()`: 清理过期缓存

#### 进度回调

```python
def progress_callback(progress: AnalysisProgress):
    print(f"阶段: {progress.stage}")
    print(f"步骤: {progress.step}")
    print(f"进度: {progress.progress}%")
    print(f"文件: {progress.current_file}")
```

### 便利函数

- `create_gemini_analyzer(**kwargs)`: 快速创建分析器实例

## 🗂️ 缓存机制

### 缓存特性
- **自动缓存**: 分析结果自动保存到本地
- **文件校验**: 基于文件内容校验，文件变更时自动失效
- **过期管理**: 自动清理过期的缓存文件
- **统计信息**: 提供详细的缓存使用统计

### 缓存管理

```python
# 获取缓存统计
stats = analyzer.get_cache_stats()
print(f"缓存文件数: {stats['total_files']}")
print(f"缓存大小: {stats['total_size']} bytes")

# 清理过期缓存
result = analyzer.clean_expired_cache()
print(f"清理了 {result['removed']} 个过期文件")
```

## 🔍 错误处理

### 常见错误

1. **认证失败**: 检查Cloudflare和Google项目配置
2. **文件过大**: 视频文件超过100MB限制
3. **网络超时**: 调整timeout参数或检查网络连接
4. **API限制**: 检查API配额和使用限制

### 日志记录

```python
import logging
logging.basicConfig(level=logging.INFO)

# 分析器会自动输出详细日志
analyzer = create_gemini_analyzer()
```

## 🔄 与TypeScript版本的对应关系

| Python | TypeScript (@mixvideo/gemini) |
|--------|-------------------------------|
| `GeminiVideoAnalyzer` | `GoogleGenaiClient` |
| `get_access_token()` | `useGeminiAccessToken()` |
| `_upload_video_file()` | `uploadFileToGemini()` |
| `_generate_content()` | `generateContent()` |
| `GeminiConfig` | `GoogleGenaiClientConfig` |

## 📝 注意事项

1. **配置要求**: 需要正确配置Cloudflare和Google项目参数
2. **文件大小**: 建议视频文件小于100MB
3. **网络环境**: 需要稳定的网络连接访问Google API
4. **缓存空间**: 缓存会占用本地磁盘空间，定期清理
5. **API配额**: 注意Google API的使用配额限制

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

MIT License

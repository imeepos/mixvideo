# 🎵 音频节奏卡点提取工具

这是一套专为视频混剪设计的Python音频分析工具，能够自动检测音频中的节拍点、分析音乐结构，并提供智能剪辑建议。

## ✨ 功能特性

### 🎯 基础功能
- **节拍检测**: 自动识别音频的BPM和节拍点
- **起始点检测**: 精确定位音频中的重要时刻
- **节奏分析**: 分析节拍稳定性和节奏模式
- **可视化**: 生成直观的分析图表

### 🚀 高级功能
- **音乐结构分析**: 自动识别intro、verse、chorus、bridge、outro段落
- **高光时刻检测**: 找到最适合做卡点的位置
- **智能剪辑建议**: 提供动态、平滑、节奏三种剪辑风格
- **能量分析**: 分析音频的能量分布和变化
- **完整报告**: 导出JSON格式的详细分析报告

## 📦 安装依赖

### 自动安装（推荐）
```bash
python setup_audio_tools.py
```

### 手动安装
```bash
pip install -r requirements.txt
```

### 系统依赖
- **Linux**: `sudo apt-get install libsndfile1 libsndfile1-dev ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: 下载安装 [FFmpeg](https://ffmpeg.org/download.html)

## 🎮 使用方法

### 1. 基础节拍检测

```bash
# 基本使用
python audio_beat_detection.py your_music.mp3

# 生成可视化图表
python audio_beat_detection.py your_music.mp3 -v

# 指定输出格式
python audio_beat_detection.py your_music.mp3 -f csv -o my_beats

# 调整检测参数
python audio_beat_detection.py your_music.mp3 -t 0.5 -s 44100
```

### 2. 高级音频分析

```bash
# 完整分析
python advanced_audio_analyzer.py your_music.mp3
```

### 3. Python代码中使用

```python
from audio_beat_detection import AudioBeatDetector
from advanced_audio_analyzer import AdvancedAudioAnalyzer

# 基础节拍检测
detector = AudioBeatDetector()
detector.load_audio("music.mp3")
tempo, beat_times = detector.detect_tempo_and_beats()
detector.export_beat_points("beats.json")

# 高级分析
analyzer = AdvancedAudioAnalyzer()
analyzer.load_audio("music.mp3")
analyzer.detect_tempo_and_beats()
analyzer.detect_music_structure()

# 获取高光时刻
highlights = analyzer.find_highlight_moments(top_n=5)

# 生成剪辑建议
cuts = analyzer.generate_cut_points(target_duration=60.0, style='dynamic')

# 导出完整报告
analyzer.export_analysis_report("analysis_report.json")
```

## 📊 输出格式

### JSON格式示例
```json
{
  "metadata": {
    "tempo_bpm": 128.5,
    "total_beats": 245,
    "audio_duration": 180.5,
    "analysis_timestamp": "2024-01-15T10:30:00"
  },
  "beat_points": [0.468, 0.936, 1.404, ...],
  "music_structure": [
    {
      "start_time": 0.0,
      "end_time": 8.0,
      "segment_type": "intro",
      "energy_level": 0.15
    }
  ],
  "highlight_moments": [
    {
      "time": 32.5,
      "intensity": 0.85,
      "description": "能量爆发 (chorus)"
    }
  ]
}
```

### CSV格式示例
```csv
序号,时间(秒),时间(分:秒)
1,0.468,0:00.468
2,0.936,0:00.936
3,1.404,0:01.404
```

## 🎨 可视化图表

工具会生成包含以下内容的可视化图表：

1. **音频波形与节拍点**: 显示原始音频和检测到的节拍位置
2. **起始强度分析**: 显示音频的起始强度变化
3. **节拍间隔分析**: 分析节拍的稳定性
4. **音乐结构标记**: 标识不同的音乐段落
5. **能量分布**: 显示音频的能量变化
6. **高光时刻**: 标记最佳卡点位置

## 🎯 应用场景

### 视频混剪
- 自动识别音乐的节拍点进行精准卡点
- 根据音乐结构安排视频片段
- 在高能量时刻放置重要画面

### 音乐分析
- 分析歌曲的结构和节奏特征
- 比较不同歌曲的节奏模式
- 为DJ混音提供节拍信息

### 自动剪辑
- 根据音乐节奏自动生成剪辑点
- 智能选择最佳的音频片段
- 生成不同风格的剪辑建议

## ⚙️ 参数说明

### 基础检测参数
- `sample_rate`: 音频采样率 (默认: 22050)
- `threshold`: 起始检测阈值 (默认: 0.3)
- `hop_length`: 分析窗口跳跃长度 (默认: 512)

### 高级分析参数
- `target_duration`: 目标剪辑时长 (默认: 60秒)
- `style`: 剪辑风格 ('dynamic', 'smooth', 'rhythmic')
- `top_n`: 返回的高光时刻数量 (默认: 5)

## 🔧 故障排除

### 常见问题

1. **ImportError: No module named 'librosa'**
   ```bash
   pip install librosa
   ```

2. **音频文件无法加载**
   - 确保安装了FFmpeg
   - 检查音频文件格式是否支持
   - 尝试转换为WAV或MP3格式

3. **分析结果不准确**
   - 调整threshold参数
   - 尝试不同的sample_rate
   - 确保音频质量良好

### 性能优化

- 对于长音频文件，考虑降低采样率
- 使用较大的hop_length可以提高处理速度
- 对于实时应用，可以分段处理音频

## 📝 示例文件

运行以下命令生成示例：

```bash
python example_usage.py
```

这将创建一个测试音频文件并演示所有功能。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📄 许可证

MIT License - 详见LICENSE文件

---

🎵 **让音频分析变得简单，让视频剪辑更加智能！**

# @mixvideo/cli

🎬 AI-powered video analysis and editing CLI tool for automatic video classification and Jianying draft generation.

## Features

- 🤖 **AI Video Analysis**: Powered by Gemini AI for intelligent video content analysis
- 📁 **Automatic Classification**: Smart categorization of videos into folders
- 🎯 **Intelligent File Naming**: Content-based file naming with original name preservation
- 📋 **Jianying Integration**: Generate draft files for Jianying video editor
- 🔄 **Caching System**: Efficient caching to avoid duplicate processing
- 🛡️ **Safe Operations**: Copy mode by default to preserve original files

## Installation

```bash
npm install -g @mixvideo/cli
```

## Quick Start

### 1. Analyze Videos

Analyze videos in a directory and automatically classify them:

```bash
mixvideo analyze ./videos
```

### 2. Generate Jianying Drafts

Generate draft files for Jianying from video directory:

```bash
mixvideo generate from-videos ./videos
```

## Commands

### `analyze`

Analyze video files and automatically classify them into folders.

```bash
mixvideo analyze <source> [options]
```

**Options:**
- `-o, --output <path>`: Output directory (default: "outputs")
- `-m, --mode <mode>`: Analysis mode - gemini|gpt4 (default: "gemini")
- `--temperature <number>`: AI model temperature (0.0-1.0, default: "0.3")
- `--max-tokens <number>`: Maximum output tokens (default: "4096")
- `--move-files`: Move files instead of copying (default: false)
- `--create-backup`: Create backup files (default: false)
- `--confidence <number>`: Minimum confidence for file movement (0.0-1.0, default: "0.4")

**Example:**
```bash
mixvideo analyze ./my-videos -o ./organized --mode gemini --confidence 0.6
```

### `generate`

Generate Jianying draft files from videos or templates.

#### `generate from-videos`

Generate draft from video directory:

```bash
mixvideo generate from-videos <source> [options]
```

**Options:**
- `-o, --output <path>`: Output file path (default: "draft_content.json")
- `--title <title>`: Project title (default: "视频项目")
- `--fps <number>`: Frame rate (default: "30")
- `--resolution <resolution>`: Resolution - 1080p|720p|4k (default: "1080p")

#### `generate from-template`

Generate draft from template:

```bash
mixvideo generate from-template <dir> [options]
```

**Options:**
- `-t, --template <template>`: Template file path (default: "draft_content.json")

### `login` / `logout`

Authentication commands (coming soon):

```bash
mixvideo login -u <username> -p <password>
mixvideo logout
```

## Configuration

The CLI tool automatically creates the following folder structure for video classification:

- 📁 产品展示 (Product Display)
- 📁 产品使用 (Product Usage)
- 📁 生活场景 (Life Scenes)
- 📁 模特实拍 (Model Photography)
- 📁 服装配饰 (Fashion & Accessories)
- 📁 美妆护肤 (Beauty & Skincare)
- 📁 其他 (Others)

## Environment Variables

Set up your AI API credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

## Examples

### Basic Video Analysis

```bash
# Analyze videos in current directory
mixvideo analyze ./videos

# Analyze with custom output directory
mixvideo analyze ./raw-videos -o ./organized-videos

# Use GPT-4 mode with higher confidence
mixvideo analyze ./videos --mode gpt4 --confidence 0.8
```

### Generate Jianying Drafts

```bash
# Generate draft from video directory
mixvideo generate from-videos ./organized-videos/产品展示

# Generate with custom settings
mixvideo generate from-videos ./videos --title "我的产品视频" --fps 60 --resolution 4k

# Generate from template
mixvideo generate from-template ./materials -t ./templates/product-template.json
```

## Supported Video Formats

- MP4, MOV, AVI, MKV
- WEBM, FLV, WMV, M4V
- 3GP, TS

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/imeepos/mixvideo).

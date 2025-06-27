# 剪映草稿元信息更新脚本

这个目录包含用于自动更新 `draft_meta_info.json` 文件的脚本工具。

## 📁 文件说明

### 核心文件
- `draft_content.json` - 剪映草稿内容文件（示例）
- `draft_meta_info.json` - 剪映草稿元信息文件

### 脚本文件
- `update-draft-meta.ts` - 完整的草稿元信息更新脚本
- `quick-update.ts` - 快速更新脚本（扫描当前目录）
- `package.json` - 项目配置文件

## 🚀 使用方法

### 1. 快速更新（推荐）

扫描当前目录下的所有文件夹，自动生成 `draft_meta_info.json`：

```bash
# 方法1: 直接运行
ts-node quick-update.ts

# 方法2: 使用 npm 脚本
npm run quick
```

### 2. 完整更新脚本

更灵活的更新脚本，支持自定义路径：

```bash
# 基本用法（扫描当前目录）
ts-node update-draft-meta.ts

# 指定扫描目录
ts-node update-draft-meta.ts --scan /path/to/projects

# 指定 JSON 文件位置
ts-node update-draft-meta.ts --json ./my-meta.json

# 完整参数示例
ts-node update-draft-meta.ts \
  --json ./draft_meta_info.json \
  --scan ./projects \
  --root /root/path

# 查看帮助
ts-node update-draft-meta.ts --help
# 或
npm run help
```

### 3. 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--json` | `-j` | 指定 JSON 文件路径 | `./draft_meta_info.json` |
| `--scan` | `-s` | 指定扫描目录路径 | JSON 文件所在目录 |
| `--root` | `-r` | 指定根路径 | 扫描路径 |
| `--help` | `-h` | 显示帮助信息 | - |

## 📋 功能特性

### ✅ 自动扫描
- 扫描指定目录下的所有文件夹
- 自动跳过隐藏文件夹和 `node_modules`
- 支持自定义扫描路径

### ✅ 智能生成
- 自动生成唯一的 UUID 作为草稿 ID
- 自动设置创建和修改时间戳
- 尝试从 `draft_content.json` 读取真实时长
- 估算文件夹大小

### ✅ 格式兼容
- 生成的 JSON 格式完全兼容剪映
- 使用 Windows 路径格式（反斜杠）
- 包含所有必需的字段

## 📊 输出示例

运行脚本后会生成类似这样的 `draft_meta_info.json`：

```json
{
  "all_draft_store": [
    {
      "draft_cloud_last_action_download": false,
      "draft_cloud_purchase_info": "",
      "draft_cloud_template_id": "",
      "draft_cloud_tutorial_info": "",
      "draft_cloud_videocut_purchase_info": "",
      "draft_cover": "C:\\path\\to\\project1\\draft_cover.jpg",
      "draft_fold_path": "C:\\path\\to\\project1",
      "draft_id": "A1B2C3D4-E5F6-4789-A012-B3C4D5E6F789",
      "draft_is_ai_shorts": false,
      "draft_is_invisible": false,
      "draft_json_file": "C:\\path\\to\\project1\\draft_content.json",
      "draft_name": "project1",
      "draft_new_version": "",
      "draft_root_path": "C:\\path\\to",
      "draft_timeline_materials_size": 2048576,
      "draft_type": "",
      "tm_draft_cloud_completed": "",
      "tm_draft_cloud_modified": 0,
      "tm_draft_create": 1751234567890123,
      "tm_draft_modified": 1751234567890123,
      "tm_draft_removed": 0,
      "tm_duration": 10000000
    }
  ],
  "draft_ids": 2,
  "root_path": "C:\\path\\to"
}
```

## 🔧 安装和设置

### 1. 安装依赖

```bash
npm install
```

### 2. 运行脚本

```bash
# 快速更新当前目录
npm run quick

# 完整更新（带参数）
npm run update

# 查看帮助
npm run help
```

## 💡 使用场景

### 场景1: 项目文件夹管理
当你有多个剪映项目文件夹时，可以快速生成元信息文件：

```bash
# 假设你的目录结构是：
# /projects/
#   ├── 项目1/
#   ├── 项目2/
#   ├── 项目3/
#   └── draft_meta_info.json

cd /projects
ts-node quick-update.ts
```

### 场景2: 批量导入项目
当你需要将多个项目导入剪映时：

```bash
# 扫描指定目录并生成元信息
ts-node update-draft-meta.ts --scan /path/to/projects --root /jianying/root
```

### 场景3: 自定义配置
当你需要特定的配置时：

```bash
# 自定义所有参数
ts-node update-draft-meta.ts \
  --json /custom/path/meta.json \
  --scan /projects \
  --root /jianying/root
```

## 🎯 注意事项

1. **路径格式**: 脚本会自动将路径转换为 Windows 格式（使用反斜杠）
2. **文件夹过滤**: 自动跳过以 `.` 开头的隐藏文件夹和 `node_modules`
3. **时长读取**: 如果文件夹中存在 `draft_content.json`，会尝试读取真实时长
4. **UUID 生成**: 每次运行都会生成新的 UUID，确保项目 ID 唯一性
5. **备份建议**: 运行前建议备份原有的 `draft_meta_info.json` 文件

## 🔗 相关工具

更完整的剪映文件处理功能请查看 `packages/jianying` 包，它提供了：
- 完整的草稿文件解析
- 增强分析功能  
- 草稿文件生成
- 丰富的工具函数

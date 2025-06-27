# 剪映草稿元信息更新脚本使用指南

## 🎯 功能说明

这个脚本可以扫描指定目录下的所有文件夹，为每个文件夹自动生成一个剪映草稿项目条目，并更新 `draft_meta_info.json` 文件。

## 🚀 快速开始

### 1. 最简单的使用方式

```bash
# 扫描当前目录并更新 draft_meta_info.json
npm run quick
```

### 2. 完整功能使用

```bash
# 查看帮助
npm run help

# 基本更新
npm run update

# 运行演示
npm run demo

# 清理演示文件
npm run cleanup
```

## 📋 脚本说明

### `quick-update.ts` - 快速更新脚本
- **用途**: 扫描当前目录下的所有文件夹
- **输出**: 更新 `draft_meta_info.json` 文件
- **特点**: 简单快速，无需参数

### `update-draft-meta.ts` - 完整更新脚本
- **用途**: 灵活的更新脚本，支持自定义参数
- **参数**: 
  - `--json` / `-j`: 指定 JSON 文件路径
  - `--scan` / `-s`: 指定扫描目录
  - `--root` / `-r`: 指定根路径
  - `--help` / `-h`: 显示帮助

### `demo.ts` - 演示脚本
- **用途**: 创建演示项目并展示脚本功能
- **特点**: 自动创建测试文件夹和示例数据

## 💡 使用场景

### 场景1: 项目文件夹批量管理
```bash
# 你的目录结构：
# /my-projects/
#   ├── 项目A/
#   ├── 项目B/
#   ├── 项目C/
#   └── draft_meta_info.json (要生成的文件)

cd /my-projects
ts-node quick-update.ts
```

### 场景2: 自定义路径扫描
```bash
# 扫描指定目录，输出到指定文件
ts-node update-draft-meta.ts \
  --scan /path/to/projects \
  --json /output/meta.json \
  --root /jianying/root
```

## 📊 输出格式

生成的 `draft_meta_info.json` 包含：

```json
{
  "all_draft_store": [
    {
      "draft_id": "唯一UUID",
      "draft_name": "文件夹名称",
      "draft_fold_path": "文件夹完整路径",
      "draft_json_file": "草稿文件路径",
      "tm_duration": "项目时长（微秒）",
      "draft_timeline_materials_size": "文件夹大小",
      "tm_draft_create": "创建时间戳",
      "tm_draft_modified": "修改时间戳",
      // ... 其他剪映所需字段
    }
  ],
  "draft_ids": "项目数量+1",
  "root_path": "根路径"
}
```

## ⚙️ 智能特性

### ✅ 自动时长检测
- 如果文件夹中存在 `draft_content.json`，会自动读取真实时长
- 否则使用默认值 0

### ✅ 文件夹过滤
- 自动跳过隐藏文件夹（以 `.` 开头）
- 自动跳过 `node_modules` 目录

### ✅ 路径格式化
- 自动转换为 Windows 路径格式（使用反斜杠）
- 确保与剪映格式兼容

### ✅ UUID 生成
- 为每个项目生成唯一的 UUID
- 确保项目 ID 不重复

## 🔧 开发和扩展

### 安装依赖
```bash
npm install
```

### 直接运行脚本
```bash
# 快速更新
ts-node quick-update.ts

# 完整更新
ts-node update-draft-meta.ts --help

# 演示
ts-node demo.ts
```

### 自定义修改
脚本使用 TypeScript 编写，可以根据需要修改：
- 调整文件夹过滤规则
- 修改时长计算逻辑
- 添加更多元数据字段
- 自定义路径格式

## 📚 相关工具

更完整的剪映文件处理功能请查看 `packages/jianying` 包：
- 完整的草稿文件解析
- 增强分析功能
- 草稿文件生成
- 丰富的工具函数

## ⚠️ 注意事项

1. **备份重要文件**: 运行前建议备份原有的 `draft_meta_info.json`
2. **路径格式**: 生成的路径使用 Windows 格式（反斜杠）
3. **文件权限**: 确保有目录读取和文件写入权限
4. **时长单位**: 时长使用微秒为单位（1秒 = 1,000,000微秒）

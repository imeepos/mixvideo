# 剪映项目管理系统

这是一个用于管理剪映草稿项目的完整系统，支持扫描、查看、创建和管理剪映项目文件。

## 📁 项目结构

每个剪映项目包含3个核心JSON文件：
- `draft_content.json` - 项目内容（时间轴、轨道、素材等）
- `draft_meta_info.json` - 项目元数据（素材信息、创建时间等）
- `draft_virtual_store.json` - 虚拟存储信息

## 🔧 组件说明

### 1. 核心管理器

#### `jianying_project_manager.py`
- **功能**: 主项目管理器，遍历目录并管理所有项目
- **特点**: 
  - 自动扫描项目目录
  - 验证项目文件完整性
  - 提供项目CRUD操作
  - 统计项目信息

#### `draft_meta_manager.py`
- **功能**: 管理 `draft_meta_info.json` 和 `draft_virtual_store.json`
- **特点**:
  - 素材元数据管理
  - 支持视频、音频、图片等多种素材类型
  - 自动获取文件信息（时长、分辨率等）

#### `draft_content_manager.py`
- **功能**: 管理 `draft_content.json`
- **特点**:
  - 时间轴管理
  - 轨道和素材引用管理
  - 特效和转场管理

### 2. 用户界面

#### `jianying_manager_gui.py`
- **功能**: 图形界面管理工具
- **特点**:
  - 直观的项目列表显示
  - 项目详情查看
  - 创建和删除项目
  - 导出项目摘要

#### `jianying_cli.py`
- **功能**: 命令行管理工具
- **特点**:
  - 批量操作支持
  - 脚本自动化友好
  - 详细的输出控制

## 🚀 使用方法

### GUI界面使用

```bash
# 启动GUI界面
python jianying_manager_gui.py
```

**操作步骤**:
1. 点击"浏览"选择剪映项目目录
2. 点击"扫描"扫描项目
3. 在项目列表中查看所有项目
4. 双击项目查看详情
5. 右键菜单进行项目操作

### 命令行使用

#### 扫描项目目录
```bash
# 基本扫描
python jianying_cli.py scan /path/to/jianying/projects

# 详细扫描并保存摘要
python jianying_cli.py scan /path/to/projects -v -o summary.json
```

#### 列出项目
```bash
# 列出所有项目
python jianying_cli.py list /path/to/projects

# 只列出有效项目
python jianying_cli.py list /path/to/projects --valid-only

# 详细列出无效项目
python jianying_cli.py list /path/to/projects --invalid-only -v
```

#### 查看项目信息
```bash
# 基本信息
python jianying_cli.py info /path/to/projects project_name

# 详细信息
python jianying_cli.py info /path/to/projects project_name --detailed
```

#### 创建新项目
```bash
python jianying_cli.py create /path/to/projects new_project_name
```

#### 删除项目
```bash
# 交互式删除
python jianying_cli.py delete /path/to/projects project_name

# 强制删除
python jianying_cli.py delete /path/to/projects project_name --force
```

#### 导出项目
```bash
python jianying_cli.py export /path/to/projects project_name /export/path
```

## 📊 项目验证

系统会自动验证项目的有效性：

### 有效项目条件
- ✅ 包含所有3个必需的JSON文件
- ✅ JSON文件格式正确
- ✅ 文件可以正常读取

### 无效项目类型
- ❌ 缺少必需文件
- ❌ JSON格式错误
- ❌ 文件读取权限问题

## 🔍 项目信息

### 基本信息
- 项目名称和路径
- 文件大小统计
- 创建和修改时间

### 详细信息
- 项目时长
- 轨道数量
- 素材数量和类型统计
- 元数据详情

## 📝 编程接口

### 基本用法

```python
from jianying.jianying_project_manager import JianyingProjectManager

# 创建管理器
manager = JianyingProjectManager("/path/to/projects")

# 扫描项目
projects = manager.scan_projects()

# 获取有效项目
valid_projects = manager.get_valid_projects()

# 获取项目管理器
content_mgr = manager.get_project_content_manager("project_name")
meta_mgr = manager.get_project_meta_manager("project_name")

# 创建新项目
manager.create_new_project("new_project")

# 获取项目摘要
summary = manager.get_project_summary()
```

### 内容管理

```python
from jianying.draft_content_manager import DraftContentManager

# 创建内容管理器
content_mgr = DraftContentManager("/path/to/project")

# 获取项目信息
info = content_mgr.get_project_info()

# 添加视频素材
content_mgr.add_video_material("/path/to/video.mp4")

# 保存项目
content_mgr.save_project()
```

### 元数据管理

```python
from jianying.draft_meta_manager import DraftMetaManager

# 创建元数据管理器
meta_mgr = DraftMetaManager("/path/to/project")

# 添加素材
meta_mgr.add_material("/path/to/video.mp4", "video")

# 获取所有素材
materials = meta_mgr.get_all_materials()

# 保存元数据
meta_mgr.save_metadata()
```

## 🛠️ 高级功能

### 批量操作

```bash
# 批量扫描多个目录
for dir in /path/to/projects/*; do
    python jianying_cli.py scan "$dir" -o "${dir}_summary.json"
done

# 批量导出有效项目
python jianying_cli.py list /path/to/projects --valid-only | while read project; do
    python jianying_cli.py export /path/to/projects "$project" "/backup/$project"
done
```

### 项目模板

```python
# 使用模板创建项目
template_data = {
    "duration": 30000000,  # 30秒
    "resolution": {"width": 1080, "height": 1920},
    "fps": 30
}

manager.create_new_project("template_project", template_data)
```

## 📋 注意事项

### 文件路径
- 支持绝对路径和相对路径
- Windows路径使用反斜杠或正斜杠都可以
- 建议使用绝对路径避免路径问题

### 权限要求
- 读取权限：扫描和查看项目
- 写入权限：创建、修改、删除项目
- 执行权限：访问目录

### 性能考虑
- 大量项目时扫描可能较慢
- 建议使用命令行工具进行批量操作
- GUI界面适合交互式管理

## 🔧 故障排除

### 常见问题

**Q: 扫描时发现项目无效？**
A: 检查项目目录是否包含所有3个JSON文件，确认文件格式正确。

**Q: 无法创建新项目？**
A: 确认目标目录有写入权限，项目名称不包含特殊字符。

**Q: GUI界面无法启动？**
A: 确认已安装tkinter，在某些Linux发行版需要单独安装python3-tk。

**Q: 命令行工具报错？**
A: 使用 `-v` 参数查看详细错误信息，检查Python路径和模块导入。

### 日志调试

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后运行你的代码，会输出详细日志
```

## 🎯 最佳实践

1. **定期备份**: 在操作项目前先备份
2. **验证完整性**: 定期扫描检查项目状态
3. **统一命名**: 使用一致的项目命名规范
4. **权限管理**: 确保适当的文件访问权限
5. **版本控制**: 重要项目考虑使用版本控制

---

**剪映项目管理系统让您轻松管理大量剪映项目，提高工作效率！** 🎬

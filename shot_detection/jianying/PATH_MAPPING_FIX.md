# 路径映射修复说明

## 问题描述

在生产环境中，用户选择素材目录 `C:\Users\imeep\Desktop\mertial\AI视频\`，但生成的项目文件中的路径变成了临时目录路径：
```
C:\\Users\\imeep\\AppData\\Local\\Temp\\tmpteo64f_k\\resources\\0630-交付素材2\\背景1\\1751264340625.mp4
```

而期望的路径应该是：
```
C:\Users\imeep\Desktop\mertial\AI视频\0630-交付素材2\背景1\1751264340625.mp4
```

## 问题原因

GUI应用（`gui_app.py` 和 `video_mix_gui.py`）为了符合工作流程的目录结构要求，会：

1. 创建临时工作目录：`tempfile.mkdtemp()`
2. 将用户选择的素材目录复制到临时目录的 `resources` 子目录
3. 工作流程扫描临时目录中的文件，生成的路径就是临时目录路径
4. 最终项目文件中包含临时目录路径而不是原始路径

## 修复方案

### 1. 修改 `VideoAllocationAlgorithm` 类

- 添加 `original_materials_dir` 参数，用于存储原始素材目录路径
- 添加 `_map_to_original_path()` 方法，将临时目录路径映射回原始路径
- 在生成项目文件时使用映射后的原始路径

### 2. 修改 `DouyinVideoWorkflow` 类

- 添加 `original_materials_dir` 参数
- 将原始素材目录传递给 `VideoAllocationAlgorithm`

### 3. 修改GUI应用

- `gui_app.py`：在创建工作流程实例时传递原始素材目录
- `video_mix_gui.py`：在创建工作流程实例时传递原始素材目录

## 修复后的工作流程

1. 用户选择素材目录：`C:\Users\imeep\Desktop\mertial\AI视频\`
2. GUI创建临时目录并复制素材
3. 工作流程扫描临时目录，但记住原始目录路径
4. 生成项目文件时，将临时路径映射回原始路径
5. 最终项目文件包含正确的原始路径

## 路径映射逻辑

```python
def _map_to_original_path(self, temp_path: str) -> str:
    """将临时目录路径映射回原始路径"""
    if not self.original_materials_dir:
        return temp_path
    
    # 检查是否是临时目录中的路径
    if "resources" in temp_path_obj.parts:
        # 提取 resources 之后的相对路径
        relative_path = extract_relative_path_after_resources(temp_path)
        # 构建原始路径
        original_path = self.original_materials_dir / relative_path
        return str(original_path)
    
    return temp_path
```

## 测试验证

修复后的路径映射功能已通过测试验证：

```
原始素材目录: C:/Users/imeep/Desktop/mertial/AI视频
临时路径: C:/Users/imeep/AppData/Local/Temp/tmpteo64f_k/resources/0630-交付素材2/背景1/1751264340625.mp4
映射后路径: C:/Users/imeep/Desktop/mertial/AI视频/0630-交付素材2/背景1/1751264340625.mp4
映射正确: True
```

## 影响的文件

- `video_allocation_algorithm.py`：添加路径映射功能
- `run_allocation.py`：传递原始素材目录参数
- `gui_app.py`：传递原始素材目录给工作流程
- `video_mix_gui.py`：传递原始素材目录给工作流程

## 向后兼容性

修复保持了向后兼容性：
- 如果不传递 `original_materials_dir` 参数，行为与之前相同
- 现有的命令行工具和直接使用工作流程的代码不受影响
- 只有GUI应用会受益于路径映射功能

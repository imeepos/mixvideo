# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path.cwd()

# 数据文件和目录
datas = [
    # 配置文件
    ('config.py', '.'),
    
    # 工具模块
    ('utils', 'utils'),
    ('detectors', 'detectors'),
    ('processors', 'processors'),
    ('exporters', 'exporters'),
    
    # 字体配置
    ('font_config.py', '.'),
    ('font_config.ini', '.'),
    
    # 示例文件
    ('test_video.mp4', '.'),
    
    # 文档
    ('README.md', '.'),
    ('*.md', '.'),
]

# 隐藏导入
hiddenimports = [
    'cv2',
    'numpy',
    'loguru',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'matplotlib',
    'matplotlib.pyplot',
    'pathlib',
    'threading',
    'subprocess',
    'webbrowser',
    'datetime',
    'json',
    'csv',
    'xml.etree.ElementTree',
    'configparser',
    'dataclasses',
    'typing',
    'collections',
    'itertools',
    'functools',
    'operator',
    'math',
    'statistics',
    'time',
    'os',
    'sys',
    'shutil',
    'tempfile',
    'platform',
    'socket',
    'urllib',
    'http',
    'email',
    'base64',
    'hashlib',
    'uuid',
    'random',
    'string',
    're',
    'glob',
    'fnmatch',
]

# 排除的模块
excludes = [
    'test_*',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'IPython',
    'jupyter',
    'notebook',
]

a = Analysis(
    ['run_gui.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ShotDetectionGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)

# 创建目录分发版本
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ShotDetectionGUI_dist',
)

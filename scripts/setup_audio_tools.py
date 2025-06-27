#!/usr/bin/env python3
"""
音频工具环境设置脚本
自动安装所需依赖并验证环境
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """安装Python依赖"""
    print("🔧 正在安装Python依赖...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Python依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python依赖安装失败: {e}")
        return False


def install_system_dependencies():
    """安装系统依赖（如果需要）"""
    print("🔧 检查系统依赖...")
    
    # 检查是否为Linux系统，如果是则尝试安装音频库
    if sys.platform.startswith('linux'):
        try:
            # 尝试安装libsndfile（soundfile依赖）
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=False, capture_output=True)
            
            subprocess.run([
                "sudo", "apt-get", "install", "-y", 
                "libsndfile1", "libsndfile1-dev", "ffmpeg"
            ], check=False, capture_output=True)
            
            print("✅ 系统依赖检查完成")
        except Exception as e:
            print(f"⚠️  系统依赖安装可能需要手动处理: {e}")
    
    elif sys.platform == 'darwin':  # macOS
        print("💡 macOS用户建议使用 Homebrew 安装 ffmpeg:")
        print("   brew install ffmpeg")
    
    elif sys.platform == 'win32':  # Windows
        print("💡 Windows用户建议下载并安装 FFmpeg")
        print("   https://ffmpeg.org/download.html")


def verify_installation():
    """验证安装是否成功"""
    print("🧪 验证安装...")
    
    try:
        import librosa
        import numpy as np
        import matplotlib.pyplot as plt
        import soundfile as sf
        
        print(f"✅ librosa版本: {librosa.__version__}")
        print(f"✅ numpy版本: {np.__version__}")
        print(f"✅ matplotlib版本: {plt.matplotlib.__version__}")
        
        # 测试基本功能
        test_signal = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 22050))
        tempo, beats = librosa.beat.beat_track(y=test_signal, sr=22050)
        
        print("✅ 基本功能测试通过")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False


def create_example_script():
    """创建示例使用脚本"""
    example_script = '''#!/usr/bin/env python3
"""
音频节拍检测使用示例
"""

from audio_beat_detection import AudioBeatDetector
import numpy as np

def create_test_audio():
    """创建测试音频（120 BPM的鼓点）"""
    sample_rate = 22050
    duration = 10  # 10秒
    bpm = 120
    
    # 计算节拍间隔
    beat_interval = 60.0 / bpm  # 0.5秒
    
    # 生成时间轴
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 生成基础音频
    audio = np.zeros_like(t)
    
    # 添加节拍点（鼓点效果）
    beat_times = np.arange(0, duration, beat_interval)
    for beat_time in beat_times:
        # 在每个节拍点添加一个短促的音调
        start_idx = int(beat_time * sample_rate)
        end_idx = min(start_idx + int(0.1 * sample_rate), len(audio))
        
        if start_idx < len(audio):
            # 生成鼓点音效（低频 + 高频）
            drum_t = np.linspace(0, 0.1, end_idx - start_idx)
            kick = np.sin(2 * np.pi * 60 * drum_t) * np.exp(-drum_t * 20)  # 低频踢鼓
            snare = np.random.normal(0, 0.1, len(drum_t)) * np.exp(-drum_t * 30)  # 高频军鼓
            
            audio[start_idx:end_idx] += kick + snare * 0.3
    
    return audio, sample_rate

def main():
    print("🎵 音频节拍检测示例")
    
    # 创建测试音频
    print("📝 生成测试音频...")
    test_audio, sr = create_test_audio()
    
    # 保存测试音频
    import soundfile as sf
    test_file = "test_beat_audio.wav"
    sf.write(test_file, test_audio, sr)
    print(f"✅ 测试音频已保存: {test_file}")
    
    # 创建检测器
    detector = AudioBeatDetector(sample_rate=sr)
    
    # 加载音频
    if detector.load_audio(test_file):
        # 检测节拍
        tempo, beat_times = detector.detect_tempo_and_beats()
        
        print(f"\\n🎯 检测结果:")
        print(f"   BPM: {tempo:.1f}")
        print(f"   节拍点数量: {len(beat_times)}")
        print(f"   前5个节拍时间: {beat_times[:5]}")
        
        # 导出结果
        detector.export_beat_points("example_beats.json")
        
        # 生成可视化
        detector.visualize_beats("example_visualization.png", show_plot=False)
        
        print("\\n✅ 示例完成！检查生成的文件:")
        print("   - example_beats.json: 节拍数据")
        print("   - example_visualization.png: 可视化图表")

if __name__ == "__main__":
    main()
'''
    
    with open("example_usage.py", "w", encoding="utf-8") as f:
        f.write(example_script)
    
    print("✅ 示例脚本已创建: example_usage.py")


def main():
    """主安装流程"""
    print("🎵 音频节奏卡点提取工具 - 环境设置")
    print("=" * 50)
    
    # 安装系统依赖
    install_system_dependencies()
    
    # 安装Python依赖
    if not install_dependencies():
        print("❌ 安装失败，请检查错误信息")
        return False
    
    # 验证安装
    if not verify_installation():
        print("❌ 验证失败，请检查安装")
        return False
    
    # 创建示例脚本
    create_example_script()
    
    print("\n🎉 安装完成！")
    print("\n📖 使用方法:")
    print("1. 命令行使用:")
    print("   python audio_beat_detection.py your_audio.mp3 -v")
    print("\n2. 运行示例:")
    print("   python example_usage.py")
    print("\n3. Python代码中使用:")
    print("   from audio_beat_detection import AudioBeatDetector")
    
    return True


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
简化版音频节拍检测演示
使用纯Python实现基础的节拍检测算法
不依赖外部库，适用于演示和学习
"""

import math
import json
import wave
import struct
from typing import List, Tuple, Optional


class SimpleBeatDetector:
    """简化版节拍检测器"""
    
    def __init__(self):
        self.audio_data = []
        self.sample_rate = 44100
        self.duration = 0
        
    def load_wav_file(self, file_path: str) -> bool:
        """
        加载WAV音频文件
        
        Args:
            file_path: WAV文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # 获取音频参数
                frames = wav_file.getnframes()
                self.sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                print(f"音频信息:")
                print(f"  采样率: {self.sample_rate} Hz")
                print(f"  声道数: {channels}")
                print(f"  位深度: {sample_width * 8} bit")
                print(f"  帧数: {frames}")
                
                # 读取音频数据
                raw_audio = wav_file.readframes(frames)
                
                # 解析音频数据
                if sample_width == 1:
                    # 8-bit
                    audio_data = struct.unpack(f'{frames * channels}B', raw_audio)
                    audio_data = [(x - 128) / 128.0 for x in audio_data]
                elif sample_width == 2:
                    # 16-bit
                    audio_data = struct.unpack(f'{frames * channels}h', raw_audio)
                    audio_data = [x / 32768.0 for x in audio_data]
                else:
                    print(f"不支持的位深度: {sample_width * 8} bit")
                    return False
                
                # 如果是立体声，转换为单声道
                if channels == 2:
                    mono_data = []
                    for i in range(0, len(audio_data), 2):
                        mono_data.append((audio_data[i] + audio_data[i + 1]) / 2.0)
                    self.audio_data = mono_data
                else:
                    self.audio_data = audio_data
                
                self.duration = len(self.audio_data) / self.sample_rate
                print(f"  时长: {self.duration:.2f} 秒")
                print(f"✅ 音频加载成功")
                return True
                
        except Exception as e:
            print(f"❌ 音频加载失败: {e}")
            return False
    
    def generate_test_audio(self, duration: float = 10.0, bpm: float = 120.0) -> bool:
        """
        生成测试音频（模拟鼓点）
        
        Args:
            duration: 音频时长（秒）
            bpm: 每分钟节拍数
            
        Returns:
            bool: 生成是否成功
        """
        print(f"生成测试音频: {duration}秒, {bpm} BPM")
        
        self.sample_rate = 44100
        self.duration = duration
        total_samples = int(self.sample_rate * duration)
        
        # 计算节拍间隔
        beat_interval = 60.0 / bpm  # 秒
        beat_samples = int(beat_interval * self.sample_rate)
        
        # 生成音频数据
        self.audio_data = [0.0] * total_samples
        
        # 添加节拍点（鼓点效果）
        beat_count = 0
        for i in range(0, total_samples, beat_samples):
            # 生成鼓点音效
            kick_duration = int(0.1 * self.sample_rate)  # 100ms鼓点
            
            for j in range(kick_duration):
                if i + j < total_samples:
                    t = j / self.sample_rate
                    # 低频踢鼓 + 衰减
                    kick = math.sin(2 * math.pi * 60 * t) * math.exp(-t * 20)
                    # 高频军鼓噪声
                    snare = (hash(j) % 1000 - 500) / 5000.0 * math.exp(-t * 30)
                    
                    self.audio_data[i + j] = kick + snare * 0.3
            
            beat_count += 1
        
        print(f"✅ 生成了 {beat_count} 个节拍点")
        return True
    
    def save_wav_file(self, file_path: str) -> bool:
        """
        保存音频为WAV文件
        
        Args:
            file_path: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)  # 单声道
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                
                # 转换为16-bit整数
                audio_int = [int(x * 32767) for x in self.audio_data]
                audio_bytes = struct.pack(f'{len(audio_int)}h', *audio_int)
                
                wav_file.writeframes(audio_bytes)
            
            print(f"✅ 音频已保存: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 音频保存失败: {e}")
            return False
    
    def calculate_energy(self, window_size: int = 1024) -> List[float]:
        """
        计算音频能量分布
        
        Args:
            window_size: 窗口大小
            
        Returns:
            List[float]: 能量数组
        """
        if not self.audio_data:
            return []
        
        energy = []
        hop_size = window_size // 2
        
        for i in range(0, len(self.audio_data) - window_size, hop_size):
            window = self.audio_data[i:i + window_size]
            window_energy = sum(x * x for x in window) / window_size
            energy.append(window_energy)
        
        return energy
    
    def detect_beats_simple(self, threshold_factor: float = 1.5) -> List[float]:
        """
        简单的节拍检测算法
        
        Args:
            threshold_factor: 阈值因子
            
        Returns:
            List[float]: 节拍时间点列表
        """
        if not self.audio_data:
            return []
        
        print("🔍 开始节拍检测...")
        
        # 计算能量
        window_size = int(self.sample_rate * 0.05)  # 50ms窗口
        energy = self.calculate_energy(window_size)
        
        if not energy:
            return []
        
        # 计算能量变化
        energy_diff = []
        for i in range(1, len(energy)):
            diff = energy[i] - energy[i-1]
            energy_diff.append(max(0, diff))  # 只考虑能量增加
        
        # 计算动态阈值
        avg_energy_diff = sum(energy_diff) / len(energy_diff)
        threshold = avg_energy_diff * threshold_factor
        
        # 检测峰值
        beats = []
        hop_size = window_size // 2
        min_beat_interval = int(self.sample_rate * 0.3)  # 最小节拍间隔300ms
        
        last_beat_sample = -min_beat_interval
        
        for i, diff in enumerate(energy_diff):
            if diff > threshold:
                sample_pos = i * hop_size
                
                # 避免过于接近的节拍点
                if sample_pos - last_beat_sample >= min_beat_interval:
                    beat_time = sample_pos / self.sample_rate
                    beats.append(beat_time)
                    last_beat_sample = sample_pos
        
        print(f"✅ 检测到 {len(beats)} 个节拍点")
        return beats
    
    def estimate_tempo(self, beats: List[float]) -> float:
        """
        估算BPM
        
        Args:
            beats: 节拍时间点列表
            
        Returns:
            float: 估算的BPM
        """
        if len(beats) < 2:
            return 0.0
        
        # 计算节拍间隔
        intervals = []
        for i in range(1, len(beats)):
            interval = beats[i] - beats[i-1]
            intervals.append(interval)
        
        # 计算平均间隔
        avg_interval = sum(intervals) / len(intervals)
        
        # 转换为BPM
        bpm = 60.0 / avg_interval if avg_interval > 0 else 0.0
        
        return bpm
    
    def analyze_rhythm_stability(self, beats: List[float]) -> float:
        """
        分析节奏稳定性
        
        Args:
            beats: 节拍时间点列表
            
        Returns:
            float: 稳定性分数 (0-1)
        """
        if len(beats) < 3:
            return 0.0
        
        # 计算节拍间隔
        intervals = []
        for i in range(1, len(beats)):
            interval = beats[i] - beats[i-1]
            intervals.append(interval)
        
        # 计算间隔的标准差
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        std_dev = math.sqrt(variance)
        
        # 稳定性分数（标准差越小越稳定）
        stability = 1.0 / (1.0 + std_dev * 10)
        
        return stability
    
    def export_analysis(self, output_file: str, beats: List[float]) -> bool:
        """
        导出分析结果
        
        Args:
            output_file: 输出文件路径
            beats: 节拍时间点列表
            
        Returns:
            bool: 导出是否成功
        """
        try:
            bpm = self.estimate_tempo(beats)
            stability = self.analyze_rhythm_stability(beats)
            
            analysis_data = {
                "metadata": {
                    "audio_duration": self.duration,
                    "sample_rate": self.sample_rate,
                    "total_beats": len(beats),
                    "estimated_bpm": round(bpm, 1),
                    "rhythm_stability": round(stability, 3),
                    "analysis_method": "simple_energy_based"
                },
                "beat_points": [round(beat, 3) for beat in beats],
                "statistics": {
                    "avg_beat_interval": round(sum(beats[i+1] - beats[i] for i in range(len(beats)-1)) / max(1, len(beats)-1), 3),
                    "first_beat": round(beats[0], 3) if beats else 0,
                    "last_beat": round(beats[-1], 3) if beats else 0
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 分析结果已导出: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    def print_analysis_summary(self, beats: List[float]):
        """打印分析摘要"""
        if not beats:
            print("❌ 没有检测到节拍点")
            return
        
        bpm = self.estimate_tempo(beats)
        stability = self.analyze_rhythm_stability(beats)
        
        print("\n📊 分析结果摘要:")
        print("=" * 40)
        print(f"🎵 音频时长: {self.duration:.2f} 秒")
        print(f"🥁 节拍点数量: {len(beats)}")
        print(f"⚡ 估算BPM: {bpm:.1f}")
        print(f"📈 节奏稳定性: {stability:.3f} (0-1)")
        print(f"⏱️  平均节拍间隔: {60/bpm:.3f} 秒" if bpm > 0 else "⏱️  平均节拍间隔: N/A")
        
        print(f"\n🎯 前10个节拍时间点:")
        for i, beat in enumerate(beats[:10]):
            minutes = int(beat // 60)
            seconds = beat % 60
            print(f"  {i+1:2d}: {beat:6.3f}s ({minutes}:{seconds:06.3f})")
        
        if len(beats) > 10:
            print(f"  ... 还有 {len(beats) - 10} 个节拍点")


def main():
    """主函数 - 演示程序"""
    print("🎵 简化版音频节拍检测演示")
    print("=" * 50)
    
    detector = SimpleBeatDetector()
    
    # 生成测试音频
    print("\n📝 生成测试音频...")
    detector.generate_test_audio(duration=15.0, bpm=128.0)
    
    # 保存测试音频
    test_file = "test_beat_demo.wav"
    detector.save_wav_file(test_file)
    
    # 检测节拍
    print("\n🔍 检测节拍...")
    beats = detector.detect_beats_simple(threshold_factor=1.2)
    
    # 显示分析结果
    detector.print_analysis_summary(beats)
    
    # 导出结果
    print("\n💾 导出分析结果...")
    detector.export_analysis("beat_analysis_demo.json", beats)
    
    print("\n🎉 演示完成！")
    print("\n📁 生成的文件:")
    print(f"  🎵 {test_file} - 测试音频文件")
    print(f"  📊 beat_analysis_demo.json - 分析结果")
    
    print("\n💡 使用提示:")
    print("  1. 可以用音频播放器播放生成的WAV文件")
    print("  2. 查看JSON文件了解检测到的节拍点")
    print("  3. 修改代码中的BPM参数生成不同节奏的测试音频")


if __name__ == "__main__":
    main()

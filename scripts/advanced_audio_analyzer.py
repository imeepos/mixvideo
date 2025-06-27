#!/usr/bin/env python3
"""
高级音频分析工具
提供更多音频特征分析功能，用于智能视频剪辑
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from audio_beat_detection import AudioBeatDetector


@dataclass
class AudioSegment:
    """音频片段数据类"""
    start_time: float
    end_time: float
    energy_level: float
    spectral_centroid: float
    tempo_stability: float
    segment_type: str  # 'intro', 'verse', 'chorus', 'bridge', 'outro'


class AdvancedAudioAnalyzer(AudioBeatDetector):
    """高级音频分析器，继承基础节拍检测功能"""
    
    def __init__(self, sample_rate: int = 22050):
        super().__init__(sample_rate)
        self.segments = []
        self.energy_profile = None
        self.spectral_features = {}
        
    def analyze_energy_profile(self, frame_length: int = 2048, hop_length: int = 512) -> np.ndarray:
        """
        分析音频能量分布
        
        Args:
            frame_length: 帧长度
            hop_length: 跳跃长度
            
        Returns:
            np.ndarray: 能量分布数组
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        # 计算短时能量
        energy = []
        for i in range(0, len(self.audio_data) - frame_length, hop_length):
            frame = self.audio_data[i:i + frame_length]
            frame_energy = np.sum(frame ** 2)
            energy.append(frame_energy)
        
        self.energy_profile = np.array(energy)
        return self.energy_profile
    
    def detect_music_structure(self) -> List[AudioSegment]:
        """
        检测音乐结构（段落分析）
        
        Returns:
            List[AudioSegment]: 音频段落列表
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        print("正在分析音乐结构...")
        
        # 计算色度特征（用于和声分析）
        chroma = librosa.feature.chroma_stft(
            y=self.audio_data, 
            sr=self.sample_rate,
            hop_length=512
        )
        
        # 计算MFCC特征
        mfcc = librosa.feature.mfcc(
            y=self.audio_data, 
            sr=self.sample_rate,
            n_mfcc=13,
            hop_length=512
        )
        
        # 计算频谱质心
        spectral_centroids = librosa.feature.spectral_centroid(
            y=self.audio_data, 
            sr=self.sample_rate,
            hop_length=512
        )[0]
        
        # 分析能量分布
        if self.energy_profile is None:
            self.analyze_energy_profile()
        
        # 使用滑动窗口分析段落
        window_size = int(self.sample_rate * 4)  # 4秒窗口
        hop_size = int(self.sample_rate * 2)     # 2秒跳跃
        
        segments = []
        audio_duration = len(self.audio_data) / self.sample_rate
        
        for start_sample in range(0, len(self.audio_data) - window_size, hop_size):
            end_sample = min(start_sample + window_size, len(self.audio_data))
            
            start_time = start_sample / self.sample_rate
            end_time = end_sample / self.sample_rate
            
            # 计算该段落的特征
            segment_audio = self.audio_data[start_sample:end_sample]
            
            # 能量水平
            energy_level = np.mean(segment_audio ** 2)
            
            # 频谱质心（音色亮度）
            start_frame = start_sample // 512
            end_frame = end_sample // 512
            segment_centroid = np.mean(spectral_centroids[start_frame:end_frame])
            
            # 节拍稳定性（如果有节拍数据）
            tempo_stability = 1.0
            if self.beat_times is not None:
                segment_beats = self.beat_times[
                    (self.beat_times >= start_time) & (self.beat_times <= end_time)
                ]
                if len(segment_beats) > 2:
                    beat_intervals = np.diff(segment_beats)
                    tempo_stability = 1.0 / (1.0 + np.std(beat_intervals))
            
            # 简单的段落类型分类
            segment_type = self._classify_segment(
                start_time, end_time, audio_duration, 
                energy_level, segment_centroid
            )
            
            segment = AudioSegment(
                start_time=start_time,
                end_time=end_time,
                energy_level=energy_level,
                spectral_centroid=segment_centroid,
                tempo_stability=tempo_stability,
                segment_type=segment_type
            )
            
            segments.append(segment)
        
        self.segments = segments
        print(f"检测到 {len(segments)} 个音频段落")
        return segments
    
    def _classify_segment(self, start_time: float, end_time: float, 
                         total_duration: float, energy: float, 
                         centroid: float) -> str:
        """
        简单的段落分类逻辑
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            total_duration: 总时长
            energy: 能量水平
            centroid: 频谱质心
            
        Returns:
            str: 段落类型
        """
        # 基于位置的初步分类
        position_ratio = start_time / total_duration
        
        if position_ratio < 0.1:
            return 'intro'
        elif position_ratio > 0.9:
            return 'outro'
        elif energy > np.percentile([s.energy_level for s in self.segments if s.energy_level], 75):
            return 'chorus'  # 高能量段落通常是副歌
        elif centroid < np.percentile([s.spectral_centroid for s in self.segments if s.spectral_centroid], 25):
            return 'bridge'  # 低频谱质心可能是过渡段
        else:
            return 'verse'   # 默认为主歌
    
    def find_highlight_moments(self, top_n: int = 5) -> List[Tuple[float, float, str]]:
        """
        找到音频中的高光时刻（适合做卡点的位置）
        
        Args:
            top_n: 返回前N个高光时刻
            
        Returns:
            List[Tuple[float, float, str]]: (时间, 强度, 描述)
        """
        if not self.segments:
            self.detect_music_structure()
        
        highlights = []
        
        # 基于能量变化找高光时刻
        for i, segment in enumerate(self.segments):
            if i == 0:
                continue
                
            prev_segment = self.segments[i-1]
            energy_change = segment.energy_level - prev_segment.energy_level
            
            # 能量突然增加的时刻
            if energy_change > 0:
                intensity = energy_change * segment.tempo_stability
                description = f"能量爆发 ({segment.segment_type})"
                highlights.append((segment.start_time, intensity, description))
        
        # 基于节拍找强拍位置
        if self.beat_times is not None:
            for i, beat_time in enumerate(self.beat_times):
                if i % 4 == 0:  # 每4拍的强拍
                    # 找到对应的段落
                    segment = next((s for s in self.segments 
                                  if s.start_time <= beat_time <= s.end_time), None)
                    if segment:
                        intensity = segment.energy_level * 0.8
                        description = f"强拍位置 ({segment.segment_type})"
                        highlights.append((beat_time, intensity, description))
        
        # 按强度排序并返回前N个
        highlights.sort(key=lambda x: x[1], reverse=True)
        return highlights[:top_n]
    
    def generate_cut_points(self, target_duration: float = 60.0, 
                           style: str = 'dynamic') -> List[Tuple[float, float]]:
        """
        生成智能剪辑点建议
        
        Args:
            target_duration: 目标时长（秒）
            style: 剪辑风格 ('dynamic', 'smooth', 'rhythmic')
            
        Returns:
            List[Tuple[float, float]]: (开始时间, 结束时间) 列表
        """
        if not self.segments:
            self.detect_music_structure()
        
        cut_points = []
        total_audio_duration = len(self.audio_data) / self.sample_rate
        
        if style == 'dynamic':
            # 动态剪辑：选择高能量段落
            high_energy_segments = sorted(
                self.segments, 
                key=lambda s: s.energy_level, 
                reverse=True
            )
            
            current_duration = 0
            for segment in high_energy_segments:
                if current_duration >= target_duration:
                    break
                
                segment_duration = segment.end_time - segment.start_time
                if current_duration + segment_duration <= target_duration:
                    cut_points.append((segment.start_time, segment.end_time))
                    current_duration += segment_duration
                else:
                    # 部分使用该段落
                    remaining_time = target_duration - current_duration
                    cut_points.append((segment.start_time, segment.start_time + remaining_time))
                    break
        
        elif style == 'smooth':
            # 平滑剪辑：按时间顺序选择
            segment_duration = target_duration / len(self.segments)
            for segment in self.segments:
                if len(cut_points) * segment_duration >= target_duration:
                    break
                
                end_time = min(segment.start_time + segment_duration, segment.end_time)
                cut_points.append((segment.start_time, end_time))
        
        elif style == 'rhythmic':
            # 节奏剪辑：基于节拍点
            if self.beat_times is not None:
                beats_per_cut = max(1, len(self.beat_times) // int(target_duration / 4))
                
                for i in range(0, len(self.beat_times), beats_per_cut):
                    if i + beats_per_cut < len(self.beat_times):
                        start_time = self.beat_times[i]
                        end_time = self.beat_times[i + beats_per_cut]
                        
                        if end_time - start_time <= target_duration:
                            cut_points.append((start_time, end_time))
                        else:
                            break
        
        return cut_points
    
    def export_analysis_report(self, output_path: str) -> bool:
        """
        导出完整的分析报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        try:
            # 获取基础分析数据
            rhythm_analysis = self.analyze_rhythm_patterns()
            
            # 获取高光时刻
            highlights = self.find_highlight_moments()
            
            # 生成剪辑建议
            dynamic_cuts = self.generate_cut_points(60.0, 'dynamic')
            smooth_cuts = self.generate_cut_points(60.0, 'smooth')
            rhythmic_cuts = self.generate_cut_points(60.0, 'rhythmic')
            
            report = {
                'metadata': {
                    'audio_duration': rhythm_analysis['audio_duration'],
                    'tempo_bpm': rhythm_analysis['tempo_bpm'],
                    'total_segments': len(self.segments),
                    'analysis_timestamp': str(np.datetime64('now'))
                },
                'rhythm_analysis': rhythm_analysis,
                'music_structure': [
                    {
                        'start_time': seg.start_time,
                        'end_time': seg.end_time,
                        'duration': seg.end_time - seg.start_time,
                        'energy_level': seg.energy_level,
                        'spectral_centroid': seg.spectral_centroid,
                        'tempo_stability': seg.tempo_stability,
                        'segment_type': seg.segment_type
                    }
                    for seg in self.segments
                ],
                'highlight_moments': [
                    {
                        'time': time,
                        'intensity': intensity,
                        'description': desc
                    }
                    for time, intensity, desc in highlights
                ],
                'cut_suggestions': {
                    'dynamic_style': [
                        {'start': start, 'end': end, 'duration': end - start}
                        for start, end in dynamic_cuts
                    ],
                    'smooth_style': [
                        {'start': start, 'end': end, 'duration': end - start}
                        for start, end in smooth_cuts
                    ],
                    'rhythmic_style': [
                        {'start': start, 'end': end, 'duration': end - start}
                        for start, end in rhythmic_cuts
                    ]
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"完整分析报告已导出到: {output_path}")
            return True
            
        except Exception as e:
            print(f"导出分析报告失败: {e}")
            return False
    
    def visualize_complete_analysis(self, output_path: Optional[str] = None):
        """
        生成完整的分析可视化图表
        
        Args:
            output_path: 图片保存路径
        """
        if self.audio_data is None:
            print("请先加载音频文件")
            return
        
        # 确保有所有分析数据
        if not self.segments:
            self.detect_music_structure()
        
        if self.energy_profile is None:
            self.analyze_energy_profile()
        
        # 创建时间轴
        time_axis = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
        energy_time_axis = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.energy_profile))
        
        # 创建图表
        fig, axes = plt.subplots(4, 1, figsize=(16, 12))
        
        # 子图1: 音频波形与段落标记
        axes[0].plot(time_axis, self.audio_data, alpha=0.6, color='blue')
        for segment in self.segments:
            color = {'intro': 'green', 'verse': 'blue', 'chorus': 'red', 
                    'bridge': 'orange', 'outro': 'purple'}.get(segment.segment_type, 'gray')
            axes[0].axvspan(segment.start_time, segment.end_time, alpha=0.3, color=color)
        axes[0].set_title('音频波形与音乐结构分析', fontsize=14)
        axes[0].set_ylabel('振幅')
        axes[0].grid(True, alpha=0.3)
        
        # 子图2: 能量分布
        axes[1].plot(energy_time_axis, self.energy_profile, color='red', linewidth=2)
        axes[1].set_title('音频能量分布', fontsize=14)
        axes[1].set_ylabel('能量')
        axes[1].grid(True, alpha=0.3)
        
        # 子图3: 节拍点与高光时刻
        if self.beat_times is not None:
            axes[2].vlines(self.beat_times, 0, 1, colors='blue', alpha=0.6, label='节拍点')
        
        highlights = self.find_highlight_moments(10)
        highlight_times = [h[0] for h in highlights]
        highlight_intensities = [h[1] for h in highlights]
        axes[2].scatter(highlight_times, [0.8] * len(highlight_times), 
                       c='red', s=100, alpha=0.8, label='高光时刻')
        axes[2].set_title('节拍点与高光时刻', fontsize=14)
        axes[2].set_ylabel('标记')
        axes[2].set_ylim(0, 1)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # 子图4: 段落类型分布
        segment_types = [seg.segment_type for seg in self.segments]
        segment_starts = [seg.start_time for seg in self.segments]
        segment_energies = [seg.energy_level for seg in self.segments]
        
        colors = {'intro': 'green', 'verse': 'blue', 'chorus': 'red', 
                 'bridge': 'orange', 'outro': 'purple'}
        for i, (start, seg_type, energy) in enumerate(zip(segment_starts, segment_types, segment_energies)):
            axes[3].bar(start, energy, width=2.0, alpha=0.7, 
                       color=colors.get(seg_type, 'gray'), label=seg_type if i == 0 else "")
        
        axes[3].set_title('段落类型与能量分布', fontsize=14)
        axes[3].set_ylabel('能量水平')
        axes[3].set_xlabel('时间 (秒)')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"完整分析图表已保存到: {output_path}")
        
        plt.show()


def main():
    """示例使用"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python advanced_audio_analyzer.py <音频文件>")
        return
    
    audio_file = sys.argv[1]
    
    # 创建分析器
    analyzer = AdvancedAudioAnalyzer()
    
    # 加载音频
    if not analyzer.load_audio(audio_file):
        return
    
    # 执行完整分析
    print("执行完整音频分析...")
    analyzer.detect_tempo_and_beats()
    analyzer.detect_music_structure()
    
    # 导出分析报告
    report_file = f"{Path(audio_file).stem}_analysis_report.json"
    analyzer.export_analysis_report(report_file)
    
    # 生成可视化
    viz_file = f"{Path(audio_file).stem}_complete_analysis.png"
    analyzer.visualize_complete_analysis(viz_file)
    
    print(f"\n✅ 分析完成！")
    print(f"📊 分析报告: {report_file}")
    print(f"📈 可视化图表: {viz_file}")


if __name__ == "__main__":
    main()

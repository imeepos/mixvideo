#!/usr/bin/env python3
"""
音频节奏卡点提取工具
使用 librosa 库进行音频分析，提取节拍点和节奏特征
适用于视频混剪中的自动卡点功能
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class AudioBeatDetector:
    """音频节拍检测器"""
    
    def __init__(self, sample_rate: int = 22050):
        """
        初始化检测器
        
        Args:
            sample_rate: 音频采样率，默认22050Hz
        """
        self.sample_rate = sample_rate
        self.audio_data = None
        self.tempo = None
        self.beat_frames = None
        self.beat_times = None
        
    def load_audio(self, audio_path: str) -> bool:
        """
        加载音频文件
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            print(f"正在加载音频文件: {audio_path}")
            self.audio_data, _ = librosa.load(
                audio_path, 
                sr=self.sample_rate,
                mono=True  # 转换为单声道
            )
            print(f"音频加载成功，时长: {len(self.audio_data) / self.sample_rate:.2f}秒")
            return True
        except Exception as e:
            print(f"音频加载失败: {e}")
            return False
    
    def detect_tempo_and_beats(self) -> Tuple[float, np.ndarray]:
        """
        检测音频的节拍和速度
        
        Returns:
            Tuple[float, np.ndarray]: (BPM, 节拍时间点数组)
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        print("正在分析音频节拍...")
        
        # 使用 librosa 的节拍跟踪算法
        tempo, beat_frames = librosa.beat.beat_track(
            y=self.audio_data,
            sr=self.sample_rate,
            hop_length=512,
            start_bpm=120.0,  # 初始BPM估计
            tightness=100     # 节拍跟踪的紧密度
        )
        
        # 将帧转换为时间
        beat_times = librosa.frames_to_time(
            beat_frames, 
            sr=self.sample_rate,
            hop_length=512
        )
        
        self.tempo = tempo
        self.beat_frames = beat_frames
        self.beat_times = beat_times
        
        print(f"检测到的BPM: {tempo:.1f}")
        print(f"检测到的节拍点数量: {len(beat_times)}")
        
        return tempo, beat_times
    
    def detect_onset_strength(self) -> np.ndarray:
        """
        检测音频的起始强度（用于更精确的卡点检测）
        
        Returns:
            np.ndarray: 起始强度数组
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        # 计算起始强度
        onset_strength = librosa.onset.onset_strength(
            y=self.audio_data,
            sr=self.sample_rate,
            hop_length=512
        )
        
        return onset_strength
    
    def detect_precise_beats(self, threshold: float = 0.3) -> List[float]:
        """
        检测精确的节拍点（结合节拍跟踪和起始检测）
        
        Args:
            threshold: 起始检测阈值
            
        Returns:
            List[float]: 精确的节拍时间点列表
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        print("正在进行精确节拍检测...")
        
        # 获取起始强度
        onset_strength = self.detect_onset_strength()
        
        # 检测起始点
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_strength,
            sr=self.sample_rate,
            hop_length=512,
            threshold=threshold,
            pre_max=3,
            post_max=3,
            pre_avg=3,
            post_avg=5,
            delta=0.2,
            wait=10
        )
        
        # 转换为时间
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=self.sample_rate,
            hop_length=512
        )
        
        # 如果已经检测过节拍，结合两种方法
        if self.beat_times is not None:
            # 合并节拍点和起始点
            all_beats = np.concatenate([self.beat_times, onset_times])
            all_beats = np.unique(np.sort(all_beats))
            
            # 过滤过于接近的点（小于0.1秒间隔）
            filtered_beats = []
            last_beat = -1
            for beat in all_beats:
                if beat - last_beat > 0.1:
                    filtered_beats.append(beat)
                    last_beat = beat
            
            return filtered_beats
        else:
            return onset_times.tolist()
    
    def analyze_rhythm_patterns(self) -> Dict:
        """
        分析音频的节奏模式
        
        Returns:
            Dict: 节奏分析结果
        """
        if self.audio_data is None:
            raise ValueError("请先加载音频文件")
        
        print("正在分析节奏模式...")
        
        # 计算节拍间隔
        if self.beat_times is not None and len(self.beat_times) > 1:
            beat_intervals = np.diff(self.beat_times)
            avg_interval = np.mean(beat_intervals)
            interval_std = np.std(beat_intervals)
        else:
            avg_interval = 0
            interval_std = 0
        
        # 计算频谱质心（音色特征）
        spectral_centroids = librosa.feature.spectral_centroid(
            y=self.audio_data, 
            sr=self.sample_rate
        )[0]
        
        # 计算零交叉率（节奏复杂度指标）
        zcr = librosa.feature.zero_crossing_rate(self.audio_data)[0]
        
        # 计算MFCC特征（音色特征）
        mfccs = librosa.feature.mfcc(
            y=self.audio_data, 
            sr=self.sample_rate, 
            n_mfcc=13
        )
        
        analysis_result = {
            'tempo_bpm': float(self.tempo) if self.tempo else 0,
            'beat_count': len(self.beat_times) if self.beat_times is not None else 0,
            'avg_beat_interval': float(avg_interval),
            'beat_interval_stability': float(1 / (1 + interval_std)),  # 稳定性指标
            'avg_spectral_centroid': float(np.mean(spectral_centroids)),
            'avg_zero_crossing_rate': float(np.mean(zcr)),
            'mfcc_features': mfccs.mean(axis=1).tolist(),
            'audio_duration': float(len(self.audio_data) / self.sample_rate)
        }
        
        return analysis_result
    
    def export_beat_points(self, output_path: str, format: str = 'json') -> bool:
        """
        导出节拍点数据
        
        Args:
            output_path: 输出文件路径
            format: 输出格式 ('json', 'txt', 'csv')
            
        Returns:
            bool: 导出是否成功
        """
        if self.beat_times is None:
            print("请先检测节拍点")
            return False
        
        try:
            # 获取精确节拍点
            precise_beats = self.detect_precise_beats()
            
            # 获取节奏分析结果
            rhythm_analysis = self.analyze_rhythm_patterns()
            
            export_data = {
                'metadata': {
                    'tempo_bpm': rhythm_analysis['tempo_bpm'],
                    'total_beats': len(precise_beats),
                    'audio_duration': rhythm_analysis['audio_duration'],
                    'analysis_timestamp': str(np.datetime64('now'))
                },
                'beat_points': precise_beats,
                'rhythm_analysis': rhythm_analysis
            }
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"BPM: {rhythm_analysis['tempo_bpm']:.1f}\n")
                    f.write(f"节拍点数量: {len(precise_beats)}\n")
                    f.write(f"音频时长: {rhythm_analysis['audio_duration']:.2f}秒\n\n")
                    f.write("节拍时间点 (秒):\n")
                    for i, beat in enumerate(precise_beats):
                        f.write(f"{i+1:3d}: {beat:8.3f}\n")
            
            elif format.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['序号', '时间(秒)', '时间(分:秒)'])
                    for i, beat in enumerate(precise_beats):
                        minutes = int(beat // 60)
                        seconds = beat % 60
                        time_str = f"{minutes}:{seconds:06.3f}"
                        writer.writerow([i+1, f"{beat:.3f}", time_str])
            
            print(f"节拍点数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def visualize_beats(self, output_path: Optional[str] = None, show_plot: bool = True):
        """
        可视化节拍检测结果
        
        Args:
            output_path: 图片保存路径（可选）
            show_plot: 是否显示图片
        """
        if self.audio_data is None or self.beat_times is None:
            print("请先加载音频并检测节拍")
            return
        
        # 创建时间轴
        time_axis = np.linspace(0, len(self.audio_data) / self.sample_rate, len(self.audio_data))
        
        # 计算起始强度用于可视化
        onset_strength = self.detect_onset_strength()
        onset_time_axis = librosa.frames_to_time(
            np.arange(len(onset_strength)),
            sr=self.sample_rate,
            hop_length=512
        )
        
        # 创建图表
        plt.figure(figsize=(15, 10))
        
        # 子图1: 音频波形
        plt.subplot(3, 1, 1)
        plt.plot(time_axis, self.audio_data, alpha=0.6, color='blue')
        plt.vlines(self.beat_times, -1, 1, color='red', alpha=0.8, linestyle='--', linewidth=1)
        plt.title(f'音频波形与节拍点 (BPM: {self.tempo:.1f})', fontsize=14)
        plt.ylabel('振幅')
        plt.grid(True, alpha=0.3)
        
        # 子图2: 起始强度
        plt.subplot(3, 1, 2)
        plt.plot(onset_time_axis, onset_strength, color='green', linewidth=2)
        plt.vlines(self.beat_times, 0, max(onset_strength), color='red', alpha=0.8, linestyle='--', linewidth=1)
        plt.title('起始强度与节拍点', fontsize=14)
        plt.ylabel('强度')
        plt.grid(True, alpha=0.3)
        
        # 子图3: 节拍间隔分析
        plt.subplot(3, 1, 3)
        if len(self.beat_times) > 1:
            beat_intervals = np.diff(self.beat_times)
            plt.plot(self.beat_times[1:], beat_intervals, 'o-', color='purple', markersize=4)
            plt.axhline(y=np.mean(beat_intervals), color='orange', linestyle='-', 
                       label=f'平均间隔: {np.mean(beat_intervals):.3f}s')
            plt.title('节拍间隔分析', fontsize=14)
            plt.ylabel('间隔 (秒)')
            plt.xlabel('时间 (秒)')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"可视化图表已保存到: {output_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(description='音频节奏卡点提取工具')
    parser.add_argument('input_file', help='输入音频文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径前缀', default='beat_analysis')
    parser.add_argument('-f', '--format', choices=['json', 'txt', 'csv'], 
                       default='json', help='输出格式')
    parser.add_argument('-v', '--visualize', action='store_true', help='生成可视化图表')
    parser.add_argument('-s', '--sample-rate', type=int, default=22050, help='音频采样率')
    parser.add_argument('-t', '--threshold', type=float, default=0.3, help='起始检测阈值')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not Path(args.input_file).exists():
        print(f"错误: 文件不存在 - {args.input_file}")
        return
    
    # 创建检测器
    detector = AudioBeatDetector(sample_rate=args.sample_rate)
    
    # 加载音频
    if not detector.load_audio(args.input_file):
        return
    
    # 检测节拍
    try:
        tempo, beat_times = detector.detect_tempo_and_beats()
        print(f"\n节拍检测完成!")
        print(f"检测到的节拍数: {len(beat_times)}")
        print(f"平均BPM: {tempo:.1f}")
        
        # 导出结果
        output_file = f"{args.output}.{args.format}"
        if detector.export_beat_points(output_file, args.format):
            print(f"结果已保存到: {output_file}")
        
        # 生成可视化
        if args.visualize:
            viz_file = f"{args.output}_visualization.png"
            detector.visualize_beats(viz_file, show_plot=False)
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
音频节拍检测API服务器
为视频混剪应用提供音频分析接口
"""

import json
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import cgi

# 导入我们的音频检测模块
from simple_beat_demo import SimpleBeatDetector


class AudioAnalysisAPI(BaseHTTPRequestHandler):
    """音频分析API处理器"""
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_api_info()
        elif parsed_path.path == '/health':
            self.serve_health_check()
        elif parsed_path.path == '/demo':
            self.serve_demo_analysis()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/analyze':
            self.handle_audio_analysis()
        elif parsed_path.path == '/analyze-url':
            self.handle_url_analysis()
        else:
            self.send_error(404, "Not Found")
    
    def serve_api_info(self):
        """提供API信息"""
        api_info = {
            "name": "音频节拍检测API",
            "version": "1.0.0",
            "description": "为视频混剪提供音频节拍检测和分析服务",
            "endpoints": {
                "GET /": "API信息",
                "GET /health": "健康检查",
                "GET /demo": "演示分析",
                "POST /analyze": "上传音频文件进行分析",
                "POST /analyze-url": "通过URL分析音频"
            },
            "supported_formats": ["WAV", "MP3 (需要ffmpeg)", "其他音频格式 (需要ffmpeg)"],
            "example_usage": {
                "curl_upload": "curl -X POST -F 'audio=@music.wav' http://localhost:8080/analyze",
                "curl_url": "curl -X POST -H 'Content-Type: application/json' -d '{\"url\":\"http://example.com/music.mp3\"}' http://localhost:8080/analyze-url"
            }
        }
        
        self.send_json_response(api_info)
    
    def serve_health_check(self):
        """健康检查"""
        health_status = {
            "status": "healthy",
            "timestamp": str(uuid.uuid4()),
            "services": {
                "audio_detector": "available",
                "file_processing": "available"
            }
        }
        
        self.send_json_response(health_status)
    
    def serve_demo_analysis(self):
        """提供演示分析"""
        try:
            # 生成演示音频
            detector = SimpleBeatDetector()
            detector.generate_test_audio(duration=10.0, bpm=120.0)
            
            # 检测节拍
            beats = detector.detect_beats_simple()
            
            # 生成分析结果
            bpm = detector.estimate_tempo(beats)
            stability = detector.analyze_rhythm_stability(beats)
            
            demo_result = {
                "demo": True,
                "metadata": {
                    "audio_duration": detector.duration,
                    "total_beats": len(beats),
                    "estimated_bpm": round(bpm, 1),
                    "rhythm_stability": round(stability, 3)
                },
                "beat_points": [round(beat, 3) for beat in beats[:20]],  # 只返回前20个
                "analysis_summary": {
                    "avg_beat_interval": round(60/bpm, 3) if bpm > 0 else 0,
                    "beat_density": round(len(beats) / detector.duration, 2)
                }
            }
            
            self.send_json_response(demo_result)
            
        except Exception as e:
            self.send_error_response(500, f"演示生成失败: {str(e)}")
    
    def handle_audio_analysis(self):
        """处理音频文件上传和分析"""
        try:
            # 解析multipart/form-data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error_response(400, "需要multipart/form-data格式")
                return
            
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解析上传的文件
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                if 'audio' not in form:
                    self.send_error_response(400, "缺少音频文件")
                    return
                
                audio_field = form['audio']
                if not audio_field.filename:
                    self.send_error_response(400, "无效的音频文件")
                    return
                
                # 保存上传的文件
                file_ext = Path(audio_field.filename).suffix.lower()
                temp_file = Path(temp_dir) / f"upload{file_ext}"
                
                with open(temp_file, 'wb') as f:
                    f.write(audio_field.file.read())
                
                # 分析音频
                result = self.analyze_audio_file(str(temp_file))
                self.send_json_response(result)
                
        except Exception as e:
            self.send_error_response(500, f"分析失败: {str(e)}")
    
    def handle_url_analysis(self):
        """处理URL音频分析"""
        try:
            # 读取JSON数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'url' not in data:
                self.send_error_response(400, "缺少URL参数")
                return
            
            url = data['url']
            
            # 下载音频文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = Path(temp_dir) / "downloaded_audio"
                
                # 使用curl下载（如果可用）
                try:
                    subprocess.run([
                        'curl', '-L', '-o', str(temp_file), url
                    ], check=True, capture_output=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    self.send_error_response(500, "无法下载音频文件")
                    return
                
                # 分析音频
                result = self.analyze_audio_file(str(temp_file))
                result['source_url'] = url
                self.send_json_response(result)
                
        except json.JSONDecodeError:
            self.send_error_response(400, "无效的JSON数据")
        except Exception as e:
            self.send_error_response(500, f"分析失败: {str(e)}")
    
    def analyze_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析音频文件
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            Dict: 分析结果
        """
        detector = SimpleBeatDetector()
        
        # 尝试直接加载WAV文件
        if file_path.lower().endswith('.wav'):
            if not detector.load_wav_file(file_path):
                raise Exception("WAV文件加载失败")
        else:
            # 对于其他格式，尝试转换为WAV
            wav_file = file_path + '.wav'
            try:
                # 使用ffmpeg转换（如果可用）
                subprocess.run([
                    'ffmpeg', '-i', file_path, '-ar', '44100', '-ac', '1', wav_file
                ], check=True, capture_output=True)
                
                if not detector.load_wav_file(wav_file):
                    raise Exception("转换后的WAV文件加载失败")
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise Exception("音频格式转换失败，请使用WAV格式或安装ffmpeg")
        
        # 检测节拍
        beats = detector.detect_beats_simple()
        
        # 计算统计信息
        bpm = detector.estimate_tempo(beats)
        stability = detector.analyze_rhythm_stability(beats)
        
        # 生成高光时刻建议
        highlights = []
        if len(beats) >= 4:
            # 选择能量较高的节拍点作为高光时刻
            energy = detector.calculate_energy()
            if energy:
                # 简单的高光时刻检测
                for i, beat in enumerate(beats):
                    if i % 4 == 0:  # 每4拍选一个
                        highlights.append({
                            "time": round(beat, 3),
                            "type": "strong_beat",
                            "description": f"强拍位置 #{i//4 + 1}"
                        })
        
        # 生成剪辑建议
        cut_suggestions = []
        if len(beats) >= 8:
            # 按8拍为一组生成剪辑建议
            for i in range(0, len(beats) - 8, 8):
                start_time = beats[i]
                end_time = beats[i + 8]
                cut_suggestions.append({
                    "start": round(start_time, 3),
                    "end": round(end_time, 3),
                    "duration": round(end_time - start_time, 3),
                    "type": "8_beat_segment"
                })
        
        return {
            "success": True,
            "metadata": {
                "audio_duration": detector.duration,
                "sample_rate": detector.sample_rate,
                "total_beats": len(beats),
                "estimated_bpm": round(bpm, 1),
                "rhythm_stability": round(stability, 3),
                "analysis_method": "simple_energy_based"
            },
            "beat_points": [round(beat, 3) for beat in beats],
            "highlights": highlights[:10],  # 最多返回10个高光时刻
            "cut_suggestions": cut_suggestions[:5],  # 最多返回5个剪辑建议
            "statistics": {
                "avg_beat_interval": round(60/bpm, 3) if bpm > 0 else 0,
                "beat_density": round(len(beats) / detector.duration, 2),
                "first_beat": round(beats[0], 3) if beats else 0,
                "last_beat": round(beats[-1], 3) if beats else 0
            }
        }
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """发送错误响应"""
        error_data = {
            "success": False,
            "error": {
                "code": status_code,
                "message": message
            }
        }
        self.send_json_response(error_data, status_code)
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.date_time_string()}] {format % args}")


def main():
    """启动API服务器"""
    host = '0.0.0.0'
    port = 8080
    
    print(f"🎵 音频节拍检测API服务器")
    print(f"🌐 启动服务器: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/")
    print(f"🧪 演示接口: http://{host}:{port}/demo")
    print(f"❤️  健康检查: http://{host}:{port}/health")
    print("\n📝 使用示例:")
    print(f"   curl http://{host}:{port}/demo")
    print(f"   curl -X POST -F 'audio=@music.wav' http://{host}:{port}/analyze")
    print("\n按 Ctrl+C 停止服务器")
    
    try:
        server = HTTPServer((host, port), AudioAnalysisAPI)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")


if __name__ == "__main__":
    main()

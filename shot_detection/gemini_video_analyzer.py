#!/usr/bin/env python3
"""
Gemini视频分析器
使用Google Gemini API分析视频内容
"""

import os
import json
import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional
import requests


class GeminiVideoAnalyzer:
    """Gemini视频分析器"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        初始化Gemini视频分析器
        
        Args:
            api_key: Google AI Studio API Key
            model_name: 使用的模型名称
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def analyze_video(self, video_path: str, prompt: str, progress_callback=None) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            video_path: 视频文件路径
            prompt: 分析提示词
            progress_callback: 进度回调函数
            
        Returns:
            分析结果字典
        """
        try:
            if progress_callback:
                progress_callback(10, "准备上传视频...")
            
            # 上传视频文件
            file_uri = self._upload_video_file(video_path, progress_callback)
            
            if progress_callback:
                progress_callback(60, "发送分析请求...")
            
            # 发送分析请求
            result = self._generate_content(file_uri, prompt, progress_callback)
            
            if progress_callback:
                progress_callback(90, "处理分析结果...")
            
            # 解析结果
            parsed_result = self._parse_analysis_result(result, video_path)
            
            if progress_callback:
                progress_callback(100, "分析完成")
            
            return parsed_result
            
        except Exception as e:
            raise Exception(f"视频分析失败: {str(e)}")
    
    def _upload_video_file(self, video_path: str, progress_callback=None) -> str:
        """
        上传视频文件到Gemini
        
        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            文件URI
        """
        try:
            # 检查文件大小（Gemini有文件大小限制）
            file_size = os.path.getsize(video_path)
            max_size = 20 * 1024 * 1024  # 20MB限制
            
            if file_size > max_size:
                raise Exception(f"视频文件过大 ({file_size / 1024 / 1024:.1f}MB)，请使用小于20MB的文件")
            
            if progress_callback:
                progress_callback(20, "读取视频文件...")
            
            # 读取视频文件
            with open(video_path, 'rb') as f:
                video_data = f.read()
            
            if progress_callback:
                progress_callback(30, "上传到Gemini...")
            
            # 上传文件
            upload_url = f"{self.base_url}/files?key={self.api_key}"
            
            # 准备上传数据
            files = {
                'metadata': (None, json.dumps({
                    "file": {
                        "display_name": Path(video_path).name
                    }
                }), 'application/json'),
                'data': (Path(video_path).name, video_data, 'video/mp4')
            }
            
            response = requests.post(upload_url, files=files, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"文件上传失败: {response.status_code} - {response.text}")
            
            upload_result = response.json()
            file_uri = upload_result.get('file', {}).get('uri')
            
            if not file_uri:
                raise Exception("上传成功但未获取到文件URI")
            
            if progress_callback:
                progress_callback(50, "等待文件处理...")
            
            # 等待文件处理完成
            self._wait_for_file_processing(file_uri)
            
            return file_uri
            
        except Exception as e:
            raise Exception(f"视频上传失败: {str(e)}")
    
    def _wait_for_file_processing(self, file_uri: str, max_wait_time: int = 300):
        """
        等待文件处理完成
        
        Args:
            file_uri: 文件URI
            max_wait_time: 最大等待时间（秒）
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # 检查文件状态
                file_id = file_uri.split('/')[-1]
                status_url = f"{self.base_url}/files/{file_id}?key={self.api_key}"
                
                response = requests.get(status_url, timeout=30)
                
                if response.status_code == 200:
                    file_info = response.json()
                    state = file_info.get('state', 'UNKNOWN')
                    
                    if state == 'ACTIVE':
                        return  # 文件处理完成
                    elif state == 'FAILED':
                        raise Exception("文件处理失败")
                    
                # 等待一段时间后重试
                time.sleep(5)
                
            except Exception as e:
                if "timeout" not in str(e).lower():
                    raise e
                # 超时错误，继续等待
                time.sleep(5)
        
        raise Exception("文件处理超时")
    
    def _generate_content(self, file_uri: str, prompt: str, progress_callback=None) -> Dict[str, Any]:
        """
        生成内容分析
        
        Args:
            file_uri: 视频文件URI
            prompt: 分析提示词
            progress_callback: 进度回调函数
            
        Returns:
            API响应结果
        """
        try:
            generate_url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            
            # 准备请求数据
            request_data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "file_data": {
                                    "mime_type": "video/mp4",
                                    "file_uri": file_uri
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 8192
                }
            }
            
            if progress_callback:
                progress_callback(70, "等待AI分析...")
            
            # 发送请求
            response = requests.post(
                generate_url,
                headers={"Content-Type": "application/json"},
                json=request_data,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
            result = response.json()
            
            if 'candidates' not in result or not result['candidates']:
                raise Exception("API返回结果为空")
            
            return result
            
        except Exception as e:
            raise Exception(f"内容生成失败: {str(e)}")
    
    def _parse_analysis_result(self, api_result: Dict[str, Any], video_path: str) -> Dict[str, Any]:
        """
        解析分析结果
        
        Args:
            api_result: API返回结果
            video_path: 视频文件路径
            
        Returns:
            格式化的分析结果
        """
        try:
            # 提取文本内容
            candidates = api_result.get('candidates', [])
            if not candidates:
                raise Exception("无有效的分析结果")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            
            if not parts:
                raise Exception("分析结果为空")
            
            analysis_text = parts[0].get('text', '')
            
            if not analysis_text:
                raise Exception("未获取到分析文本")
            
            # 尝试解析JSON格式的结果
            try:
                # 如果结果是JSON格式
                if analysis_text.strip().startswith('{'):
                    analysis_data = json.loads(analysis_text)
                else:
                    # 如果是文本格式，创建基本结构
                    analysis_data = {
                        "content_analysis": {
                            "summary": analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text,
                            "full_text": analysis_text
                        }
                    }
            except json.JSONDecodeError:
                # JSON解析失败，使用文本格式
                analysis_data = {
                    "content_analysis": {
                        "summary": analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text,
                        "full_text": analysis_text
                    }
                }
            
            # 添加基本信息
            result = {
                "video_info": {
                    "file_name": Path(video_path).name,
                    "file_path": str(video_path),
                    "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model_used": self.model_name
                },
                "analysis_result": analysis_data,
                "raw_response": api_result
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"结果解析失败: {str(e)}")


def test_gemini_analyzer():
    """测试Gemini分析器"""
    print("🧪 Gemini视频分析器测试")
    
    # 这里需要真实的API Key进行测试
    api_key = "your_api_key_here"
    
    if api_key == "your_api_key_here":
        print("⚠️  请设置真实的API Key进行测试")
        return
    
    analyzer = GeminiVideoAnalyzer(api_key)
    
    # 测试视频路径
    test_video = "test_video.mp4"
    
    if not os.path.exists(test_video):
        print(f"⚠️  测试视频文件不存在: {test_video}")
        return
    
    # 测试提示词
    prompt = "请分析这个视频的内容，包括场景、物体、情感等方面。"
    
    try:
        def progress_callback(progress, description):
            print(f"进度: {progress}% - {description}")
        
        result = analyzer.analyze_video(test_video, prompt, progress_callback)
        
        print("✅ 分析完成！")
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_gemini_analyzer()

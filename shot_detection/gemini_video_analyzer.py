#!/usr/bin/env python3
"""
Gemini视频分析器
使用Google Gemini API分析视频内容，参考 @mixvideo/gemini 包的实现模式
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import requests
import logging
from dataclasses import dataclass, asdict


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeminiConfig:
    """Gemini配置类"""
    # 认证配置
    cloudflare_project_id: str = ""
    cloudflare_gateway_id: str = ""
    google_project_id: str = ""
    regions: List[str] = None
    access_token: str = ""

    # API配置
    model_name: str = "gemini-2.5-flash"
    base_url: str = "https://bowongai-dev--bowong-ai-video-gemini-fastapi-webapp.modal.run"
    bearer_token: str = "bowong7777"
    timeout: int = 120

    # 缓存配置
    enable_cache: bool = True
    cache_dir: str = ".cache/gemini_analysis"
    cache_expiry: int = 7 * 24 * 3600  # 7天

    # 重试配置
    max_retries: int = 3
    retry_delay: int = 5

    def __post_init__(self):
        if self.regions is None:
            self.regions = ["us-central1", "us-east1", "europe-west1"]


@dataclass
class AnalysisProgress:
    """分析进度"""
    step: str
    progress: int  # 0-100
    description: str = ""
    current_file: str = ""
    stage: str = "upload"  # upload, analysis, complete


@dataclass
class CacheEntry:
    """缓存条目"""
    video_path: str
    file_uri: str
    prompt: str
    result: Dict[str, Any]
    timestamp: float
    checksum: str
    model_name: str


class GeminiVideoAnalyzer:
    """Gemini视频分析器 - 参考 @mixvideo/gemini 实现"""

    def __init__(self, config: Optional[GeminiConfig] = None):
        """
        初始化Gemini视频分析器

        Args:
            config: Gemini配置对象
        """
        self.config = config or GeminiConfig()
        self._access_token = None
        self._token_expires_at = None

        # 确保缓存目录存在
        if self.config.enable_cache:
            os.makedirs(self.config.cache_dir, exist_ok=True)

    async def get_access_token(self) -> str:
        """
        获取Google访问令牌，参考 useGeminiAccessToken 实现
        """
        # 检查缓存的令牌是否仍然有效
        if (self._access_token and self._token_expires_at and
            time.time() < self._token_expires_at - 300):  # 提前5分钟刷新
            return self._access_token

        try:
            headers = {
                "Authorization": f"Bearer {self.config.bearer_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(
                f"{self.config.base_url}/google/access-token",
                headers=headers,
                timeout=self.config.timeout
            )

            if response.status_code != 200:
                raise Exception(f"获取访问令牌失败: {response.status_code} - {response.text}")

            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data.get("expires_in", 3600)

            logger.info("✅ 成功获取Google访问令牌")
            return self._access_token

        except Exception as e:
            logger.error(f"❌ 获取访问令牌失败: {e}")
            raise Exception(f"获取访问令牌失败: {str(e)}")

    def _create_gemini_client(self, access_token: str) -> Dict[str, Any]:
        """
        创建Gemini客户端配置，参考 GoogleGenaiClient 实现
        """
        import random

        # 随机选择区域
        region = random.choice(self.config.regions)

        gateway_url = (
            f"https://gateway.ai.cloudflare.com/v1/"
            f"{self.config.cloudflare_project_id}/"
            f"{self.config.cloudflare_gateway_id}/"
            f"google-vertex-ai/v1/projects/"
            f"{self.config.google_project_id}/"
            f"locations/{region}/publishers/google/models"
        )

        return {
            "gateway_url": gateway_url,
            "access_token": access_token,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        }

    def _calculate_file_checksum(self, file_path: str) -> str:
        """计算文件校验和"""
        import hashlib

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _generate_cache_key(self, video_path: str, prompt: str, model_name: str) -> str:
        """生成缓存键"""
        import hashlib

        key_data = f"{video_path}:{prompt}:{model_name}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _check_analysis_cache(self, video_path: str, prompt: str) -> Optional[Dict[str, Any]]:
        """检查分析缓存"""
        if not self.config.enable_cache:
            return None

        try:
            cache_key = self._generate_cache_key(video_path, prompt, self.config.model_name)
            cache_file = os.path.join(self.config.cache_dir, f"{cache_key}.json")

            if not os.path.exists(cache_file):
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry_data = json.load(f)
                cache_entry = CacheEntry(**cache_entry_data)

            # 检查缓存是否过期
            if time.time() - cache_entry.timestamp > self.config.cache_expiry:
                os.unlink(cache_file)
                logger.info(f"⏰ 缓存已过期: {Path(video_path).name}")
                return None

            # 检查文件是否发生变化
            current_checksum = self._calculate_file_checksum(video_path)
            if current_checksum != cache_entry.checksum:
                os.unlink(cache_file)
                logger.info(f"🔄 文件已变更: {Path(video_path).name}")
                return None

            logger.info(f"🎯 使用缓存的分析结果: {Path(video_path).name}")
            return cache_entry.result

        except Exception as e:
            logger.warning(f"检查分析缓存失败: {e}")
            return None

    def _save_analysis_cache(self, video_path: str, file_uri: str, prompt: str, result: Dict[str, Any]) -> None:
        """保存分析结果到缓存"""
        if not self.config.enable_cache:
            return

        try:
            cache_key = self._generate_cache_key(video_path, prompt, self.config.model_name)
            cache_file = os.path.join(self.config.cache_dir, f"{cache_key}.json")

            checksum = self._calculate_file_checksum(video_path)
            cache_entry = CacheEntry(
                video_path=video_path,
                file_uri=file_uri,
                prompt=prompt,
                result=result,
                timestamp=time.time(),
                checksum=checksum,
                model_name=self.config.model_name
            )

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(cache_entry), f, ensure_ascii=False, indent=2)

            logger.info(f"💾 分析结果已缓存: {Path(video_path).name}")

        except Exception as e:
            logger.warning(f"保存分析缓存失败: {e}")

    def analyze_video(self, video_path: str, prompt: str, progress_callback: Optional[Callable[[AnalysisProgress], None]] = None) -> Dict[str, Any]:
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
            progress = AnalysisProgress(
                step="开始分析",
                progress=0,
                current_file=Path(video_path).name,
                stage="upload"
            )
            if progress_callback:
                progress_callback(progress)

            # 检查缓存
            progress.step = "检查缓存"
            progress.progress = 5
            if progress_callback:
                progress_callback(progress)

            cached_result = self._check_analysis_cache(video_path, prompt)
            if cached_result:
                progress.step = "使用缓存结果"
                progress.progress = 100
                progress.stage = "complete"
                if progress_callback:
                    progress_callback(progress)
                return cached_result

            # 上传视频文件
            progress.step = "上传视频文件"
            progress.progress = 10
            if progress_callback:
                progress_callback(progress)

            file_uri = self._upload_video_file(video_path, progress_callback)

            # 发送分析请求
            progress.step = "发送分析请求"
            progress.progress = 60
            progress.stage = "analysis"
            if progress_callback:
                progress_callback(progress)

            result = self._generate_content(file_uri, prompt, progress_callback)

            # 解析结果
            progress.step = "处理分析结果"
            progress.progress = 90
            if progress_callback:
                progress_callback(progress)

            parsed_result = self._parse_analysis_result(result, video_path)

            # 保存到缓存
            self._save_analysis_cache(video_path, file_uri, prompt, parsed_result)

            progress.step = "分析完成"
            progress.progress = 100
            progress.stage = "complete"
            if progress_callback:
                progress_callback(progress)

            return parsed_result

        except Exception as e:
            logger.error(f"❌ 视频分析失败: {e}")
            raise Exception(f"视频分析失败: {str(e)}")

    def _upload_video_file(self, video_path: str, progress_callback: Optional[Callable[[AnalysisProgress], None]] = None) -> str:
        """
        上传视频文件到Gemini，参考 uploadFileToGemini 实现

        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数

        Returns:
            文件URI
        """
        try:
            # 检查文件大小
            file_size = os.path.getsize(video_path)
            max_size = 100 * 1024 * 1024  # 100MB限制

            if file_size > max_size:
                raise Exception(f"视频文件过大 ({file_size / 1024 / 1024:.1f}MB)，请使用小于100MB的文件")

            # 获取访问令牌
            import asyncio
            access_token = asyncio.run(self.get_access_token())

            progress = AnalysisProgress(
                step="准备上传数据",
                progress=20,
                current_file=Path(video_path).name,
                stage="upload"
            )
            if progress_callback:
                progress_callback(progress)

            # 准备FormData
            with open(video_path, 'rb') as f:
                video_data = f.read()

            # 使用新的上传API
            files = {
                'file': (Path(video_path).name, video_data, 'video/mp4')
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "x-google-api-key": access_token,
            }

            progress.step = "上传到Vertex AI"
            progress.progress = 30
            if progress_callback:
                progress_callback(progress)

            # 上传到Vertex AI
            upload_url = f"{self.config.base_url}/google/vertex-ai/upload"
            params = {
                "bucket": "dy-media-storage",
                "prefix": "video-analysis"
            }

            response = requests.post(
                upload_url,
                files=files,
                headers=headers,
                params=params,
                timeout=self.config.timeout
            )

            if response.status_code != 200:
                raise Exception(f"文件上传失败: {response.status_code} - {response.text}")

            upload_result = response.json()
            file_uri = upload_result.get('urn') or upload_result.get('uri')

            if not file_uri:
                raise Exception("上传成功但未获取到文件URI")

            progress.step = "上传完成"
            progress.progress = 50
            if progress_callback:
                progress_callback(progress)

            logger.info(f"✅ 视频上传成功: {Path(video_path).name} -> {file_uri}")
            return file_uri

        except Exception as e:
            logger.error(f"❌ 视频上传失败: {e}")
            raise Exception(f"视频上传失败: {str(e)}")

    def _generate_content(self, file_uri: str, prompt: str, progress_callback: Optional[Callable[[AnalysisProgress], None]] = None) -> Dict[str, Any]:
        """
        生成内容分析，参考 GoogleGenaiClient.generateContent 实现

        Args:
            file_uri: 视频文件URI
            prompt: 分析提示词
            progress_callback: 进度回调函数

        Returns:
            API响应结果
        """
        try:
            # 获取访问令牌
            import asyncio
            access_token = asyncio.run(self.get_access_token())

            # 创建客户端配置
            client_config = self._create_gemini_client(access_token)

            # 格式化GCS URI
            formatted_uri = self._format_gcs_uri(file_uri)

            # 准备请求数据，参考 TypeScript 实现
            request_data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "fileData": {
                                    "mimeType": "video/mp4",
                                    "fileUri": formatted_uri
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

            progress = AnalysisProgress(
                step="等待AI分析",
                progress=70,
                current_file="",
                stage="analysis"
            )
            if progress_callback:
                progress_callback(progress)

            # 发送请求到Cloudflare Gateway
            generate_url = f"{client_config['gateway_url']}/{self.config.model_name}:generateContent"

            logger.info(f"📤 发送 Gemini API 请求: {formatted_uri}")

            # 重试机制
            last_exception = None
            for attempt in range(self.config.max_retries):
                try:
                    response = requests.post(
                        generate_url,
                        headers=client_config["headers"],
                        json=request_data,
                        timeout=self.config.timeout
                    )

                    if response.status_code == 200:
                        result = response.json()

                        if 'candidates' not in result or not result['candidates']:
                            raise Exception("API返回结果为空")

                        logger.info("✅ 成功获取Gemini分析结果")
                        return result
                    else:
                        error_msg = f"API请求失败: {response.status_code} - {response.text}"
                        logger.warning(f"⚠️ 尝试 {attempt + 1}/{self.config.max_retries}: {error_msg}")

                        if attempt == self.config.max_retries - 1:
                            raise Exception(error_msg)

                        time.sleep(self.config.retry_delay)

                except requests.exceptions.Timeout as e:
                    last_exception = e
                    logger.warning(f"⚠️ 请求超时，尝试 {attempt + 1}/{self.config.max_retries}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"⚠️ 请求失败，尝试 {attempt + 1}/{self.config.max_retries}: {e}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)

            raise Exception(f"内容生成失败，已重试{self.config.max_retries}次: {last_exception}")

        except Exception as e:
            logger.error(f"❌ 内容生成失败: {e}")
            raise Exception(f"内容生成失败: {str(e)}")

    def _format_gcs_uri(self, file_uri: str) -> str:
        """格式化GCS URI"""
        if file_uri.startswith('gs://'):
            return file_uri
        elif file_uri.startswith('https://storage.googleapis.com/'):
            # 转换为gs://格式
            path = file_uri.replace('https://storage.googleapis.com/', '')
            return f"gs://{path}"
        else:
            # 假设已经是正确格式
            return file_uri

    def _parse_analysis_result(self, api_result: Dict[str, Any], video_path: str) -> Dict[str, Any]:
        """
        解析分析结果，参考 video-analyzer 的解析模式

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

            logger.info(f"✅ 成功获取响应文本，长度: {len(analysis_text)}")

            # 尝试解析JSON格式的结果
            analysis_data = None
            try:
                # 清理文本，移除可能的markdown标记
                cleaned_text = analysis_text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                if cleaned_text.startswith('{') or cleaned_text.startswith('['):
                    analysis_data = json.loads(cleaned_text)
                    logger.info("✅ 成功解析JSON格式的分析结果")
                else:
                    raise json.JSONDecodeError("Not JSON format", "", 0)

            except json.JSONDecodeError:
                # JSON解析失败，使用文本格式
                logger.info("📝 使用文本格式的分析结果")
                analysis_data = {
                    "content_analysis": {
                        "summary": analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text,
                        "full_text": analysis_text
                    }
                }

            # 构建标准化结果格式
            result = {
                "video_info": {
                    "file_name": Path(video_path).name,
                    "file_path": str(video_path),
                    "file_size": os.path.getsize(video_path),
                    "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model_used": self.config.model_name,
                    "config": {
                        "cache_enabled": self.config.enable_cache,
                        "regions": self.config.regions
                    }
                },
                "analysis_result": analysis_data,
                "metadata": {
                    "response_length": len(analysis_text),
                    "candidates_count": len(candidates),
                    "success": True
                },
                "raw_response": api_result
            }

            return result

        except Exception as e:
            logger.error(f"❌ 结果解析失败: {e}")
            raise Exception(f"结果解析失败: {str(e)}")

    def clean_expired_cache(self) -> Dict[str, int]:
        """清理过期缓存"""
        if not self.config.enable_cache:
            return {"removed": 0, "total": 0}

        try:
            cache_dir = Path(self.config.cache_dir)
            if not cache_dir.exists():
                return {"removed": 0, "total": 0}

            removed_count = 0
            total_count = 0
            current_time = time.time()

            for cache_file in cache_dir.glob("*.json"):
                total_count += 1
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)

                    if current_time - cache_data.get('timestamp', 0) > self.config.cache_expiry:
                        cache_file.unlink()
                        removed_count += 1

                except Exception:
                    # 损坏的缓存文件，删除
                    cache_file.unlink()
                    removed_count += 1

            logger.info(f"🧹 缓存清理完成: 删除 {removed_count}/{total_count} 个文件")
            return {"removed": removed_count, "total": total_count}

        except Exception as e:
            logger.warning(f"缓存清理失败: {e}")
            return {"removed": 0, "total": 0}

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.config.enable_cache:
            return {"enabled": False}

        try:
            cache_dir = Path(self.config.cache_dir)
            if not cache_dir.exists():
                return {"enabled": True, "total_files": 0, "total_size": 0}

            total_files = 0
            total_size = 0
            oldest_timestamp = float('inf')
            newest_timestamp = 0

            for cache_file in cache_dir.glob("*.json"):
                total_files += 1
                total_size += cache_file.stat().st_size

                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    timestamp = cache_data.get('timestamp', 0)
                    oldest_timestamp = min(oldest_timestamp, timestamp)
                    newest_timestamp = max(newest_timestamp, timestamp)
                except Exception:
                    pass

            return {
                "enabled": True,
                "total_files": total_files,
                "total_size": total_size,
                "cache_dir": str(cache_dir),
                "oldest_entry": None if oldest_timestamp == float('inf') else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(oldest_timestamp)),
                "newest_entry": None if newest_timestamp == 0 else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(newest_timestamp))
            }

        except Exception as e:
            logger.warning(f"获取缓存统计失败: {e}")
            return {"enabled": True, "error": str(e)}


# 便利函数
def create_gemini_analyzer(
    cloudflare_project_id: str = "",
    cloudflare_gateway_id: str = "",
    google_project_id: str = "",
    regions: Optional[List[str]] = None,
    model_name: str = "gemini-2.5-flash",
    enable_cache: bool = True,
    cache_dir: str = ".cache/gemini_analysis"
) -> GeminiVideoAnalyzer:
    """
    创建Gemini分析器的便利函数
    """
    config = GeminiConfig(
        cloudflare_project_id=cloudflare_project_id,
        cloudflare_gateway_id=cloudflare_gateway_id,
        google_project_id=google_project_id,
        regions=regions or ["us-central1", "us-east1", "europe-west1"],
        model_name=model_name,
        enable_cache=enable_cache,
        cache_dir=cache_dir
    )
    return GeminiVideoAnalyzer(config)


def test_gemini_analyzer():
    """测试Gemini分析器"""
    print("🧪 Gemini视频分析器测试")

    # 使用默认配置创建分析器
    analyzer = create_gemini_analyzer(
        cloudflare_project_id="your_cloudflare_project_id",
        cloudflare_gateway_id="your_cloudflare_gateway_id",
        google_project_id="your_google_project_id"
    )

    # 测试视频路径
    test_video = "test_video.mp4"

    if not os.path.exists(test_video):
        print(f"⚠️  测试视频文件不存在: {test_video}")
        print("请将测试视频文件放在当前目录下，或修改test_video变量")
        return

    # 测试提示词
    prompt = """请分析这个视频的内容，包括以下方面：
1. 场景描述
2. 主要物体和人物
3. 动作和活动
4. 视频质量评估
5. 情感色调

请以JSON格式返回结果。"""

    try:
        def progress_callback(progress: AnalysisProgress):
            print(f"进度: {progress.progress}% - {progress.step}")
            if progress.description:
                print(f"  描述: {progress.description}")

        # 显示缓存统计
        cache_stats = analyzer.get_cache_stats()
        print(f"📊 缓存统计: {cache_stats}")

        # 执行分析
        result = analyzer.analyze_video(test_video, prompt, progress_callback)

        print("✅ 分析完成！")
        print(f"📄 结果摘要:")
        print(f"  - 文件: {result['video_info']['file_name']}")
        print(f"  - 模型: {result['video_info']['model_used']}")
        print(f"  - 时间: {result['video_info']['analysis_time']}")
        print(f"  - 响应长度: {result['metadata']['response_length']}")

        # 保存结果到文件
        output_file = f"analysis_result_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存到: {output_file}")

        # 显示更新后的缓存统计
        cache_stats = analyzer.get_cache_stats()
        print(f"📊 更新后缓存统计: {cache_stats}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_cache_functionality():
    """测试缓存功能"""
    print("🧪 测试缓存功能")

    analyzer = create_gemini_analyzer()

    # 清理过期缓存
    clean_result = analyzer.clean_expired_cache()
    print(f"🧹 缓存清理结果: {clean_result}")

    # 显示缓存统计
    stats = analyzer.get_cache_stats()
    print(f"📊 缓存统计: {stats}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cache":
        test_cache_functionality()
    else:
        test_gemini_analyzer()

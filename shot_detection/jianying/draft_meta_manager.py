#!/usr/bin/env python3
"""
剪映项目元数据管理器

用于管理 draft_meta_info.json 文件的读取、写入和更新操作。
支持视频、音频、图片等素材的元数据管理。
"""

import json
import time
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import subprocess


@dataclass
class MaterialInfo:
    """素材信息数据类"""
    file_path: str
    name: str
    duration: int = 6000000  # 默认6秒（微秒）
    width: int = 1080
    height: int = 1920
    create_time: Optional[int] = None
    material_type: str = "video"  # video, audio, image, text


class DraftMetaManager:
    """剪映项目元数据管理器"""
    
    # 素材类型映射
    MATERIAL_TYPES = {
        "video": 0,
        "audio": 1, 
        "image": 2,
        "text": 3,
        "other": 6
    }
    
    def __init__(self, project_path: Union[str, Path]):
        """
        初始化元数据管理器
        
        Args:
            project_path: 剪映项目目录路径
        """
        self.project_path = Path(project_path)
        self.meta_file_path = self.project_path / "draft_meta_info.json"
        self.project_name = self.project_path.name
        self._meta_data = None
        
    def load_meta_data(self) -> Dict[str, Any]:
        """加载元数据文件"""
        if self.meta_file_path.exists():
            try:
                with open(self.meta_file_path, 'r', encoding='utf-8') as f:
                    self._meta_data = json.load(f)
                return self._meta_data
            except Exception as e:
                print(f"加载元数据文件失败: {e}")
                return self._create_default_meta_data()
        else:
            return self._create_default_meta_data()
    
    def _create_default_meta_data(self) -> Dict[str, Any]:
        """创建默认的元数据结构"""
        current_time = int(time.time())
        current_time_ms = int(time.time() * 1000000)
        
        self._meta_data = {
            "cloud_package_completed_time": "",
            "draft_cloud_capcut_purchase_info": "",
            "draft_cloud_last_action_download": False,
            "draft_cloud_materials": [],
            "draft_cloud_purchase_info": "",
            "draft_cloud_template_id": "",
            "draft_cloud_tutorial_info": "",
            "draft_cloud_videocut_purchase_info": "",
            "draft_cover": "draft_cover.jpg",
            "draft_deeplink_url": "",
            "draft_enterprise_info": {
                "draft_enterprise_extra": "",
                "draft_enterprise_id": "",
                "draft_enterprise_name": "",
                "enterprise_material": []
            },
            "draft_fold_path": str(self.project_path),
            "draft_id": str(uuid.uuid4()).upper(),
            "draft_is_ai_packaging_used": False,
            "draft_is_ai_shorts": False,
            "draft_is_ai_translate": False,
            "draft_is_article_video_draft": False,
            "draft_is_from_deeplink": "false",
            "draft_is_invisible": False,
            "draft_materials": [
                {"type": 0, "value": []},  # 视频
                {"type": 1, "value": []},  # 音频
                {"type": 2, "value": []},  # 图片
                {"type": 3, "value": []},  # 文本
                {"type": 6, "value": []}   # 其他
            ],
            "draft_materials_copied_info": [],
            "draft_name": self.project_name,
            "draft_new_version": "",
            "draft_removable_storage_device": "",
            "draft_root_path": str(self.project_path.parent),
            "draft_segment_extra_info": [],
            "draft_timeline_materials_size_": 0,
            "draft_type": "",
            "tm_draft_cloud_completed": "",
            "tm_draft_cloud_modified": 0,
            "tm_draft_create": current_time_ms,
            "tm_draft_modified": current_time_ms,
            "tm_draft_removed": 0,
            "tm_duration": 0
        }
        return self._meta_data
    
    def add_material(self, material: MaterialInfo) -> str:
        """
        添加素材到项目
        
        Args:
            material: 素材信息
            
        Returns:
            str: 生成的素材ID
        """
        if self._meta_data is None:
            self.load_meta_data()
        
        # 生成素材元数据
        material_id = str(uuid.uuid4())
        current_time = int(time.time())
        current_time_ms = int(time.time() * 1000000)
        
        # 获取文件信息
        file_path = Path(material.file_path)
        file_stats = file_path.stat() if file_path.exists() else None
        
        material_data = {
            "create_time": material.create_time or (int(file_stats.st_ctime) if file_stats else current_time),
            "duration": material.duration,
            "extra_info": material.name,
            "file_Path": str(file_path.resolve()),
            "height": material.height,
            "id": material_id,
            "import_time": current_time,
            "import_time_ms": current_time_ms,
            "item_source": 1,
            "md5": "",
            "metetype": material.material_type,
            "roughcut_time_range": {
                "duration": material.duration,
                "start": 0
            },
            "sub_time_range": {
                "duration": -1,
                "start": -1
            },
            "type": 0,
            "width": material.width
        }
        
        # 根据素材类型获取真实的文件信息
        if material.material_type == "video":
            video_info = self._get_video_info(file_path)
            if video_info:
                material_data.update(video_info)
        elif material.material_type == "audio":
            audio_info = self._get_audio_info(file_path)
            if audio_info:
                material_data.update(audio_info)
                # 音频文件设置默认尺寸
                material_data['width'] = 0
                material_data['height'] = 0
        elif material.material_type == "image":
            image_info = self._get_image_info(file_path)
            if image_info:
                material_data.update(image_info)
                # 图片设置默认时长（5秒）
                if 'duration' not in image_info:
                    material_data['duration'] = 5000000
                    material_data['roughcut_time_range'] = {
                        "duration": 5000000,
                        "start": 0
                    }
        
        # 添加到对应的素材类型组
        material_type_index = self.MATERIAL_TYPES.get(material.material_type, 0)
        for material_group in self._meta_data["draft_materials"]:
            if material_group["type"] == material_type_index:
                material_group["value"].append(material_data)
                break
        
        # 更新修改时间
        self._meta_data["tm_draft_modified"] = current_time_ms
        
        return material_id
    
    def _get_video_info(self, video_path: Path) -> Optional[Dict[str, Any]]:
        """使用ffprobe获取详细的视频信息"""
        try:
            # 使用ffprobe获取详细的视频信息
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                '-show_entries', 'stream=codec_type,width,height,duration,bit_rate,codec_name,pix_fmt,r_frame_rate:format=duration,bit_rate,size',
                str(video_path)
            ], capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                video_info = {}

                # 获取格式信息
                format_info = probe_data.get('format', {})

                # 获取视频流信息
                video_stream = None
                for stream in probe_data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break

                if video_stream:
                    # 基本尺寸信息
                    if 'width' in video_stream:
                        video_info['width'] = int(video_stream['width'])
                    if 'height' in video_stream:
                        video_info['height'] = int(video_stream['height'])

                    # 时长信息（优先使用format中的duration）
                    duration = None
                    if 'duration' in format_info:
                        duration = float(format_info['duration'])
                    elif 'duration' in video_stream:
                        duration = float(video_stream['duration'])

                    if duration:
                        # 转换为微秒
                        duration_us = int(duration * 1000000)
                        video_info['duration'] = duration_us
                        video_info['roughcut_time_range'] = {
                            "duration": duration_us,
                            "start": 0
                        }

                    # 编码信息
                    if 'codec_name' in video_stream:
                        video_info['codec'] = video_stream['codec_name']

                    # 帧率信息
                    if 'r_frame_rate' in video_stream:
                        frame_rate_str = video_stream['r_frame_rate']
                        if '/' in frame_rate_str:
                            num, den = frame_rate_str.split('/')
                            if int(den) != 0:
                                video_info['frame_rate'] = round(int(num) / int(den), 2)

                    # 像素格式
                    if 'pix_fmt' in video_stream:
                        video_info['pixel_format'] = video_stream['pix_fmt']

                    # 比特率
                    if 'bit_rate' in video_stream:
                        video_info['bit_rate'] = int(video_stream['bit_rate'])
                    elif 'bit_rate' in format_info:
                        video_info['bit_rate'] = int(format_info['bit_rate'])

                # 文件大小
                if 'size' in format_info:
                    video_info['file_size'] = int(format_info['size'])

                print(f"成功获取视频信息: {video_path.name}")
                print(f"  尺寸: {video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}")
                print(f"  时长: {video_info.get('duration', 0)/1000000:.2f}秒")
                print(f"  编码: {video_info.get('codec', 'N/A')}")
                print(f"  帧率: {video_info.get('frame_rate', 'N/A')} fps")
                print(f"  比特率: {video_info.get('bit_rate', 'N/A')} bps")
                print(f"  文件大小: {video_info.get('file_size', 'N/A')} bytes")

                return video_info

        except subprocess.TimeoutExpired:
            print(f"ffprobe超时: {video_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"ffprobe执行失败: {e}")
        except json.JSONDecodeError as e:
            print(f"ffprobe输出解析失败: {e}")
        except Exception as e:
            print(f"获取视频信息失败: {e}")

        return None

    def _get_audio_info(self, audio_path: Path) -> Optional[Dict[str, Any]]:
        """使用ffprobe获取音频文件信息"""
        try:
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                '-show_entries', 'stream=duration,bit_rate,codec_name,sample_rate,channels:format=duration,bit_rate,size',
                str(audio_path)
            ], capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                audio_info = {}

                # 获取格式信息
                format_info = probe_data.get('format', {})

                # 获取音频流信息
                audio_stream = None
                for stream in probe_data.get('streams', []):
                    if stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break

                if audio_stream:
                    # 时长信息
                    duration = None
                    if 'duration' in format_info:
                        duration = float(format_info['duration'])
                    elif 'duration' in audio_stream:
                        duration = float(audio_stream['duration'])

                    if duration:
                        # 转换为微秒
                        duration_us = int(duration * 1000000)
                        audio_info['duration'] = duration_us
                        audio_info['roughcut_time_range'] = {
                            "duration": duration_us,
                            "start": 0
                        }

                    # 编码信息
                    if 'codec_name' in audio_stream:
                        audio_info['codec'] = audio_stream['codec_name']

                    # 采样率
                    if 'sample_rate' in audio_stream:
                        audio_info['sample_rate'] = int(audio_stream['sample_rate'])

                    # 声道数
                    if 'channels' in audio_stream:
                        audio_info['channels'] = int(audio_stream['channels'])

                    # 比特率
                    if 'bit_rate' in audio_stream:
                        audio_info['bit_rate'] = int(audio_stream['bit_rate'])
                    elif 'bit_rate' in format_info:
                        audio_info['bit_rate'] = int(format_info['bit_rate'])

                # 文件大小
                if 'size' in format_info:
                    audio_info['file_size'] = int(format_info['size'])

                print(f"成功获取音频信息: {audio_path.name}")
                print(f"  时长: {audio_info.get('duration', 0)/1000000:.2f}秒")
                print(f"  编码: {audio_info.get('codec', 'N/A')}")
                print(f"  采样率: {audio_info.get('sample_rate', 'N/A')} Hz")
                print(f"  声道: {audio_info.get('channels', 'N/A')}")

                return audio_info

        except Exception as e:
            print(f"获取音频信息失败: {e}")

        return None

    def _get_image_info(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """使用ffprobe获取图片文件信息"""
        try:
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-show_entries', 'stream=width,height,pix_fmt,codec_name',
                str(image_path)
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                probe_data = json.loads(result.stdout)
                image_info = {}

                # 获取图片流信息
                for stream in probe_data.get('streams', []):
                    if stream.get('codec_type') == 'video':  # 图片也被识别为video流
                        if 'width' in stream:
                            image_info['width'] = int(stream['width'])
                        if 'height' in stream:
                            image_info['height'] = int(stream['height'])
                        if 'codec_name' in stream:
                            image_info['codec'] = stream['codec_name']
                        if 'pix_fmt' in stream:
                            image_info['pixel_format'] = stream['pix_fmt']
                        break

                print(f"成功获取图片信息: {image_path.name}")
                print(f"  尺寸: {image_info.get('width', 'N/A')}x{image_info.get('height', 'N/A')}")
                print(f"  格式: {image_info.get('codec', 'N/A')}")

                return image_info

        except Exception as e:
            print(f"获取图片信息失败: {e}")

        return None
    
    def remove_material(self, material_id: str) -> bool:
        """
        移除素材
        
        Args:
            material_id: 素材ID
            
        Returns:
            bool: 是否成功移除
        """
        if self._meta_data is None:
            self.load_meta_data()
        
        for material_group in self._meta_data["draft_materials"]:
            materials = material_group["value"]
            for i, material in enumerate(materials):
                if material.get("id") == material_id:
                    materials.pop(i)
                    self._meta_data["tm_draft_modified"] = int(time.time() * 1000000)
                    return True
        
        return False
    
    def get_materials_by_type(self, material_type: str) -> List[Dict[str, Any]]:
        """
        获取指定类型的素材列表
        
        Args:
            material_type: 素材类型 (video, audio, image, text, other)
            
        Returns:
            List[Dict]: 素材列表
        """
        if self._meta_data is None:
            self.load_meta_data()
        
        material_type_index = self.MATERIAL_TYPES.get(material_type, 0)
        
        for material_group in self._meta_data["draft_materials"]:
            if material_group["type"] == material_type_index:
                return material_group["value"]
        
        return []
    
    def update_material(self, material_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新素材信息
        
        Args:
            material_id: 素材ID
            updates: 要更新的字段
            
        Returns:
            bool: 是否成功更新
        """
        if self._meta_data is None:
            self.load_meta_data()
        
        for material_group in self._meta_data["draft_materials"]:
            for material in material_group["value"]:
                if material.get("id") == material_id:
                    material.update(updates)
                    self._meta_data["tm_draft_modified"] = int(time.time() * 1000000)
                    return True
        
        return False
    
    def save_meta_data(self) -> bool:
        """保存元数据到文件"""
        if self._meta_data is None:
            return False
        
        try:
            # 确保目录存在
            self.meta_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(self.meta_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._meta_data, f, ensure_ascii=False, indent=4)
            
            return True
            
        except Exception as e:
            print(f"保存元数据文件失败: {e}")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """获取项目基本信息"""
        if self._meta_data is None:
            self.load_meta_data()
        
        return {
            "project_id": self._meta_data.get("draft_id"),
            "project_name": self._meta_data.get("draft_name"),
            "project_path": self._meta_data.get("draft_fold_path"),
            "create_time": self._meta_data.get("tm_draft_create"),
            "modified_time": self._meta_data.get("tm_draft_modified"),
            "duration": self._meta_data.get("tm_duration")
        }
    
    def set_project_duration(self, duration_ms: int):
        """设置项目总时长"""
        if self._meta_data is None:
            self.load_meta_data()
        
        self._meta_data["tm_duration"] = duration_ms
        self._meta_data["tm_draft_modified"] = int(time.time() * 1000000)

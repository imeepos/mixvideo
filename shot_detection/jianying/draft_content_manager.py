#!/usr/bin/env python3
"""
剪映项目内容管理器

用于管理 draft_content.json 文件的读取、写入和更新操作。
支持时间轴、轨道、素材、特效等内容的管理。
"""

import json
import time
import uuid
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# 尝试导入yaml，如果失败则使用None
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False


@dataclass
class TrackInfo:
    """轨道信息数据类"""
    track_type: str  # "video", "audio", "text", "sticker"
    attribute: int = 0
    flag: int = 0
    id: str = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4()).upper()


@dataclass
class MaterialRef:
    """素材引用数据类"""
    material_id: str
    material_type: str  # "video", "audio", "image", "text"
    start_time: int = 0  # 微秒
    duration: int = 6000000  # 默认6秒
    track_render_index: int = 0


class DraftContentManager:
    """剪映项目内容管理器"""
    
    def __init__(self, project_path: Union[str, Path]):
        """
        初始化内容管理器

        Args:
            project_path: 剪映项目目录路径
        """
        self.project_path = Path(project_path)
        self.content_file_path = self.project_path / "draft_content.json"
        self.project_name = self.project_path.name
        self._content_data = None
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        # 如果yaml不可用，直接使用默认配置
        if not YAML_AVAILABLE:
            print("yaml模块不可用，使用默认配置")
            return self._get_default_config()

        # 查找配置文件，从当前目录向上查找
        current_dir = Path(__file__).parent
        config_file = None

        # 向上查找config.yaml文件
        for parent in [current_dir] + list(current_dir.parents):
            potential_config = parent / "config.yaml"
            if potential_config.exists():
                config_file = potential_config
                break

        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            print("未找到config.yaml文件，使用默认配置")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "jianying": {
                "device_info": {
                    "device_id": "0594836068dad896e25a104fc9dbabab",
                    "hard_disk_id": "92ff8fc0225cc7379b7488c983cc022b",
                    "mac_address": "32d6cbfd9256fd8884fac27c2658c25c,ec42e1bff9b87e6e58088ef68d13a818,f2ee8c3f35364c316ce08bf3c505b58b,003dc1a823f26cc7edc2f0bfac31c811"
                },
                "platform_info": {
                    "app_id": 3704,
                    "app_source": "lv",
                    "app_version": "5.9.0",
                    "os": "windows",
                    "os_version": "10.0.26100"
                },
                "project_defaults": {
                    "canvas_width": 1920,
                    "canvas_height": 1080,
                    "fps": 30.0,
                    "version": 360000,
                    "new_version": "110.0.0"
                }
            }
        }
        
    def load_content_data(self) -> Dict[str, Any]:
        """加载内容数据文件"""
        if self.content_file_path.exists():
            try:
                with open(self.content_file_path, 'r', encoding='utf-8') as f:
                    self._content_data = json.load(f)
                return self._content_data
            except Exception as e:
                print(f"加载内容数据文件失败: {e}")
                return self._create_default_content_data()
        else:
            return self._create_default_content_data()
    
    def _create_default_content_data(self) -> Dict[str, Any]:
        """创建默认的内容数据结构"""
        current_time = int(time.time())

        # 从配置文件获取设备和平台信息
        device_info = self._config.get("jianying", {}).get("device_info", {})
        platform_info = self._config.get("jianying", {}).get("platform_info", {})
        project_defaults = self._config.get("jianying", {}).get("project_defaults", {})

        self._content_data = {
            "canvas_config": {
                "height": project_defaults.get("canvas_height", 1080),
                "ratio": "original",
                "width": project_defaults.get("canvas_width", 1920)
            },
            "color_space": -1,
            "config": {
                "adjust_max_index": 1,
                "attachment_info": [],
                "combination_max_index": 1,
                "export_range": None,
                "extract_audio_last_index": 1,
                "lyrics_recognition_id": "",
                "lyrics_sync": True,
                "lyrics_taskinfo": [],
                "maintrack_adsorb": True,
                "material_save_mode": 0,
                "multi_language_current": "none",
                "multi_language_list": [],
                "multi_language_main": "none",
                "multi_language_mode": "none",
                "original_sound_last_index": 1,
                "record_audio_last_index": 1,
                "sticker_max_index": 1,
                "subtitle_keywords_config": None,
                "subtitle_recognition_id": "",
                "subtitle_sync": True,
                "subtitle_taskinfo": [],
                "system_font_list": [],
                "video_mute": False,
                "zoom_info_params": None
            },
            "cover": None,
            "create_time": current_time,
            "duration": 0,
            "extra_info": None,
            "fps": project_defaults.get("fps", 30.0),
            "free_render_index_mode_on": False,
            "group_container": None,
            "id": str(uuid.uuid4()).upper(),
            "keyframe_graph_list": [],
            "keyframes": {
                "adjusts": [],
                "audios": [],
                "effects": [],
                "filters": [],
                "handwrites": [],
                "stickers": [],
                "texts": [],
                "videos": []
            },
            "last_modified_platform": {
                "app_id": platform_info.get("app_id", 3704),
                "app_source": platform_info.get("app_source", "lv"),
                "app_version": platform_info.get("app_version", "5.9.0"),
                "device_id": device_info.get("device_id", "0594836068dad896e25a104fc9dbabab"),
                "hard_disk_id": device_info.get("hard_disk_id", "92ff8fc0225cc7379b7488c983cc022b"),
                "mac_address": device_info.get("mac_address", "32d6cbfd9256fd8884fac27c2658c25c,ec42e1bff9b87e6e58088ef68d13a818"),
                "os": platform_info.get("os", "windows"),
                "os_version": platform_info.get("os_version", "10.0.26100")
            },
            "materials": {
                "ai_translates": [],
                "audio_balances": [],
                "audio_effects": [],
                "audio_fades": [],
                "audio_track_indexes": [],
                "audios": [],
                "beats": [],
                "canvases": [],
                "chromas": [],
                "color_curves": [],
                "digital_humans": [],
                "drafts": [],
                "effects": [],
                "flowers": [],
                "green_screens": [],
                "handwrites": [],
                "hsl": [],
                "images": [],
                "log_color_wheels": [],
                "loudnesses": [],
                "manual_deformations": [],
                "masks": [],
                "material_animations": [],
                "material_colors": [],
                "multi_language_refs": [],
                "placeholders": [],
                "plugin_effects": [],
                "primary_color_wheels": [],
                "realtime_denoises": [],
                "shapes": [],
                "smart_crops": [],
                "smart_relights": [],
                "sound_channel_mappings": [],
                "speeds": [],
                "stickers": [],
                "tail_leaders": [],
                "text_templates": [],
                "texts": [],
                "time_marks": [],
                "transitions": [],
                "video_effects": [],
                "video_trackings": [],
                "videos": [],
                "vocal_beautifys": [],
                "vocal_separations": []
            },
            "mutable_config": None,
            "name": self.project_name,
            "new_version": project_defaults.get("new_version", "110.0.0"),
            "platform": {
                "app_id": platform_info.get("app_id", 3704),
                "app_source": platform_info.get("app_source", "lv"),
                "app_version": platform_info.get("app_version", "5.9.0"),
                "device_id": device_info.get("device_id", "0594836068dad896e25a104fc9dbabab"),
                "hard_disk_id": device_info.get("hard_disk_id", "92ff8fc0225cc7379b7488c983cc022b"),
                "mac_address": device_info.get("mac_address", "32d6cbfd9256fd8884fac27c2658c25c,ec42e1bff9b87e6e58088ef68d13a818"),
                "os": platform_info.get("os", "windows"),
                "os_version": platform_info.get("os_version", "10.0.26100")
            },
            "relationships": [],
            "render_index_track_mode_on": False,
            "retouch_cover": None,
            "source": "default",
            "static_cover_image_path": "",
            "time_marks": None,
            "tracks": [],
            "update_time": current_time,
            "version": project_defaults.get("version", 360000)
        }
        return self._content_data

    def load_from_template(self, template_path: Union[str, Path]) -> bool:
        """
        从指定的JSON模板文件加载内容数据

        Args:
            template_path: 模板文件路径

        Returns:
            bool: 加载是否成功
        """
        template_file = Path(template_path)

        if not template_file.exists():
            print(f"模板文件不存在: {template_file}")
            return False

        if not template_file.suffix.lower() == '.json':
            print(f"模板文件必须是JSON格式: {template_file}")
            return False

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            # 验证模板数据结构
            if not self._validate_template_structure(template_data):
                print("模板文件结构验证失败")
                return False

            # 深拷贝模板数据
            import copy
            self._content_data = copy.deepcopy(template_data)

            # 更新项目相关信息
            self._update_project_info_from_template()

            print(f"成功从模板加载: {template_file}")
            return True

        except json.JSONDecodeError as e:
            print(f"模板文件JSON格式错误: {e}")
            return False
        except Exception as e:
            print(f"加载模板文件失败: {e}")
            return False

    def _validate_template_structure(self, template_data: Dict[str, Any]) -> bool:
        """
        验证模板数据结构是否有效

        Args:
            template_data: 模板数据

        Returns:
            bool: 结构是否有效
        """
        required_fields = [
            "canvas_config", "config", "keyframes", "materials",
            "platform", "tracks", "version"
        ]

        for field in required_fields:
            if field not in template_data:
                print(f"模板缺少必需字段: {field}")
                return False

        # 验证canvas_config结构
        canvas_config = template_data.get("canvas_config", {})
        if not all(key in canvas_config for key in ["width", "height", "ratio"]):
            print("模板canvas_config结构不完整")
            return False

        # 验证materials结构
        materials = template_data.get("materials", {})
        if not isinstance(materials, dict):
            print("模板materials字段必须是字典")
            return False

        # 验证tracks结构
        tracks = template_data.get("tracks", [])
        if not isinstance(tracks, list):
            print("模板tracks字段必须是列表")
            return False

        return True

    def _update_project_info_from_template(self):
        """更新从模板加载的项目信息"""
        if self._content_data is None:
            return

        # 从配置文件获取设备和平台信息
        device_info = self._config.get("jianying", {}).get("device_info", {})
        platform_info = self._config.get("jianying", {}).get("platform_info", {})

        # 更新项目基本信息
        current_time = int(time.time())
        self._content_data["id"] = str(uuid.uuid4()).upper()
        self._content_data["name"] = self.project_name
        self._content_data["create_time"] = current_time
        self._content_data["update_time"] = current_time

        # 更新设备和平台信息
        if "last_modified_platform" in self._content_data:
            self._content_data["last_modified_platform"].update({
                "device_id": device_info.get("device_id", self._content_data["last_modified_platform"].get("device_id")),
                "hard_disk_id": device_info.get("hard_disk_id", self._content_data["last_modified_platform"].get("hard_disk_id")),
                "mac_address": device_info.get("mac_address", self._content_data["last_modified_platform"].get("mac_address")),
                "app_id": platform_info.get("app_id", self._content_data["last_modified_platform"].get("app_id")),
                "app_source": platform_info.get("app_source", self._content_data["last_modified_platform"].get("app_source")),
                "app_version": platform_info.get("app_version", self._content_data["last_modified_platform"].get("app_version")),
                "os": platform_info.get("os", self._content_data["last_modified_platform"].get("os")),
                "os_version": platform_info.get("os_version", self._content_data["last_modified_platform"].get("os_version"))
            })

        if "platform" in self._content_data:
            self._content_data["platform"].update({
                "device_id": device_info.get("device_id", self._content_data["platform"].get("device_id")),
                "hard_disk_id": device_info.get("hard_disk_id", self._content_data["platform"].get("hard_disk_id")),
                "mac_address": device_info.get("mac_address", self._content_data["platform"].get("mac_address")),
                "app_id": platform_info.get("app_id", self._content_data["platform"].get("app_id")),
                "app_source": platform_info.get("app_source", self._content_data["platform"].get("app_source")),
                "app_version": platform_info.get("app_version", self._content_data["platform"].get("app_version")),
                "os": platform_info.get("os", self._content_data["platform"].get("os")),
                "os_version": platform_info.get("os_version", self._content_data["platform"].get("os_version"))
            })

    def save_as_template(self, template_path: Union[str, Path]) -> bool:
        """
        将当前内容数据保存为模板文件

        Args:
            template_path: 模板保存路径

        Returns:
            bool: 保存是否成功
        """
        if self._content_data is None:
            print("没有内容数据可保存")
            return False

        template_file = Path(template_path)

        # 确保文件扩展名为.json
        if template_file.suffix.lower() != '.json':
            template_file = template_file.with_suffix('.json')

        try:
            # 确保目录存在
            template_file.parent.mkdir(parents=True, exist_ok=True)

            # 创建模板数据（移除项目特定信息）
            import copy
            template_data = copy.deepcopy(self._content_data)

            # 清理项目特定信息
            template_data["id"] = "TEMPLATE_ID"
            template_data["name"] = "Template Project"
            template_data["create_time"] = 0
            template_data["update_time"] = 0
            template_data["duration"] = 0

            # 清空轨道和素材（保留结构）
            template_data["tracks"] = []
            for material_type in template_data["materials"]:
                template_data["materials"][material_type] = []

            # 保存模板文件
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)

            print(f"模板保存成功: {template_file}")
            return True

        except Exception as e:
            print(f"保存模板文件失败: {e}")
            return False

    def list_available_templates(self, templates_dir: Union[str, Path] = None) -> List[Dict[str, Any]]:
        """
        列出可用的模板文件

        Args:
            templates_dir: 模板目录路径，默认为项目目录下的templates文件夹

        Returns:
            List[Dict]: 模板信息列表
        """
        if templates_dir is None:
            templates_dir = self.project_path.parent / "templates"
        else:
            templates_dir = Path(templates_dir)

        templates = []

        if not templates_dir.exists():
            return templates

        for template_file in templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                template_info = {
                    "file_path": str(template_file),
                    "file_name": template_file.name,
                    "name": template_data.get("name", template_file.stem),
                    "canvas_config": template_data.get("canvas_config", {}),
                    "version": template_data.get("version", "unknown"),
                    "track_count": len(template_data.get("tracks", [])),
                    "file_size": template_file.stat().st_size,
                    "modified_time": template_file.stat().st_mtime
                }

                templates.append(template_info)

            except Exception as e:
                print(f"读取模板文件失败 {template_file}: {e}")
                continue

        # 按修改时间排序
        templates.sort(key=lambda x: x["modified_time"], reverse=True)

        return templates

    def add_track(self, track_info: TrackInfo) -> str:
        """
        添加轨道
        
        Args:
            track_info: 轨道信息
            
        Returns:
            str: 轨道ID
        """
        if self._content_data is None:
            self.load_content_data()
        
        track_data = {
            "attribute": track_info.attribute,
            "flag": track_info.flag,
            "id": track_info.id,
            "segments": [],
            "type": track_info.track_type
        }
        
        self._content_data["tracks"].append(track_data)
        self._update_modification_time()
        
        return track_info.id
    
    def add_material_to_track(self, track_id: str, material_ref: MaterialRef) -> str:
        """
        向轨道添加素材
        
        Args:
            track_id: 轨道ID
            material_ref: 素材引用信息
            
        Returns:
            str: 片段ID
        """
        if self._content_data is None:
            self.load_content_data()
        
        # 查找轨道
        track = self._find_track_by_id(track_id)
        if not track:
            raise ValueError(f"未找到轨道: {track_id}")
        
        # 创建片段
        segment_id = str(uuid.uuid4()).upper()
        segment_data = {
            "cartoon": False,
            "clip": {
                "alpha": 1.0,
                "flip": {
                    "horizontal": False,
                    "vertical": False
                },
                "rotation": 0.0,
                "scale": {
                    "x": 1.0,
                    "y": 1.0
                },
                "transform": {
                    "x": 0.0,
                    "y": 0.0
                }
            },
            "common_keyframes": [],
            "enable_adjust": True,
            "enable_color_curves": True,
            "enable_color_match_adjust": False,
            "enable_color_wheels": True,
            "enable_lut": True,
            "enable_smart_color_adjust": False,
            "extra_material_refs": [],
            "group_id": "",
            "hdr_settings": None,
            "id": segment_id,
            "intensifies_audio": False,
            "is_placeholder": False,
            "is_tone_modify": False,
            "keyframe_refs": [],
            "last_nonzero_volume": 1.0,
            "material_id": material_ref.material_id,
            "render_index": material_ref.track_render_index,
            "reverse": False,
            "source_timerange": {
                "duration": material_ref.duration,
                "start": 0
            },
            "speed": 1.0,
            "target_timerange": {
                "duration": material_ref.duration,
                "start": material_ref.start_time
            },
            "template_id": "",
            "template_scene": "default",
            "track_attribute": 0,
            "track_render_index": material_ref.track_render_index,
            "uniform_scale": None,
            "visible": True,
            "volume": 1.0
        }
        
        track["segments"].append(segment_data)
        self._update_modification_time()

        return segment_id

    def _find_track_by_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查找轨道"""
        if self._content_data is None:
            return None

        for track in self._content_data["tracks"]:
            if track.get("id") == track_id:
                return track
        return None

    def _update_modification_time(self):
        """更新修改时间"""
        if self._content_data:
            self._content_data["update_time"] = int(time.time())

    def get_tracks(self) -> List[Dict[str, Any]]:
        """获取所有轨道"""
        if self._content_data is None:
            self.load_content_data()
        return self._content_data.get("tracks", [])

    def get_track_by_type(self, track_type: str) -> List[Dict[str, Any]]:
        """根据类型获取轨道"""
        tracks = self.get_tracks()
        return [track for track in tracks if track.get("type") == track_type]

    def remove_track(self, track_id: str) -> bool:
        """删除轨道"""
        if self._content_data is None:
            self.load_content_data()

        tracks = self._content_data["tracks"]
        for i, track in enumerate(tracks):
            if track.get("id") == track_id:
                del tracks[i]
                self._update_modification_time()
                return True
        return False

    def remove_segment_from_track(self, track_id: str, segment_id: str) -> bool:
        """从轨道中删除片段"""
        track = self._find_track_by_id(track_id)
        if not track:
            return False

        segments = track.get("segments", [])
        for i, segment in enumerate(segments):
            if segment.get("id") == segment_id:
                del segments[i]
                self._update_modification_time()
                return True
        return False

    def update_project_duration(self, duration: int):
        """更新项目总时长（微秒）"""
        if self._content_data is None:
            self.load_content_data()

        self._content_data["duration"] = duration
        self._update_modification_time()

    def update_canvas_config(self, width: int = 1920, height: int = 1080, ratio: str = "original"):
        """更新画布配置"""
        if self._content_data is None:
            self.load_content_data()

        self._content_data["canvas_config"] = {
            "width": width,
            "height": height,
            "ratio": ratio
        }
        self._update_modification_time()

    def add_material_reference(self, material_type: str, material_data: Dict[str, Any]) -> str:
        """
        添加素材引用到materials中

        Args:
            material_type: 素材类型 (videos, audios, images, texts等)
            material_data: 素材数据

        Returns:
            str: 素材ID
        """
        if self._content_data is None:
            self.load_content_data()

        if material_type not in self._content_data["materials"]:
            raise ValueError(f"不支持的素材类型: {material_type}")

        # 确保素材有ID
        if "id" not in material_data:
            material_data["id"] = str(uuid.uuid4()).upper()

        self._content_data["materials"][material_type].append(material_data)
        self._update_modification_time()

        return material_data["id"]

    def update_material_reference(self, material_type: str, material_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新素材引用信息

        Args:
            material_type: 素材类型 (videos, audios, images, texts等)
            material_id: 素材ID
            updates: 要更新的字段和值

        Returns:
            bool: 更新是否成功
        """
        if self._content_data is None:
            self.load_content_data()

        if material_type not in self._content_data["materials"]:
            print(f"不支持的素材类型: {material_type}")
            return False

        materials = self._content_data["materials"][material_type]

        # 查找要更新的素材
        for material in materials:
            if material.get("id") == material_id:
                # 更新素材信息
                for key, value in updates.items():
                    material[key] = value

                self._update_modification_time()
                print(f"成功更新素材 {material_id} 的 {len(updates)} 个字段")
                return True

        print(f"未找到素材: {material_id} (类型: {material_type})")
        return False

    def get_material_reference(self, material_type: str, material_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的素材引用信息

        Args:
            material_type: 素材类型
            material_id: 素材ID

        Returns:
            Dict: 素材信息，如果未找到返回None
        """
        if self._content_data is None:
            self.load_content_data()

        if material_type not in self._content_data["materials"]:
            return None

        materials = self._content_data["materials"][material_type]

        for material in materials:
            if material.get("id") == material_id:
                return material

        return None

    def update_material_reference_batch(self, updates_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量更新素材引用信息

        Args:
            updates_list: 更新列表，每个元素包含 material_type, material_id, updates

        Returns:
            Dict: 更新结果统计 {"success": 成功数量, "failed": 失败数量}
        """
        if self._content_data is None:
            self.load_content_data()

        success_count = 0
        failed_count = 0

        for update_item in updates_list:
            material_type = update_item.get("material_type")
            material_id = update_item.get("material_id")
            updates = update_item.get("updates", {})

            if not material_type or not material_id:
                print(f"批量更新项缺少必需字段: {update_item}")
                failed_count += 1
                continue

            success = self.update_material_reference(material_type, material_id, updates)
            if success:
                success_count += 1
            else:
                failed_count += 1

        print(f"批量更新完成: 成功 {success_count}, 失败 {failed_count}")
        return {"success": success_count, "failed": failed_count}

    def get_materials_by_type(self, material_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的素材"""
        if self._content_data is None:
            self.load_content_data()

        return self._content_data.get("materials", {}).get(material_type, [])

    def remove_material_reference(self, material_type: str, material_id: str) -> bool:
        """删除素材引用"""
        if self._content_data is None:
            self.load_content_data()

        materials = self._content_data.get("materials", {}).get(material_type, [])
        for i, material in enumerate(materials):
            if material.get("id") == material_id:
                del materials[i]
                self._update_modification_time()
                return True
        return False

    def find_material_references(self, material_id: str) -> List[Dict[str, Any]]:
        """
        查找指定素材ID在所有类型中的引用

        Args:
            material_id: 素材ID

        Returns:
            List[Dict]: 包含素材类型和素材信息的列表
        """
        if self._content_data is None:
            self.load_content_data()

        references = []

        for material_type, materials in self._content_data["materials"].items():
            for material in materials:
                if material.get("id") == material_id:
                    references.append({
                        "material_type": material_type,
                        "material_data": material
                    })

        return references

    def find_material_reference_by_material_name(self, material_name: str, material_type: str = None, exact_match: bool = True) -> List[Dict[str, Any]]:
        """
        根据素材名称查找素材引用

        Args:
            material_name: 要查找的素材名称
            material_type: 可选，指定素材类型进行过滤 (videos, audios, images等)
            exact_match: 是否精确匹配，False时进行模糊匹配

        Returns:
            List[Dict]: 匹配的素材引用列表，每个元素包含 material_type, material_data
        """
        if self._content_data is None:
            self.load_content_data()

        matches = []

        # 确定要搜索的素材类型
        search_types = [material_type] if material_type else self._content_data["materials"].keys()

        for search_type in search_types:
            if search_type not in self._content_data["materials"]:
                continue

            materials = self._content_data["materials"][search_type]

            for material in materials:
                material_name_in_data = material.get("name", "")

                # 根据匹配模式进行比较
                if exact_match:
                    # 精确匹配
                    if material_name_in_data == material_name:
                        matches.append({
                            "material_type": search_type,
                            "material_data": material
                        })
                else:
                    # 模糊匹配（不区分大小写）
                    if material_name.lower() in material_name_in_data.lower():
                        matches.append({
                            "material_type": search_type,
                            "material_data": material
                        })

        return matches

    def find_material_reference_by_file_path(self, file_path: str, exact_match: bool = True) -> List[Dict[str, Any]]:
        """
        根据文件路径查找素材引用

        Args:
            file_path: 要查找的文件路径
            exact_match: 是否精确匹配，False时进行模糊匹配

        Returns:
            List[Dict]: 匹配的素材引用列表
        """
        if self._content_data is None:
            self.load_content_data()

        matches = []

        for material_type, materials in self._content_data["materials"].items():
            for material in materials:
                material_file_path = material.get("file_path", "") or material.get("file_Path", "")

                if exact_match:
                    # 精确匹配
                    if material_file_path == file_path:
                        matches.append({
                            "material_type": material_type,
                            "material_data": material
                        })
                else:
                    # 模糊匹配（路径包含）
                    if file_path.lower() in material_file_path.lower():
                        matches.append({
                            "material_type": material_type,
                            "material_data": material
                        })

        return matches

    def find_material_reference_by_attributes(self, search_criteria: Dict[str, Any], match_all: bool = True) -> List[Dict[str, Any]]:
        """
        根据素材属性查找素材引用

        Args:
            search_criteria: 搜索条件字典，键为属性名，值为要匹配的值
            match_all: True时所有条件都必须匹配，False时匹配任一条件即可

        Returns:
            List[Dict]: 匹配的素材引用列表
        """
        if self._content_data is None:
            self.load_content_data()

        matches = []

        for material_type, materials in self._content_data["materials"].items():
            for material in materials:
                match_count = 0

                for key, value in search_criteria.items():
                    material_value = material.get(key)

                    # 支持不同类型的匹配
                    if isinstance(value, str) and isinstance(material_value, str):
                        # 字符串模糊匹配
                        if value.lower() in material_value.lower():
                            match_count += 1
                    elif material_value == value:
                        # 精确匹配
                        match_count += 1

                # 根据匹配模式决定是否添加到结果
                if match_all:
                    # 所有条件都必须匹配
                    if match_count == len(search_criteria):
                        matches.append({
                            "material_type": material_type,
                            "material_data": material
                        })
                else:
                    # 匹配任一条件即可
                    if match_count > 0:
                        matches.append({
                            "material_type": material_type,
                            "material_data": material
                        })

        return matches

    def search_materials(self, query: str, search_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        在素材中进行全文搜索

        Args:
            query: 搜索查询字符串
            search_fields: 要搜索的字段列表，默认搜索 name, file_path, description

        Returns:
            List[Dict]: 匹配的素材引用列表
        """
        if self._content_data is None:
            self.load_content_data()

        if search_fields is None:
            search_fields = ["name", "file_path", "file_Path", "description", "extra_info"]

        matches = []
        query_lower = query.lower()

        for material_type, materials in self._content_data["materials"].items():
            for material in materials:
                found = False

                for field in search_fields:
                    field_value = material.get(field, "")
                    if isinstance(field_value, str) and query_lower in field_value.lower():
                        found = True
                        break

                if found:
                    matches.append({
                        "material_type": material_type,
                        "material_data": material,
                        "matched_fields": [
                            field for field in search_fields
                            if isinstance(material.get(field, ""), str) and
                            query_lower in material.get(field, "").lower()
                        ]
                    })

        return matches

    def get_all_material_ids(self) -> Dict[str, List[str]]:
        """
        获取所有素材类型的素材ID列表

        Returns:
            Dict: 按类型分组的素材ID列表
        """
        if self._content_data is None:
            self.load_content_data()

        all_ids = {}

        for material_type, materials in self._content_data["materials"].items():
            ids = [material.get("id") for material in materials if material.get("id")]
            if ids:  # 只包含非空的ID列表
                all_ids[material_type] = ids

        return all_ids

    def validate_material_references(self) -> Dict[str, Any]:
        """
        验证素材引用的完整性

        Returns:
            Dict: 验证结果，包含错误和警告信息
        """
        if self._content_data is None:
            self.load_content_data()

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {
                "total_materials": 0,
                "materials_by_type": {},
                "duplicate_ids": [],
                "missing_ids": []
            }
        }

        all_ids = []
        materials_by_type = {}

        # 收集所有素材ID和统计信息
        for material_type, materials in self._content_data["materials"].items():
            type_ids = []
            for material in materials:
                material_id = material.get("id")
                if material_id:
                    all_ids.append(material_id)
                    type_ids.append(material_id)
                else:
                    validation_result["errors"].append(f"素材缺少ID: {material_type}")
                    validation_result["valid"] = False

            if type_ids:
                materials_by_type[material_type] = len(type_ids)
                validation_result["statistics"]["materials_by_type"][material_type] = len(type_ids)

        validation_result["statistics"]["total_materials"] = len(all_ids)

        # 检查重复ID
        seen_ids = set()
        for material_id in all_ids:
            if material_id in seen_ids:
                validation_result["statistics"]["duplicate_ids"].append(material_id)
                validation_result["errors"].append(f"重复的素材ID: {material_id}")
                validation_result["valid"] = False
            else:
                seen_ids.add(material_id)

        # 检查轨道中引用的素材ID是否存在
        tracks = self._content_data.get("tracks", [])
        for track in tracks:
            segments = track.get("segments", [])
            for segment in segments:
                segment_material_id = segment.get("material_id")
                if segment_material_id and segment_material_id not in seen_ids:
                    validation_result["statistics"]["missing_ids"].append(segment_material_id)
                    validation_result["warnings"].append(f"轨道片段引用了不存在的素材ID: {segment_material_id}")

        return validation_result

    def cleanup_unused_materials(self) -> Dict[str, int]:
        """
        清理未使用的素材引用

        Returns:
            Dict: 清理结果统计
        """
        if self._content_data is None:
            self.load_content_data()

        # 收集轨道中使用的素材ID
        used_material_ids = set()
        tracks = self._content_data.get("tracks", [])

        for track in tracks:
            segments = track.get("segments", [])
            for segment in segments:
                material_id = segment.get("material_id")
                if material_id:
                    used_material_ids.add(material_id)

        # 清理未使用的素材
        cleanup_stats = {}
        total_removed = 0

        for material_type, materials in self._content_data["materials"].items():
            original_count = len(materials)

            # 保留被使用的素材
            used_materials = [
                material for material in materials
                if material.get("id") in used_material_ids
            ]

            removed_count = original_count - len(used_materials)
            if removed_count > 0:
                self._content_data["materials"][material_type] = used_materials
                cleanup_stats[material_type] = removed_count
                total_removed += removed_count

        if total_removed > 0:
            self._update_modification_time()
            print(f"清理了 {total_removed} 个未使用的素材引用")

        return cleanup_stats

    def get_project_info(self) -> Dict[str, Any]:
        """获取项目基本信息"""
        if self._content_data is None:
            self.load_content_data()

        return {
            "id": self._content_data.get("id"),
            "name": self._content_data.get("name"),
            "duration": self._content_data.get("duration", 0),
            "fps": self._content_data.get("fps", 30.0),
            "canvas_config": self._content_data.get("canvas_config", {}),
            "create_time": self._content_data.get("create_time", 0),
            "update_time": self._content_data.get("update_time", 0),
            "version": self._content_data.get("version", 360000)
        }

    def update_project_info(self, **kwargs):
        """更新项目信息"""
        if self._content_data is None:
            self.load_content_data()

        allowed_fields = ["name", "duration", "fps"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                self._content_data[field] = value

        self._update_modification_time()

    def save_content_data(self) -> bool:
        """保存内容数据到文件"""
        if self._content_data is None:
            return False

        try:
            # 确保项目目录存在
            self.project_path.mkdir(parents=True, exist_ok=True)

            # 保存文件
            with open(self.content_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._content_data, f, ensure_ascii=False, indent=4)

            return True
        except Exception as e:
            print(f"保存内容数据失败: {e}")
            return False

    def clear_all_tracks(self):
        """清空所有轨道"""
        if self._content_data is None:
            self.load_content_data()

        self._content_data["tracks"] = []
        self._update_modification_time()

    def clear_all_materials(self):
        """清空所有素材引用"""
        if self._content_data is None:
            self.load_content_data()

        # 重置所有素材列表
        for material_type in self._content_data["materials"]:
            self._content_data["materials"][material_type] = []

        self._update_modification_time()

    def get_timeline_summary(self) -> Dict[str, Any]:
        """获取时间轴摘要信息"""
        if self._content_data is None:
            self.load_content_data()

        tracks = self._content_data.get("tracks", [])

        summary = {
            "total_tracks": len(tracks),
            "track_types": {},
            "total_segments": 0,
            "project_duration": self._content_data.get("duration", 0)
        }

        for track in tracks:
            track_type = track.get("type", "unknown")
            segments = track.get("segments", [])

            if track_type not in summary["track_types"]:
                summary["track_types"][track_type] = {
                    "count": 0,
                    "segments": 0
                }

            summary["track_types"][track_type]["count"] += 1
            summary["track_types"][track_type]["segments"] += len(segments)
            summary["total_segments"] += len(segments)

        return summary

    def create_new_project(self, template_data: Optional[Dict] = None):
        """创建新的剪映项目内容"""
        # 创建基础内容结构
        self._content_data = {
            "duration": template_data.get("duration", 30000000) if template_data else 30000000,  # 默认30秒
            "materials": {
                "videos": [],
                "audios": [],
                "images": [],
                "texts": []
            },
            "tracks": [],
            "canvases": [
                {
                    "album_image": "",
                    "blur": 0.0,
                    "color": "",
                    "id": str(uuid.uuid4()).upper(),
                    "image": "",
                    "image_id": "",
                    "image_name": "",
                    "source_platform": 0,
                    "team_id": "",
                    "type": "canvas_color"
                }
            ],
            "cover": {
                "category": 0,
                "has_use_smart_cover": False,
                "images": [],
                "is_custom": True,
                "is_smart": False,
                "path": "",
                "source_platform": 0,
                "team_id": ""
            },
            "extra_info": {
                "export_range": {
                    "duration": template_data.get("duration", 30000000) if template_data else 30000000,
                    "start": 0
                }
            },
            "id": str(uuid.uuid4()).upper(),
            "new_version": "12.2.0",
            "platform": {
                "device_id": "device_id_placeholder",
                "hard_disk_id": "hard_disk_id_placeholder",
                "mac_address": "mac_address_placeholder",
                "os": "windows",
                "version": "12.2.0"
            },
            "relationships": [],
            "revert": False,
            "source_platform": 0,
            "team_id": "",
            "version": 15
        }

        # 保存文件
        return self.save_project()

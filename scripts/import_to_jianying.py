import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import uuid
import time
import shutil
import subprocess
import random

def get_video_metadata(video_path):
    """使用 ffprobe 获取视频元数据"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, encoding='utf-8')
        data = json.loads(result.stdout)
        
        video_stream = next((stream for stream in data['streams'] if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            return None, None, None

        duration_ns = int(float(video_stream.get('duration', 0)) * 1_000_000_000)
        width = int(video_stream.get('width', 0))
        height = int(video_stream.get('height', 0))
        
        return duration_ns, width, height
        
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"获取视频元数据失败: {video_path},错误: {e}")
        return None, None, None

def create_new_project_json(video_paths):
    """基于模板和视频文件列表创建剪映工程JSON"""
    try:
        # 获取脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "jianying", "draft_content.json")

        if not os.path.exists(template_path):
            messagebox.showerror("错误", f"未找到剪映模板文件: {template_path}")
            return None

        with open(template_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

    except Exception as e:
        messagebox.showerror("错误", f"加载剪映模板失败: {e}")
        return None

    # 清空模板中的素材和轨道
    project_data["materials"]["videos"] = []
    project_data["tracks"] = []
    
    total_duration_ns = 0
    
    # 为主轨道创建一个ID
    main_track_id = str(uuid.uuid4()).upper()

    # 创建主轨道
    main_track = {
        "attribute": 0,
        "flag": 0,
        "id": main_track_id,
        "is_default_name": True,
        "segments": [],
        "type": "video"
    }
    
    for i, video_path in enumerate(video_paths):
        duration_ns, width, height = get_video_metadata(video_path)
        
        if duration_ns is None:
            print(f"跳过文件 {video_path} 因为无法获取元数据")
            continue
        
        # 使用相对路径，剪映需要
        draft_video_path = os.path.join("video", os.path.basename(video_path))
        material_id = str(uuid.uuid4()).upper()
        segment_id = str(uuid.uuid4()).upper()

        # 添加到 materials
        video_material = {
            "aigc_type": "none",
            "algorithm_gear": "default",
            "audio_fade": None,
            "cartoon_path": "",
            "category_id": "",
            "category_name": "local",
            "check_flag": 63487,
            "crop": { "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0, "upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0 },
            "crop_ratio": "free",
            "crop_scale": 1.0,
            "duration": duration_ns,
            "extra_type_option": 0,
            "formula_id": "",
            "freeze": None,
            "gameplay": None,
            "has_audio": True, # 假设有音频
            "height": height,
            "id": material_id,
            "import_time": int(time.time()),
            "intensifies_audio_path": "",
            "intensifies_path": "",
            "is_ai_matting": False,
            "is_trans_video": False,
            "local_id": "",
            "matting": { "flag": 0, "has_real_time_matting": False, "interactive_matting_path": "", "path": "" },
            "media_meta": None,
            "path": draft_video_path,
            "real_duration": duration_ns,
            "recognize_type": 0,
            "reverse_intensifies_path": "",
            "reverse_path": "",
            "source": 0,
            "source_platform": 0,
            "stable": None,
            "team_id": "",
            "type": "video",
            "video_algorithm": { "algorithms": [], "deflicker": None, "motion_blur_config": None, "noise_reduction": None, "path": "", "time_range": None },
            "width": width
        }
        project_data["materials"]["videos"].append(video_material)

        # 添加到轨道
        track_segment = {
            "cartoon": False,
            "clip": { "alpha": 1.0, "flip": { "horizontal": False, "vertical": False }, "rotation": 0.0, "scale": { "x": 1.0, "y": 1.0 }, "transform": { "x": 0.0, "y": 0.0 } },
            "enable_adjust": True,
            "enable_color_curves": True,
            "enable_color_wheels": True,
            "enable_lut": False,
            "extra_material_refs": [],
            "got_audio_recognize_result": True,
            "hdr_settings": { "intensity": 1.0, "mode": 1, "sdr_mode": 1 },
            "id": segment_id,
            "intensifies_audio": False,
            "is_placeholder": False,
            "is_tone_modify": False,
            "key_frame_refs": [],
            "last_operation_id": "",
            "material_id": material_id,
            "render_index": 0,
            "responsive_layout": { "enable": False, "target_adaptive_type": 0, "target_follow_type": 0, "target_id": "" },
            "reverse": False,
            "source_timerange": { "duration": duration_ns, "start": 0 },
            "speed": 1.0,
            "target_timerange": { "duration": duration_ns, "start": total_duration_ns },
            "template_id": "",
            "template_scene": "default",
            "track_attribute": 0,
            "track_render_index": 0,
            "uniform_scale": None,
            "visible": True
        }
        main_track["segments"].append(track_segment)
        
        total_duration_ns += duration_ns

    # 添加轨道到工程
    project_data["tracks"].append(main_track)
    
    # 更新工程总时长
    project_data["duration"] = total_duration_ns
    
    # 更新工程时间
    now = int(time.time())
    project_data["create_time"] = now
    project_data["update_time"] = now
    
    # 更新工程ID
    project_data["id"] = str(uuid.uuid4()).upper()

    return project_data

def generate_random_draft_id():
    """生成剪映草稿ID（格式：draft_timestamp_randomstr）"""
    timestamp = int(time.time())
    random_str = ''.join(random.choices('0123456789abcdef', k=6))
    return f"draft_{timestamp}_{random_str}"

def copy_to_jianying_draft(ordered_clip_paths):
    """将视频片段按指定顺序复制到剪映草稿目录并生成配置文件"""
    # 获取剪映草稿目录
    base_draft_path = os.path.expandvars(r"%LOCALAPPDATA%\\JianyingPro\\User Data\\Projects\\com.lveditor.draft")
    if not os.path.exists(base_draft_path):
        os.makedirs(base_draft_path)
    
    # 生成新的草稿ID
    draft_id = generate_random_draft_id()
    draft_path = os.path.join(base_draft_path, draft_id)
    
    try:
        # 创建新的草稿目录
        os.makedirs(draft_path)
        
        # 复制视频文件
        draft_video_dir = os.path.join(draft_path, "video")
        os.makedirs(draft_video_dir)
        
        copied_video_paths = []
        for i, clip_path in enumerate(ordered_clip_paths):
            if os.path.exists(clip_path):
                file_extension = os.path.splitext(clip_path)[1]
                new_filename = f"video_{i+1:03d}{file_extension}"
                dst_path = os.path.join(draft_video_dir, new_filename)
                
                shutil.copy2(clip_path, dst_path)
                copied_video_paths.append(dst_path)
                print(f"复制片段 {i+1}: {os.path.basename(clip_path)} -> {new_filename}")
        
        # 复制draft_meta_info.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        meta_info_src = os.path.join(current_dir, "jianying", "draft_meta_info.json")
        if os.path.exists(meta_info_src):
            with open(meta_info_src, 'r', encoding='utf-8') as f:
                meta_info = json.load(f)
                meta_info["draft_id"] = draft_id
                meta_info["create_time"] = int(time.time())
                meta_info["modify_time"] = int(time.time())
            
            meta_info_dst = os.path.join(draft_path, "draft_meta_info.json")
            with open(meta_info_dst, 'w', encoding='utf-8') as f:
                json.dump(meta_info, f, indent=2)
        else:
            print(f"警告：未找到draft_meta_info.json模板文件: {meta_info_src}")
        
        # 生成draft_content.json
        project_data = create_new_project_json(ordered_clip_paths) # 使用原始路径获取元数据
        if project_data:
            json_path = os.path.join(draft_path, "draft_content.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=4)
            
            return draft_id, draft_path
        
        return None, None
        
    except Exception as e:
        print(f"导入剪映时发生错误: {str(e)}")
        if os.path.exists(draft_path):
            try:
                shutil.rmtree(draft_path)
            except:
                pass
        return None, None

class JianyingImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频导入剪映工具")
        self.root.geometry("600x400")
        self.file_paths = []

        # 主框架
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件选择部分
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(file_frame, text="选择视频文件", command=self.choose_files).pack(side=tk.LEFT)
        self.file_label = tk.Label(file_frame, text="尚未选择文件", wraplength=450)
        self.file_label.pack(side=tk.LEFT, padx=10)

        # 导入按钮
        tk.Button(main_frame, text="导入到剪映", command=self.import_to_jianying, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=10, fill=tk.X)

        # 日志显示
        tk.Label(main_frame, text="处理日志:").pack(anchor='w')
        self.log_text = scrolledtext.ScrolledText(main_frame, width=70, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 重定向print到日志框
        sys.stdout = self.PrintRedirector(self.log_text)

    def choose_files(self):
        file_paths = filedialog.askopenfilenames(
            title="选择要导入的MP4文件（按顺序）",
            filetypes=[("MP4文件", "*.mp4")]
        )
        if file_paths:
            self.file_paths = list(file_paths)
            self.file_label.config(text=f"已选择 {len(self.file_paths)} 个文件")
            self.log_text.insert(tk.END, f"选择了 {len(self.file_paths)} 个视频文件:\n")
            for path in self.file_paths:
                self.log_text.insert(tk.END, f"- {os.path.basename(path)}\n")
            self.log_text.insert(tk.END, "\n")


    def import_to_jianying(self):
        if not self.file_paths:
            messagebox.showerror("错误", "请先选择视频文件！")
            return
        
        self.log_text.insert(tk.END, "====== 开始导入到剪映 ======\n")
        self.root.update_idletasks()
        
        try:
            draft_id, draft_path = copy_to_jianying_draft(self.file_paths)
            
            if draft_id and draft_path:
                success_message = f"✅ 成功导入到剪映！\n草稿ID: {draft_id}\n路径: {draft_path}"
                self.log_text.insert(tk.END, success_message + "\n")
                messagebox.showinfo("成功", success_message)
            else:
                error_message = "❌ 导入剪映失败！请查看日志获取详细信息。"
                self.log_text.insert(tk.END, error_message + "\n")
                messagebox.showerror("失败", error_message)
        except Exception as e:
            self.log_text.insert(tk.END, f"❌ 发生未知错误: {e}\n")
            import traceback
            self.log_text.insert(tk.END, traceback.format_exc() + "\n")
            messagebox.showerror("严重错误", f"发生严重错误: {e}")
        finally:
            self.log_text.insert(tk.END, "====== 导入结束 ======\n\n")

    # 用于重定向 print 输出
    class PrintRedirector:
        def __init__(self, text_widget):
            self.text_space = text_widget

        def write(self, string):
            self.text_space.insert('end', string)
            self.text_space.see('end')
        
        def flush(self):
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = JianyingImporterApp(root)
    root.mainloop()
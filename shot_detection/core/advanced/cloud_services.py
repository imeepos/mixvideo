"""
Cloud Services Module
云服务模块
"""

import json
import time
import hashlib
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from loguru import logger


class CloudStorage:
    """云存储服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化云存储服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="CloudStorage")
        
        # 云存储配置
        self.storage_config = self.config.get('cloud_storage', {
            'provider': 'aws_s3',  # aws_s3, azure_blob, gcp_storage
            'bucket_name': 'shot-detection-storage',
            'region': 'us-west-2',
            'access_key': '',
            'secret_key': '',
            'encryption': True,
            'compression': True,
            'max_file_size_mb': 1024,
            'retry_attempts': 3
        })
        
        # 连接状态
        self.connected = False
        self.client = None
        
        self.logger.info("Cloud storage service initialized")
    
    def connect(self) -> bool:
        """连接到云存储"""
        try:
            provider = self.storage_config['provider']
            
            if provider == 'aws_s3':
                self.client = self._connect_aws_s3()
            elif provider == 'azure_blob':
                self.client = self._connect_azure_blob()
            elif provider == 'gcp_storage':
                self.client = self._connect_gcp_storage()
            else:
                raise ValueError(f"Unsupported storage provider: {provider}")
            
            if self.client:
                self.connected = True
                self.logger.info(f"Connected to {provider}")
                return True
            else:
                self.logger.error(f"Failed to connect to {provider}")
                return False
                
        except Exception as e:
            self.logger.error(f"Cloud storage connection failed: {e}")
            return False
    
    def upload_file(self, local_path: str, remote_path: str,
                   progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        上传文件到云存储
        
        Args:
            local_path: 本地文件路径
            remote_path: 远程文件路径
            progress_callback: 进度回调函数
            
        Returns:
            上传结果
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {"success": False, "error": "Not connected to cloud storage"}
            
            local_file = Path(local_path)
            if not local_file.exists():
                return {"success": False, "error": f"Local file not found: {local_path}"}
            
            file_size = local_file.stat().st_size
            max_size = self.storage_config['max_file_size_mb'] * 1024 * 1024
            
            if file_size > max_size:
                return {"success": False, "error": f"File too large: {file_size} bytes"}
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(local_path)
            
            # 检查文件是否已存在
            if self._file_exists(remote_path):
                existing_hash = self._get_file_hash(remote_path)
                if existing_hash == file_hash:
                    return {
                        "success": True,
                        "message": "File already exists with same content",
                        "remote_path": remote_path,
                        "file_hash": file_hash
                    }
            
            # 执行上传
            upload_result = self._upload_file_impl(local_path, remote_path, progress_callback)
            
            if upload_result["success"]:
                self.logger.info(f"File uploaded successfully: {remote_path}")
                return {
                    "success": True,
                    "remote_path": remote_path,
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "upload_time": upload_result.get("upload_time", 0)
                }
            else:
                return upload_result
                
        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def download_file(self, remote_path: str, local_path: str,
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        从云存储下载文件
        
        Args:
            remote_path: 远程文件路径
            local_path: 本地文件路径
            progress_callback: 进度回调函数
            
        Returns:
            下载结果
        """
        try:
            if not self.connected:
                if not self.connect():
                    return {"success": False, "error": "Not connected to cloud storage"}
            
            if not self._file_exists(remote_path):
                return {"success": False, "error": f"Remote file not found: {remote_path}"}
            
            # 创建本地目录
            local_file = Path(local_path)
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 执行下载
            download_result = self._download_file_impl(remote_path, local_path, progress_callback)
            
            if download_result["success"]:
                self.logger.info(f"File downloaded successfully: {local_path}")
                return {
                    "success": True,
                    "local_path": local_path,
                    "file_size": local_file.stat().st_size,
                    "download_time": download_result.get("download_time", 0)
                }
            else:
                return download_result
                
        except Exception as e:
            self.logger.error(f"File download failed: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, prefix: str = "") -> Dict[str, Any]:
        """列出云存储中的文件"""
        try:
            if not self.connected:
                if not self.connect():
                    return {"success": False, "error": "Not connected to cloud storage"}
            
            files = self._list_files_impl(prefix)
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_file(self, remote_path: str) -> Dict[str, Any]:
        """删除云存储中的文件"""
        try:
            if not self.connected:
                if not self.connect():
                    return {"success": False, "error": "Not connected to cloud storage"}
            
            if not self._file_exists(remote_path):
                return {"success": False, "error": f"Remote file not found: {remote_path}"}
            
            success = self._delete_file_impl(remote_path)
            
            if success:
                self.logger.info(f"File deleted successfully: {remote_path}")
                return {"success": True, "remote_path": remote_path}
            else:
                return {"success": False, "error": "Failed to delete file"}
                
        except Exception as e:
            self.logger.error(f"File deletion failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _connect_aws_s3(self):
        """连接到AWS S3（模拟实现）"""
        # 这里应该使用boto3连接到AWS S3
        # 暂时返回模拟客户端
        class MockS3Client:
            def __init__(self, config):
                self.config = config
        
        return MockS3Client(self.storage_config)
    
    def _connect_azure_blob(self):
        """连接到Azure Blob Storage（模拟实现）"""
        # 这里应该使用azure-storage-blob连接
        class MockAzureClient:
            def __init__(self, config):
                self.config = config
        
        return MockAzureClient(self.storage_config)
    
    def _connect_gcp_storage(self):
        """连接到Google Cloud Storage（模拟实现）"""
        # 这里应该使用google-cloud-storage连接
        class MockGCPClient:
            def __init__(self, config):
                self.config = config
        
        return MockGCPClient(self.storage_config)
    
    def _upload_file_impl(self, local_path: str, remote_path: str,
                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """实际的文件上传实现"""
        try:
            start_time = time.time()
            
            # 模拟上传过程
            file_size = Path(local_path).stat().st_size
            chunk_size = 1024 * 1024  # 1MB chunks
            uploaded = 0
            
            while uploaded < file_size:
                chunk_uploaded = min(chunk_size, file_size - uploaded)
                uploaded += chunk_uploaded
                
                if progress_callback:
                    progress = uploaded / file_size
                    progress_callback(progress, f"上传中 {uploaded}/{file_size} 字节")
                
                # 模拟网络延迟
                time.sleep(0.01)
            
            upload_time = time.time() - start_time
            
            return {
                "success": True,
                "upload_time": upload_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _download_file_impl(self, remote_path: str, local_path: str,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """实际的文件下载实现"""
        try:
            start_time = time.time()
            
            # 模拟下载过程
            # 这里应该实现实际的下载逻辑
            with open(local_path, 'w') as f:
                f.write(f"# Downloaded from {remote_path}")
            
            download_time = time.time() - start_time
            
            return {
                "success": True,
                "download_time": download_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _file_exists(self, remote_path: str) -> bool:
        """检查远程文件是否存在"""
        # 模拟实现
        return True
    
    def _get_file_hash(self, remote_path: str) -> str:
        """获取远程文件哈希"""
        # 模拟实现
        return "mock_hash"
    
    def _list_files_impl(self, prefix: str) -> List[Dict[str, Any]]:
        """实际的文件列表实现"""
        # 模拟实现
        return [
            {
                "path": f"{prefix}file1.mp4",
                "size": 1024000,
                "modified": "2024-01-01T12:00:00Z"
            },
            {
                "path": f"{prefix}file2.json",
                "size": 2048,
                "modified": "2024-01-01T13:00:00Z"
            }
        ]
    
    def _delete_file_impl(self, remote_path: str) -> bool:
        """实际的文件删除实现"""
        # 模拟实现
        return True
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def disconnect(self):
        """断开云存储连接"""
        self.connected = False
        self.client = None
        self.logger.info("Disconnected from cloud storage")
    
    def cleanup(self):
        """清理资源"""
        self.disconnect()
        self.logger.info("Cloud storage cleanup completed")


class CloudProcessor:
    """云处理服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化云处理服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="CloudProcessor")
        
        # 云处理配置
        self.processor_config = self.config.get('cloud_processor', {
            'api_endpoint': 'https://api.shotdetection.com/v1',
            'api_key': '',
            'timeout': 300,
            'max_retries': 3,
            'batch_size': 10,
            'priority': 'normal'  # low, normal, high
        })
        
        # 云存储服务
        self.cloud_storage = CloudStorage(config)
        
        self.logger.info("Cloud processor service initialized")
    
    def process_video_cloud(self, video_path: str, 
                           processing_options: Optional[Dict[str, Any]] = None,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        在云端处理视频
        
        Args:
            video_path: 视频文件路径
            processing_options: 处理选项
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        try:
            options = processing_options or {}
            
            # 1. 上传视频到云存储
            if progress_callback:
                progress_callback(0.1, "上传视频到云端...")
            
            upload_result = self._upload_video(video_path)
            if not upload_result["success"]:
                return upload_result
            
            # 2. 提交处理任务
            if progress_callback:
                progress_callback(0.2, "提交处理任务...")
            
            task_result = self._submit_processing_task(
                upload_result["remote_path"], options
            )
            if not task_result["success"]:
                return task_result
            
            # 3. 等待处理完成
            if progress_callback:
                progress_callback(0.3, "等待云端处理...")
            
            completion_result = self._wait_for_completion(
                task_result["task_id"], progress_callback
            )
            if not completion_result["success"]:
                return completion_result
            
            # 4. 下载处理结果
            if progress_callback:
                progress_callback(0.9, "下载处理结果...")
            
            download_result = self._download_results(completion_result["result_path"])
            
            if progress_callback:
                progress_callback(1.0, "云端处理完成")
            
            return {
                "success": True,
                "task_id": task_result["task_id"],
                "processing_time": completion_result.get("processing_time", 0),
                "result_path": download_result.get("local_path", ""),
                "cloud_result": completion_result
            }
            
        except Exception as e:
            self.logger.error(f"Cloud processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _upload_video(self, video_path: str) -> Dict[str, Any]:
        """上传视频到云存储"""
        try:
            remote_path = f"videos/{Path(video_path).name}"
            return self.cloud_storage.upload_file(video_path, remote_path)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _submit_processing_task(self, remote_video_path: str, 
                               options: Dict[str, Any]) -> Dict[str, Any]:
        """提交处理任务到云端"""
        try:
            # 构建任务请求
            task_request = {
                "video_path": remote_video_path,
                "algorithm": options.get("algorithm", "frame_difference"),
                "threshold": options.get("threshold", 0.3),
                "priority": self.processor_config["priority"],
                "callback_url": options.get("callback_url", "")
            }
            
            # 模拟API调用
            task_id = f"task_{int(time.time())}"
            
            self.logger.info(f"Processing task submitted: {task_id}")
            
            return {
                "success": True,
                "task_id": task_id,
                "estimated_time": 60  # 预估处理时间（秒）
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _wait_for_completion(self, task_id: str, 
                            progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """等待处理任务完成"""
        try:
            start_time = time.time()
            timeout = self.processor_config["timeout"]
            
            while time.time() - start_time < timeout:
                # 检查任务状态
                status = self._check_task_status(task_id)
                
                if status["status"] == "completed":
                    return {
                        "success": True,
                        "result_path": status["result_path"],
                        "processing_time": status["processing_time"]
                    }
                elif status["status"] == "failed":
                    return {
                        "success": False,
                        "error": status.get("error", "Processing failed")
                    }
                elif status["status"] == "processing":
                    if progress_callback:
                        progress = 0.3 + status.get("progress", 0) * 0.6  # 30%-90%
                        progress_callback(progress, f"云端处理中... {status.get('progress', 0):.1%}")
                
                # 等待一段时间再检查
                time.sleep(5)
            
            return {"success": False, "error": "Processing timeout"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_task_status(self, task_id: str) -> Dict[str, Any]:
        """检查任务状态"""
        # 模拟API调用
        # 这里应该调用实际的云端API
        
        # 模拟处理进度
        elapsed = time.time() % 60  # 模拟60秒处理时间
        
        if elapsed < 50:
            return {
                "status": "processing",
                "progress": elapsed / 50,
                "message": "Processing video..."
            }
        else:
            return {
                "status": "completed",
                "result_path": f"results/{task_id}_result.json",
                "processing_time": 50.0
            }
    
    def _download_results(self, result_path: str) -> Dict[str, Any]:
        """下载处理结果"""
        try:
            local_path = f"./cloud_results/{Path(result_path).name}"
            return self.cloud_storage.download_file(result_path, local_path)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_processing_status(self, task_id: str) -> Dict[str, Any]:
        """获取处理状态"""
        return self._check_task_status(task_id)
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消处理任务"""
        try:
            # 模拟取消任务
            self.logger.info(f"Cancelling task: {task_id}")
            
            return {
                "success": True,
                "task_id": task_id,
                "message": "Task cancelled successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'cloud_storage'):
            self.cloud_storage.cleanup()
        self.logger.info("Cloud processor cleanup completed")


class CloudAPIManager:
    """云API管理器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化云API管理器

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="CloudAPIManager")

        # API配置
        self.api_config = self.config.get('cloud_api', {
            'providers': {
                'aws': {
                    'base_url': 'https://api.aws.amazon.com',
                    'access_key': '',
                    'secret_key': '',
                    'region': 'us-west-2'
                },
                'azure': {
                    'base_url': 'https://management.azure.com',
                    'subscription_id': '',
                    'client_id': '',
                    'client_secret': '',
                    'tenant_id': ''
                },
                'gcp': {
                    'base_url': 'https://googleapis.com',
                    'project_id': '',
                    'service_account_key': ''
                }
            },
            'timeout': 30,
            'retry_attempts': 3,
            'rate_limit': {
                'requests_per_minute': 60,
                'burst_limit': 10
            }
        })

        # API客户端
        self.clients = {}

        # 速率限制
        self.rate_limiter = RateLimiter(
            self.api_config['rate_limit']['requests_per_minute'],
            self.api_config['rate_limit']['burst_limit']
        )

        self.logger.info("Cloud API manager initialized")

    async def make_request(self, provider: str, endpoint: str, method: str = 'GET',
                          data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发起API请求

        Args:
            provider: 云服务提供商
            endpoint: API端点
            method: HTTP方法
            data: 请求数据
            headers: 请求头

        Returns:
            API响应
        """
        try:
            # 速率限制
            await self.rate_limiter.acquire()

            # 获取提供商配置
            provider_config = self.api_config['providers'].get(provider)
            if not provider_config:
                raise ValueError(f"Unknown provider: {provider}")

            # 构建URL
            base_url = provider_config['base_url']
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            # 准备认证头
            auth_headers = self._get_auth_headers(provider, provider_config)
            if headers:
                auth_headers.update(headers)

            # 发起请求
            timeout = aiohttp.ClientTimeout(total=self.api_config['timeout'])

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=auth_headers
                ) as response:
                    response_data = await response.json()

                    if response.status >= 400:
                        raise Exception(f"API request failed: {response.status} - {response_data}")

                    return {
                        'success': True,
                        'data': response_data,
                        'status_code': response.status,
                        'headers': dict(response.headers)
                    }

        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_auth_headers(self, provider: str, config: Dict[str, Any]) -> Dict[str, str]:
        """获取认证头"""
        headers = {}

        if provider == 'aws':
            # AWS签名认证
            headers['Authorization'] = self._generate_aws_signature(config)
        elif provider == 'azure':
            # Azure Bearer Token
            headers['Authorization'] = f"Bearer {self._get_azure_token(config)}"
        elif provider == 'gcp':
            # GCP Service Account
            headers['Authorization'] = f"Bearer {self._get_gcp_token(config)}"

        return headers

    def _generate_aws_signature(self, config: Dict[str, Any]) -> str:
        """生成AWS签名"""
        # 简化的AWS签名实现
        access_key = config['access_key']
        secret_key = config['secret_key']
        region = config['region']

        # 实际实现需要完整的AWS签名算法
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        signature = hashlib.sha256(f"{secret_key}{timestamp}".encode()).hexdigest()

        return f"AWS4-HMAC-SHA256 Credential={access_key}/{region}, Signature={signature}"

    def _get_azure_token(self, config: Dict[str, Any]) -> str:
        """获取Azure访问令牌"""
        # 简化的Azure令牌获取
        return "mock_azure_token"

    def _get_gcp_token(self, config: Dict[str, Any]) -> str:
        """获取GCP访问令牌"""
        # 简化的GCP令牌获取
        return "mock_gcp_token"


class RateLimiter:
    """速率限制器"""

    def __init__(self, requests_per_minute: int, burst_limit: int):
        """
        初始化速率限制器

        Args:
            requests_per_minute: 每分钟请求数
            burst_limit: 突发限制
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.tokens = burst_limit
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """获取令牌"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # 添加令牌
            tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.burst_limit, self.tokens + tokens_to_add)
            self.last_update = now

            # 检查是否有可用令牌
            if self.tokens >= 1:
                self.tokens -= 1
                return

            # 等待下一个令牌
            wait_time = (1 - self.tokens) / (self.requests_per_minute / 60.0)
            await asyncio.sleep(wait_time)
            self.tokens = 0


class CloudMonitoring:
    """云监控服务"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化云监控服务

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="CloudMonitoring")

        # 监控配置
        self.monitoring_config = self.config.get('cloud_monitoring', {
            'enabled': True,
            'metrics_interval': 60,  # 秒
            'log_retention_days': 30,
            'alert_thresholds': {
                'cpu_usage': 80,
                'memory_usage': 85,
                'disk_usage': 90,
                'error_rate': 5
            },
            'notification_channels': []
        })

        # 监控数据
        self.metrics_data = []
        self.alerts = []

        # 监控状态
        self.monitoring_active = False

        self.logger.info("Cloud monitoring service initialized")

    def start_monitoring(self):
        """开始监控"""
        try:
            if not self.monitoring_config['enabled']:
                self.logger.info("Monitoring is disabled")
                return

            self.monitoring_active = True

            # 启动监控任务
            asyncio.create_task(self._monitoring_loop())

            self.logger.info("Cloud monitoring started")

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")

    def stop_monitoring(self):
        """停止监控"""
        try:
            self.monitoring_active = False
            self.logger.info("Cloud monitoring stopped")

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")

    async def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集指标
                metrics = await self._collect_metrics()

                # 存储指标
                self._store_metrics(metrics)

                # 检查告警
                await self._check_alerts(metrics)

                # 等待下一次收集
                await asyncio.sleep(self.monitoring_config['metrics_interval'])

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # 错误时短暂等待

    async def _collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            import psutil

            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100

            # 网络统计
            network = psutil.net_io_counters()

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'disk_usage': disk_usage,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {}

    def _store_metrics(self, metrics: Dict[str, Any]):
        """存储指标数据"""
        try:
            self.metrics_data.append(metrics)

            # 限制数据量
            max_records = 24 * 60  # 24小时的分钟数
            if len(self.metrics_data) > max_records:
                self.metrics_data = self.metrics_data[-max_records:]

        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")

    async def _check_alerts(self, metrics: Dict[str, Any]):
        """检查告警条件"""
        try:
            thresholds = self.monitoring_config['alert_thresholds']

            # 检查CPU使用率
            if metrics.get('cpu_usage', 0) > thresholds['cpu_usage']:
                await self._trigger_alert('high_cpu_usage', metrics)

            # 检查内存使用率
            if metrics.get('memory_usage', 0) > thresholds['memory_usage']:
                await self._trigger_alert('high_memory_usage', metrics)

            # 检查磁盘使用率
            if metrics.get('disk_usage', 0) > thresholds['disk_usage']:
                await self._trigger_alert('high_disk_usage', metrics)

        except Exception as e:
            self.logger.error(f"Failed to check alerts: {e}")

    async def _trigger_alert(self, alert_type: str, metrics: Dict[str, Any]):
        """触发告警"""
        try:
            alert = {
                'type': alert_type,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'severity': 'warning'
            }

            self.alerts.append(alert)

            # 发送通知
            await self._send_notification(alert)

            self.logger.warning(f"Alert triggered: {alert_type}")

        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")

    async def _send_notification(self, alert: Dict[str, Any]):
        """发送通知"""
        try:
            channels = self.monitoring_config['notification_channels']

            for channel in channels:
                if channel['type'] == 'email':
                    await self._send_email_notification(channel, alert)
                elif channel['type'] == 'webhook':
                    await self._send_webhook_notification(channel, alert)

        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")

    async def _send_email_notification(self, channel: Dict[str, Any], alert: Dict[str, Any]):
        """发送邮件通知"""
        # 邮件通知实现
        self.logger.info(f"Email notification sent: {alert['type']}")

    async def _send_webhook_notification(self, channel: Dict[str, Any], alert: Dict[str, Any]):
        """发送Webhook通知"""
        # Webhook通知实现
        self.logger.info(f"Webhook notification sent: {alert['type']}")

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取指标摘要"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            # 过滤指定时间范围内的数据
            filtered_data = [
                m for m in self.metrics_data
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]

            if not filtered_data:
                return {}

            # 计算统计信息
            cpu_values = [m['cpu_usage'] for m in filtered_data if 'cpu_usage' in m]
            memory_values = [m['memory_usage'] for m in filtered_data if 'memory_usage' in m]
            disk_values = [m['disk_usage'] for m in filtered_data if 'disk_usage' in m]

            summary = {
                'time_range_hours': hours,
                'data_points': len(filtered_data),
                'cpu_usage': {
                    'avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    'max': max(cpu_values) if cpu_values else 0,
                    'min': min(cpu_values) if cpu_values else 0
                },
                'memory_usage': {
                    'avg': sum(memory_values) / len(memory_values) if memory_values else 0,
                    'max': max(memory_values) if memory_values else 0,
                    'min': min(memory_values) if memory_values else 0
                },
                'disk_usage': {
                    'avg': sum(disk_values) / len(disk_values) if disk_values else 0,
                    'max': max(disk_values) if disk_values else 0,
                    'min': min(disk_values) if disk_values else 0
                },
                'alerts_count': len([a for a in self.alerts
                                   if datetime.fromisoformat(a['timestamp']) > cutoff_time])
            }

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get metrics summary: {e}")
            return {}

    def cleanup(self):
        """清理资源"""
        try:
            self.stop_monitoring()
            self.metrics_data.clear()
            self.alerts.clear()
            self.logger.info("Cloud monitoring cleanup completed")
        except Exception as e:
            self.logger.error(f"Cloud monitoring cleanup failed: {e}")

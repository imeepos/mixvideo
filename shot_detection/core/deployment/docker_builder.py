"""
Docker Builder
Docker构建器
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class DockerConfig:
    """Docker配置"""
    
    def __init__(self):
        """初始化Docker配置"""
        self.image_name = "shot-detection"
        self.image_tag = "latest"
        self.base_image = "python:3.9-slim"
        self.working_dir = "/app"
        self.expose_port = 8080
        self.include_gui = False
        self.optimize_size = True
        self.multi_stage_build = True
        self.health_check = True
        self.user_id = 1000
        self.group_id = 1000


class DockerBuilder:
    """Docker构建器"""
    
    def __init__(self, config: Optional[DockerConfig] = None):
        """
        初始化Docker构建器
        
        Args:
            config: Docker配置
        """
        self.config = config or DockerConfig()
        self.logger = logger.bind(component="DockerBuilder")
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        
        # 构建目录
        self.build_dir = self.project_root / "docker_build"
        
        self.logger.info("Docker builder initialized")
    
    def build_image(self, tag: Optional[str] = None) -> bool:
        """
        构建Docker镜像
        
        Args:
            tag: 镜像标签
            
        Returns:
            是否构建成功
        """
        try:
            image_tag = tag or f"{self.config.image_name}:{self.config.image_tag}"
            
            self.logger.info(f"Building Docker image: {image_tag}")
            
            # 准备构建环境
            self._prepare_build_context()
            
            # 生成Dockerfile
            dockerfile = self._generate_dockerfile()
            
            # 构建镜像
            result = subprocess.run([
                "docker", "build",
                "-t", image_tag,
                "-f", str(dockerfile),
                str(self.build_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Docker image built successfully: {image_tag}")
                return True
            else:
                self.logger.error(f"Docker build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to build Docker image: {e}")
            return False
    
    def build_multi_arch_image(self, platforms: List[str] = None) -> bool:
        """
        构建多架构镜像
        
        Args:
            platforms: 目标平台列表
            
        Returns:
            是否构建成功
        """
        try:
            if platforms is None:
                platforms = ["linux/amd64", "linux/arm64"]
            
            image_tag = f"{self.config.image_name}:{self.config.image_tag}"
            
            self.logger.info(f"Building multi-arch Docker image: {image_tag}")
            
            # 准备构建环境
            self._prepare_build_context()
            
            # 生成Dockerfile
            dockerfile = self._generate_dockerfile()
            
            # 创建buildx builder
            builder_name = "shot-detection-builder"
            subprocess.run([
                "docker", "buildx", "create",
                "--name", builder_name,
                "--use"
            ], capture_output=True)
            
            # 构建多架构镜像
            platform_str = ",".join(platforms)
            result = subprocess.run([
                "docker", "buildx", "build",
                "--platform", platform_str,
                "-t", image_tag,
                "-f", str(dockerfile),
                "--push",
                str(self.build_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Multi-arch Docker image built successfully: {image_tag}")
                return True
            else:
                self.logger.error(f"Multi-arch Docker build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to build multi-arch Docker image: {e}")
            return False
    
    def create_docker_compose(self) -> bool:
        """
        创建Docker Compose配置
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating Docker Compose configuration")
            
            compose_content = self._generate_docker_compose()
            
            compose_file = self.project_root / "docker-compose.yml"
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(compose_content)
            
            self.logger.info("Docker Compose configuration created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Docker Compose configuration: {e}")
            return False
    
    def _prepare_build_context(self):
        """准备构建上下文"""
        try:
            # 清理并创建构建目录
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True)
            
            # 复制应用文件
            source_dir = self.project_root / "shot_detection"
            if source_dir.exists():
                shutil.copytree(source_dir, self.build_dir / "shot_detection")
            
            # 复制其他必要文件
            for file_name in ["requirements.txt", "README.md", "LICENSE"]:
                source_file = self.project_root / file_name
                if source_file.exists():
                    shutil.copy2(source_file, self.build_dir)
            
            # 创建入口脚本
            self._create_entrypoint_script()
            
            self.logger.debug("Build context prepared")
            
        except Exception as e:
            self.logger.error(f"Failed to prepare build context: {e}")
    
    def _generate_dockerfile(self) -> Path:
        """生成Dockerfile"""
        try:
            if self.config.multi_stage_build:
                dockerfile_content = self._generate_multi_stage_dockerfile()
            else:
                dockerfile_content = self._generate_simple_dockerfile()
            
            dockerfile = self.build_dir / "Dockerfile"
            with open(dockerfile, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            
            self.logger.debug("Dockerfile generated")
            return dockerfile
            
        except Exception as e:
            self.logger.error(f"Failed to generate Dockerfile: {e}")
            return Path("Dockerfile")
    
    def _generate_simple_dockerfile(self) -> str:
        """生成简单Dockerfile"""
        return f'''FROM {self.config.base_image}

# 设置工作目录
WORKDIR {self.config.working_dir}

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    libopencv-dev \\
    python3-opencv \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY shot_detection/ ./shot_detection/
COPY entrypoint.sh .

# 创建非root用户
RUN groupadd -g {self.config.group_id} appgroup && \\
    useradd -u {self.config.user_id} -g appgroup -m appuser

# 设置权限
RUN chown -R appuser:appgroup {self.config.working_dir}
RUN chmod +x entrypoint.sh

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE {self.config.expose_port}

# 健康检查
{"HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c \\"import shot_detection; print('OK')\\"" if self.config.health_check else ""}

# 入口点
ENTRYPOINT ["./entrypoint.sh"]
CMD ["--help"]
'''
    
    def _generate_multi_stage_dockerfile(self) -> str:
        """生成多阶段Dockerfile"""
        return f'''# 构建阶段
FROM {self.config.base_image} as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y \\
    build-essential \\
    libopencv-dev \\
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖到临时目录
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM {self.config.base_image}

# 设置工作目录
WORKDIR {self.config.working_dir}

# 安装运行时依赖
RUN apt-get update && apt-get install -y \\
    libopencv-dev \\
    python3-opencv \\
    ffmpeg \\
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=builder /root/.local /root/.local

# 复制应用代码
COPY shot_detection/ ./shot_detection/
COPY entrypoint.sh .

# 创建非root用户
RUN groupadd -g {self.config.group_id} appgroup && \\
    useradd -u {self.config.user_id} -g appgroup -m appuser

# 设置权限
RUN chown -R appuser:appgroup {self.config.working_dir}
RUN chmod +x entrypoint.sh

# 切换到非root用户
USER appuser

# 确保用户可以访问Python包
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.9/site-packages:$PYTHONPATH

# 暴露端口
EXPOSE {self.config.expose_port}

# 健康检查
{"HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c \\"import shot_detection; print('OK')\\"" if self.config.health_check else ""}

# 入口点
ENTRYPOINT ["./entrypoint.sh"]
CMD ["--help"]
'''
    
    def _create_entrypoint_script(self):
        """创建入口脚本"""
        try:
            entrypoint_content = '''#!/bin/bash
set -e

# 初始化应用
echo "Starting Shot Detection..."

# 检查环境变量
if [ -n "$SHOT_DETECTION_CONFIG" ]; then
    echo "Using config: $SHOT_DETECTION_CONFIG"
fi

# 运行应用
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    python -m shot_detection.cli --help
elif [ "$1" = "--version" ] || [ "$1" = "-v" ]; then
    python -c "import shot_detection; print(shot_detection.__version__)"
elif [ "$1" = "server" ]; then
    echo "Starting web server..."
    python -m shot_detection.web.app --host 0.0.0.0 --port 8080
elif [ "$1" = "gui" ]; then
    echo "Starting GUI..."
    python -m shot_detection.gui.main
else
    # 传递所有参数给CLI
    python -m shot_detection.cli "$@"
fi
'''
            
            entrypoint_file = self.build_dir / "entrypoint.sh"
            with open(entrypoint_file, 'w', encoding='utf-8') as f:
                f.write(entrypoint_content)
            
            # 设置执行权限
            entrypoint_file.chmod(0o755)
            
            self.logger.debug("Entrypoint script created")
            
        except Exception as e:
            self.logger.error(f"Failed to create entrypoint script: {e}")
    
    def _generate_docker_compose(self) -> str:
        """生成Docker Compose配置"""
        return f'''version: '3.8'

services:
  shot-detection:
    image: {self.config.image_name}:{self.config.image_tag}
    container_name: shot-detection-app
    ports:
      - "{self.config.expose_port}:{self.config.expose_port}"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./config:/app/config
    environment:
      - SHOT_DETECTION_CONFIG=/app/config/config.yaml
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    {"user: \"${self.config.user_id}:${self.config.group_id}\"" if self.config.user_id != 0 else ""}
    
  # 可选：添加数据库服务
  # redis:
  #   image: redis:alpine
  #   container_name: shot-detection-redis
  #   ports:
  #     - "6379:6379"
  #   volumes:
  #     - redis_data:/data
  #   restart: unless-stopped

volumes:
  # redis_data:
  data:
  output:
  config:

networks:
  default:
    name: shot-detection-network
'''
    
    def push_image(self, registry: str = "", tag: Optional[str] = None) -> bool:
        """
        推送镜像到仓库
        
        Args:
            registry: 镜像仓库地址
            tag: 镜像标签
            
        Returns:
            是否推送成功
        """
        try:
            image_tag = tag or f"{self.config.image_name}:{self.config.image_tag}"
            
            if registry:
                full_tag = f"{registry}/{image_tag}"
                
                # 标记镜像
                subprocess.run([
                    "docker", "tag", image_tag, full_tag
                ], check=True)
                
                image_tag = full_tag
            
            self.logger.info(f"Pushing Docker image: {image_tag}")
            
            # 推送镜像
            result = subprocess.run([
                "docker", "push", image_tag
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Docker image pushed successfully: {image_tag}")
                return True
            else:
                self.logger.error(f"Docker push failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to push Docker image: {e}")
            return False
    
    def create_kubernetes_manifests(self) -> bool:
        """
        创建Kubernetes部署清单
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating Kubernetes manifests")
            
            k8s_dir = self.project_root / "k8s"
            k8s_dir.mkdir(exist_ok=True)
            
            # 创建Deployment
            deployment_content = self._generate_k8s_deployment()
            with open(k8s_dir / "deployment.yaml", 'w') as f:
                f.write(deployment_content)
            
            # 创建Service
            service_content = self._generate_k8s_service()
            with open(k8s_dir / "service.yaml", 'w') as f:
                f.write(service_content)
            
            # 创建ConfigMap
            configmap_content = self._generate_k8s_configmap()
            with open(k8s_dir / "configmap.yaml", 'w') as f:
                f.write(configmap_content)
            
            self.logger.info("Kubernetes manifests created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Kubernetes manifests: {e}")
            return False
    
    def _generate_k8s_deployment(self) -> str:
        """生成Kubernetes Deployment"""
        return f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: shot-detection
  labels:
    app: shot-detection
spec:
  replicas: 1
  selector:
    matchLabels:
      app: shot-detection
  template:
    metadata:
      labels:
        app: shot-detection
    spec:
      containers:
      - name: shot-detection
        image: {self.config.image_name}:{self.config.image_tag}
        ports:
        - containerPort: {self.config.expose_port}
        env:
        - name: SHOT_DETECTION_CONFIG
          value: "/app/config/config.yaml"
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        - name: output
          mountPath: /app/output
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import shot_detection; print('OK')"
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import shot_detection; print('OK')"
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: shot-detection-config
      - name: data
        persistentVolumeClaim:
          claimName: shot-detection-data
      - name: output
        persistentVolumeClaim:
          claimName: shot-detection-output
'''
    
    def _generate_k8s_service(self) -> str:
        """生成Kubernetes Service"""
        return f'''apiVersion: v1
kind: Service
metadata:
  name: shot-detection-service
  labels:
    app: shot-detection
spec:
  selector:
    app: shot-detection
  ports:
  - protocol: TCP
    port: 80
    targetPort: {self.config.expose_port}
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: shot-detection-nodeport
  labels:
    app: shot-detection
spec:
  selector:
    app: shot-detection
  ports:
  - protocol: TCP
    port: 80
    targetPort: {self.config.expose_port}
    nodePort: 30080
  type: NodePort
'''
    
    def _generate_k8s_configmap(self) -> str:
        """生成Kubernetes ConfigMap"""
        return '''apiVersion: v1
kind: ConfigMap
metadata:
  name: shot-detection-config
data:
  config.yaml: |
    app:
      name: "Shot Detection"
      version: "2.0.0"
      debug: false
    
    detection:
      default_algorithm: "frame_difference"
      threshold: 0.5
      min_shot_duration: 1.0
    
    processing:
      max_workers: 4
      chunk_size: 1000
    
    logging:
      level: "INFO"
      format: "json"
'''
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            
            self.logger.info("Docker builder cleanup completed")
        except Exception as e:
            self.logger.error(f"Docker builder cleanup failed: {e}")

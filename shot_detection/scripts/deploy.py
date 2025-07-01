#!/usr/bin/env python3
"""
Shot Detection v2.0 Deployment Script
部署脚本
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, List

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent


def run_command(cmd: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令"""
    print(f"🔧 Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd or ROOT_DIR, check=check, capture_output=True, text=True)


def deploy_local():
    """本地部署"""
    print("🏠 Deploying locally...")
    
    try:
        # 安装包
        run_command([sys.executable, "-m", "pip", "install", "-e", "."])
        
        # 创建配置目录
        config_dir = Path.home() / ".shot_detection"
        config_dir.mkdir(exist_ok=True)
        
        # 复制配置文件
        config_file = ROOT_DIR / "config_v2.yaml"
        if config_file.exists():
            import shutil
            shutil.copy2(config_file, config_dir / "config_v2.yaml")
        
        print("✅ Local deployment completed")
        print(f"📁 Configuration directory: {config_dir}")
        print("🚀 Run 'shot-detection --help' to get started")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Local deployment failed: {e}")
        return False


def deploy_docker():
    """Docker部署"""
    print("🐳 Deploying with Docker...")
    
    try:
        # 构建镜像
        run_command(["docker", "build", "-t", "shot-detection:latest", "."])
        
        # 创建数据目录
        data_dirs = ["data", "output", "config", "logs"]
        for dir_name in data_dirs:
            dir_path = ROOT_DIR / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # 启动容器
        run_command([
            "docker", "run", "-d",
            "--name", "shot-detection",
            "-p", "8000:8000",
            "-v", f"{ROOT_DIR}/data:/home/app/data",
            "-v", f"{ROOT_DIR}/output:/home/app/output",
            "-v", f"{ROOT_DIR}/config:/home/app/.shot_detection",
            "-v", f"{ROOT_DIR}/logs:/home/app/.shot_detection/logs",
            "shot-detection:latest"
        ])
        
        print("✅ Docker deployment completed")
        print("🌐 Application available at: http://localhost:8000")
        print("📊 Check status: docker ps")
        print("📝 View logs: docker logs shot-detection")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker deployment failed: {e}")
        return False


def deploy_docker_compose():
    """Docker Compose部署"""
    print("🐳 Deploying with Docker Compose...")
    
    try:
        # 检查docker-compose文件
        compose_file = ROOT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            print("❌ docker-compose.yml not found")
            return False
        
        # 创建必要目录
        dirs_to_create = [
            "data", "output", "config", "logs",
            "monitoring", "nginx", "scripts"
        ]
        
        for dir_name in dirs_to_create:
            dir_path = ROOT_DIR / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # 启动服务
        run_command(["docker-compose", "up", "-d"])
        
        # 等待服务启动
        import time
        print("⏳ Waiting for services to start...")
        time.sleep(10)
        
        # 检查服务状态
        result = run_command(["docker-compose", "ps"])
        print("\n📊 Service status:")
        print(result.stdout)
        
        print("✅ Docker Compose deployment completed")
        print("🌐 Application: http://localhost")
        print("📊 Monitoring: http://localhost:3000 (Grafana)")
        print("🔍 Metrics: http://localhost:9090 (Prometheus)")
        print("🌸 Task Monitor: http://localhost:5555 (Flower)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker Compose deployment failed: {e}")
        return False


def deploy_kubernetes():
    """Kubernetes部署"""
    print("☸️ Deploying to Kubernetes...")
    
    try:
        # 检查kubectl
        run_command(["kubectl", "version", "--client"])
        
        # 创建命名空间
        namespace_yaml = """
apiVersion: v1
kind: Namespace
metadata:
  name: shot-detection
"""
        
        # 创建部署配置
        deployment_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shot-detection
  namespace: shot-detection
spec:
  replicas: 3
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
        image: shot-detection:latest
        ports:
        - containerPort: 8000
        env:
        - name: SHOT_DETECTION_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: shot-detection-service
  namespace: shot-detection
spec:
  selector:
    app: shot-detection
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""
        
        # 保存配置文件
        k8s_dir = ROOT_DIR / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        with open(k8s_dir / "namespace.yaml", "w") as f:
            f.write(namespace_yaml)
        
        with open(k8s_dir / "deployment.yaml", "w") as f:
            f.write(deployment_yaml)
        
        # 应用配置
        run_command(["kubectl", "apply", "-f", str(k8s_dir / "namespace.yaml")])
        run_command(["kubectl", "apply", "-f", str(k8s_dir / "deployment.yaml")])
        
        print("✅ Kubernetes deployment completed")
        print("📊 Check status: kubectl get pods -n shot-detection")
        print("🌐 Get service URL: kubectl get svc -n shot-detection")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Kubernetes deployment failed: {e}")
        return False


def deploy_cloud_aws():
    """AWS云部署"""
    print("☁️ Deploying to AWS...")
    
    try:
        # 检查AWS CLI
        run_command(["aws", "--version"])
        
        # 创建ECR仓库
        try:
            run_command([
                "aws", "ecr", "create-repository",
                "--repository-name", "shot-detection",
                "--region", "us-west-2"
            ])
        except subprocess.CalledProcessError:
            print("ℹ️ ECR repository already exists")
        
        # 获取登录令牌
        result = run_command([
            "aws", "ecr", "get-login-password",
            "--region", "us-west-2"
        ])
        
        login_token = result.stdout.strip()
        
        # 登录到ECR
        run_command([
            "docker", "login",
            "--username", "AWS",
            "--password-stdin",
            "123456789012.dkr.ecr.us-west-2.amazonaws.com"
        ], input=login_token)
        
        # 标记和推送镜像
        run_command([
            "docker", "tag",
            "shot-detection:latest",
            "123456789012.dkr.ecr.us-west-2.amazonaws.com/shot-detection:latest"
        ])
        
        run_command([
            "docker", "push",
            "123456789012.dkr.ecr.us-west-2.amazonaws.com/shot-detection:latest"
        ])
        
        print("✅ AWS deployment completed")
        print("🌐 Image pushed to ECR")
        print("📋 Next: Deploy to ECS/EKS using the pushed image")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ AWS deployment failed: {e}")
        return False


def create_systemd_service():
    """创建systemd服务"""
    print("🔧 Creating systemd service...")
    
    service_content = f"""[Unit]
Description=Shot Detection v2.0 Service
After=network.target

[Service]
Type=simple
User=shot-detection
Group=shot-detection
WorkingDirectory={ROOT_DIR}
Environment=SHOT_DETECTION_ENV=production
ExecStart={sys.executable} {ROOT_DIR}/main_v2.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/shot-detection.service")
    
    try:
        # 需要root权限
        with open(service_file, "w") as f:
            f.write(service_content)
        
        # 重新加载systemd
        run_command(["sudo", "systemctl", "daemon-reload"])
        run_command(["sudo", "systemctl", "enable", "shot-detection"])
        
        print("✅ Systemd service created")
        print("🚀 Start service: sudo systemctl start shot-detection")
        print("📊 Check status: sudo systemctl status shot-detection")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create systemd service: {e}")
        return False


def health_check(url: str = "http://localhost:8000/health"):
    """健康检查"""
    print(f"🏥 Performing health check: {url}")
    
    try:
        import urllib.request
        import urllib.error
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status}")
                return False
                
    except urllib.error.URLError as e:
        print(f"❌ Health check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Shot Detection v2.0 Deployment Script")
    parser.add_argument("--local", action="store_true", help="Deploy locally")
    parser.add_argument("--docker", action="store_true", help="Deploy with Docker")
    parser.add_argument("--compose", action="store_true", help="Deploy with Docker Compose")
    parser.add_argument("--k8s", action="store_true", help="Deploy to Kubernetes")
    parser.add_argument("--aws", action="store_true", help="Deploy to AWS")
    parser.add_argument("--systemd", action="store_true", help="Create systemd service")
    parser.add_argument("--health-check", type=str, help="Perform health check")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 Shot Detection v2.0 Deployment Script")
    print("=" * 50)
    
    success = True
    
    try:
        if args.local:
            success &= deploy_local()
        
        if args.docker:
            success &= deploy_docker()
        
        if args.compose:
            success &= deploy_docker_compose()
        
        if args.k8s:
            success &= deploy_kubernetes()
        
        if args.aws:
            success &= deploy_cloud_aws()
        
        if args.systemd:
            success &= create_systemd_service()
        
        if args.health_check:
            success &= health_check(args.health_check)
        
        if success:
            print("\n🎉 Deployment completed successfully!")
        else:
            print("\n❌ Deployment completed with errors!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Shot Detection v2.0 Docker Image
# 多阶段构建，优化镜像大小

# 构建阶段
FROM python:3.10-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements-optional.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 升级pip并安装依赖
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
RUN pip install -r requirements-optional.txt

# 运行阶段
FROM python:3.10-slim as runtime

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 创建应用用户
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# 复制应用代码
COPY --chown=app:app . /home/app/shot_detection/

# 设置Python路径
ENV PYTHONPATH="/home/app/shot_detection:$PYTHONPATH"

# 创建必要目录
RUN mkdir -p /home/app/.shot_detection/{logs,cache,models,temp}

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import shot_detection; print('OK')" || exit 1

# 默认命令
CMD ["python", "/home/app/shot_detection/main_v2.py", "--help"]

# 标签
LABEL maintainer="Shot Detection Team <team@shotdetection.com>"
LABEL version="2.0.0"
LABEL description="Advanced video shot boundary detection system"
LABEL org.opencontainers.image.source="https://github.com/shotdetection/shotdetection"

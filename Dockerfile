# 使用Python 3.11 slim镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --no-cache-dir --upgrade pip

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码并设置权限
COPY . .
RUN mkdir -p /app/logs && \
    groupadd -r ddns && useradd -r -g ddns ddns && \
    chown -R ddns:ddns /app

# 切换到非root用户
USER ddns

# 暴露端口
EXPOSE 4646

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:4646/api/status', timeout=5)" || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:4646", "--workers", "2", "--timeout", "60", "--max-requests", "1000", "--max-requests-jitter", "50", "app:app"]
#!/bin/bash

# EdgeOne DDNS 部署脚本

set -e

echo "🚀 开始部署 EdgeOne DDNS 系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs

# 检查配置文件是否存在
if [ ! -f "config.json" ]; then
    echo "⚠️  配置文件 config.json 不存在，将创建示例配置文件..."
    cat > config.json << EOF
{
  "secret_id": "",
  "secret_key": "",
  "zone_id": "",
  "domains": [],
  "wechat_webhook": "",
  "update_interval": 300,
  "log_level": "INFO"
}
EOF
    echo "✅ 已创建示例配置文件，请编辑 config.json 填入正确的配置信息"
fi

# 构建Docker镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:4646/api/status &> /dev/null; then
    echo "✅ 服务启动成功！"
    echo "📱 Web管理界面: http://localhost:4646"
    echo "📝 配置文件: config.json"
    echo "📋 查看日志: docker-compose logs -f edgeone-ddns"
    echo ""
    echo "ℹ️  网络模式: bridge with IPv6 support"
    echo "ℹ️  容器已启用 IPv6 支持，能够正确检测和更新 IPv6 DNS 记录"
else
    echo "❌ 服务启动失败，请检查日志:"
    docker-compose logs edgeone-ddns
    exit 1
fi

echo "🎉 部署完成！请访问 http://localhost:4646 进行配置"
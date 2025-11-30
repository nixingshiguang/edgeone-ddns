@echo off
chcp 65001
setlocal enabledelayedexpansion

echo 🚀 开始部署 EdgeOne DDNS 系统...

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "logs" mkdir logs

REM 检查配置文件是否存在
if not exist "config.json" (
    echo ⚠️  配置文件 config.json 不存在，将创建示例配置文件...
    (
        echo {
        echo   "secret_id": "",
        echo   "secret_key": "",
        echo   "zone_id": "",
        echo   "domains": [],
        echo   "wechat_webhook": "",
        echo   "update_interval": 300,
        echo   "log_level": "INFO"
        echo }
    ) > config.json
    echo ✅ 已创建示例配置文件，请编辑 config.json 填入正确的配置信息
)

REM 构建Docker镜像
echo 🔨 构建 Docker 镜像...
docker-compose build
if errorlevel 1 (
    echo ❌ 镜像构建失败
    pause
    exit /b 1
)

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
curl -f http://localhost:4646/api/status >nul 2>&1
if errorlevel 1 (
    echo ❌ 服务启动失败，请检查日志:
    docker-compose logs edgeone-ddns
    pause
    exit /b 1
)

echo ✅ 服务启动成功！
echo 📱 Web管理界面: http://localhost:4646
echo 📝 配置文件: config.json
echo 📋 查看日志: docker-compose logs -f edgeone-ddns
echo.
echo ℹ️  网络模式: bridge with IPv6 support
echo ℹ️  容器已启用 IPv6 支持，能够正确检测和更新 IPv6 DNS 记录
echo.
echo 🎉 部署完成！请访问 http://localhost:4646 进行配置
pause
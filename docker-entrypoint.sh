#!/bin/sh
# Docker容器入口脚本
# 处理配置文件和目录权限问题

set -e

echo "初始化容器环境..."

# 获取ddns用户的UID和GID（如果需要的话，可以在docker-compose中覆盖）
USER_ID=${UID:-999}
GROUP_ID=${GID:-999}

# 确保日志目录存在且有正确权限
mkdir -p /app/logs
chown -R ${USER_ID}:${GROUP_ID} /app/logs
chmod -R 755 /app/logs
echo "日志目录权限设置完成"

# 处理配置文件 - 在配置目录中创建配置文件
CONFIG_DIR="/app/config"
CONFIG_FILE="$CONFIG_DIR/config.json"

# 确保配置目录存在
mkdir -p "$CONFIG_DIR"
chown ${USER_ID}:${GROUP_ID} "$CONFIG_DIR"
chmod 755 "$CONFIG_DIR"

# 创建或更新配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "创建配置文件..."
    touch "$CONFIG_FILE"
    chown ${USER_ID}:${GROUP_ID} "$CONFIG_FILE"
    chmod 664 "$CONFIG_FILE"
    echo "{}" > "$CONFIG_FILE"
    echo "空配置文件创建完成: $CONFIG_FILE"
else
    echo "配置文件已存在，设置权限: $CONFIG_FILE"
    chown ${USER_ID}:${GROUP_ID} "$CONFIG_FILE"
    chmod 664 "$CONFIG_FILE"
fi

# 创建环境变量，告诉应用配置文件的真正位置
export CONFIG_FILE_PATH="$CONFIG_FILE"
echo "export CONFIG_FILE_PATH='$CONFIG_FILE'" >> /etc/profile.d/config.sh

echo "容器环境初始化完成"
echo "配置文件: $CONFIG_FILE"
echo "日志目录: /app/logs"

# 使用gosu切换到ddns用户并执行CMD命令
echo "切换到ddns用户并启动应用..."
exec gosu ${USER_ID}:${GROUP_ID} "$@"
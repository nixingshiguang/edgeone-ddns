# EdgeOne DDNS 动态域名解析系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com/)

基于 Python + Docker 的腾讯云 EdgeOne 动态域名解析系统，提供现代化的 Web 管理界面，支持 IPv4/IPv6 双栈解析和自定义 Webhook 通知。

**声明：** 本项目由AI生成，很多内容没有经过人工校对，但是已测试，可以正常使用。

## ✨ 核心特性

- 🌐 **双栈解析**: 同时支持 IPv4 (A记录) 和 IPv6 (AAAA记录) 动态解析
- 🔄 **灵活配置**: 可独立启用/禁用 IPv4 或 IPv6，支持不启用 DDNS 的监控模式
- 🎯 **分离域名**: IPv4 和 IPv6 可配置不同的域名列表，满足复杂部署需求
- 🔔 **自定义通知**: 支持自定义 Webhook 通知，兼容钉钉、飞书、企业微信等所有服务
- 🌍 **多源IP检测**: 内置11个公网IP检测服务，支持自定义检测端点
- 🖥️ **现代化界面**: 基于 Bootstrap 5 的响应式 Web 管理界面
- 📊 **实时监控**: 实时状态显示、详细日志记录和系统健康检查
- 🐳 **容器化部署**: 完整的 Docker 和 Docker Compose 支持
- 🔒 **安全可靠**: 使用非 root 用户运行，支持 API 密钥加密存储
- ⚡ **高性能**: 异步处理，资源占用极低，适合长期运行

## 🏗️ 系统架构

```
EdgeOne DDNS System
├── app.py                 # Flask 主应用程序和 Web API
├── config.py              # 配置管理模块，支持动态配置
├── edgeone_client.py       # EdgeOne API 客户端，支持 A/AAAA 记录
├── ip_detector.py         # 公网IP检测模块，IPv4/IPv6 双栈支持
├── notification.py        # 自定义 Webhook 通知模块
├── ddns_service.py        # DDNS 服务核心模块，支持分离域名
├── templates/              # Web 界面模板（Bootstrap 5）
│   ├── index.html         # 仪表板页面
│   ├── config.html        # 配置管理页面
│   └── logs.html          # 日志查看页面
├── static/                 # 静态资源文件
│   ├── css/               # 样式文件
│   └── js/                # JavaScript 文件
├── logs/                   # 日志文件目录
├── config.json             # 配置文件（可选，Web界面可自动创建）
├── docker-entrypoint.sh    # Docker 容器入口脚本
├── requirements.txt        # Python 依赖
├── Dockerfile             # Docker 容器配置
├── docker-compose.yml      # Docker Compose 配置
└── README.md              # 项目文档
```

## 🚀 快速开始

### 方式一：Docker Compose 部署（推荐）

```bash
services:
  edgeone-ddns:
    image: edgeone-ddns
    container_name: nixingshiguang/edgeone-ddns
    volumes:
      - ddns-config:/app/config.json
      - ddns-logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - TZ=Asia/Shanghai
    network_mode: host #需要解析ipv6的必须使用host模式
    healthcheck:
      test:
        - CMD
        - curl
        - -f
        - http://localhost:4646/api/status
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
volumes:
  ddns-config:
    driver: local
  ddns-logs:
    driver: local
```

### 方式二：命令行部署脚本

#### Windows 用户
```bash
git clone https://github.com/your-username/ddns-for-edgeone.git
cd ddns-for-edgeone
deploy.bat
```

#### Linux/Mac 用户
```bash
git clone https://github.com/your-username/ddns-for-edgeone.git
cd ddns-for-edgeone
chmod +x deploy.sh
./deploy.sh
```

### 方式三：手动 Docker 部署
```bash
# 1. 构建镜像
docker build -t edgeone-ddns .

# 2. 运行容器（使用 Docker 托管卷）
docker run -d \
  --name edgeone-ddns \
  --network host \
  -v ddns-config:/app/config \
  -v ddns-logs:/app/logs \
  --restart unless-stopped \
  edgeone-ddns

# 3. 访问 Web 界面进行配置
# 浏览器打开：http://localhost:4646

# 注意：
# - 使用 Docker 托管卷自动管理配置和日志存储
# - 配置文件通过 Web 界面创建和保存
# - 无需手动挂载配置文件或担心权限问题
```

### 方式四：本地开发部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/ddns-for-edgeone.git
cd ddns-for-edgeone

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建日志目录
mkdir -p logs

# 5. 运行应用
python app.py
```

### 🎯 首次配置

1. 访问 `http://localhost:4646`
2. 进入 **配置管理** 页面
3. 填写腾讯云 API 凭证和 EdgeOne 站点信息
4. 配置 IPv4/IPv6 设置和域名列表
5. 设置自定义 Webhook 通知（可选）
6. 保存配置并测试连接

**重要提示**：
- 🔧 **Docker 部署**：配置文件通过 Web 界面自动创建和保存
- 🔧 **权限管理**：使用 Docker 托管卷和容器内权限管理，无需手动设置权限
- 🔧 **数据持久化**：配置和日志数据通过 Docker 托管卷持久化存储

## ⚙️ 配置详解

### 基础配置

访问 `http://localhost:4646/config` 进行配置：

#### 腾讯云 API 配置
- **Secret ID**: 腾讯云访问管理 API 的 Secret ID
- **Secret Key**: 腾讯云访问管理 API 的 Secret Key  
- **站点ID**: EdgeOne 站点 ID（格式：zone-xxxxxxxx）

#### IPv4/IPv6 配置
- **启用 IPv4**: 开启/关闭 IPv4 动态解析
- **启用 IPv6**: 开启/关闭 IPv6 动态解析
- **IPv4 域名列表**: IPv4 解析的域名（每行一个）
- **IPv6 域名列表**: IPv6 解析的域名（每行一个）
- **IPv4 检测端点**: 自定义 IPv4 IP 检测 URL（可选）
- **IPv6 检测端点**: 自定义 IPv6 IP 检测 URL（可选）

#### 通知配置
- **启用通知**: 开启/关闭 Webhook 通知
- **Webhook URL**: 通知接收地址
- **请求方法**: GET/POST/PUT 方法选择
- **请求头**: JSON 格式的请求头配置
- **请求体**: 支持模板变量的请求体内容

#### 高级配置
- **检查间隔**: IP 检查间隔（秒）
- **超时时间**: 网络请求超时时间
- **重试次数**: 失败重试次数

### API 密钥权限要求

确保你的腾讯云 API 密钥具有以下 EdgeOne 权限：
- 云解析 DNS 全读写访问权限
- 边缘安全加速平台 EO 全读写访问权限边缘安全加速平台 EO 全读写访问权限


## 📱 Web 界面功能

### 🏠 仪表板
- **实时状态**: IPv4/IPv6 地址显示，连接状态监控
- **统计信息**: 域名数量、最后更新时间、更新频率
- **快速操作**: 手动更新、测试连接、清空日志
- **日志预览**: 最近 20 条日志记录实时显示

### ⚙️ 配置管理
- **基础设置**: 腾讯云 API 凭证、站点 ID 配置
- **双栈配置**: IPv4/IPv6 独立开关和域名列表管理
- **IP 检测**: 内置 11 个检测服务，支持自定义端点
- **通知设置**: 自定义 Webhook 配置，支持模板变量
- **实时验证**: 配置保存前自动验证连接和权限

### 📊 系统日志
- **分类显示**: INFO/WARNING/ERROR 级别筛选
- **搜索功能**: 关键词快速搜索定位
- **详细查看**: 日志详情弹窗显示
- **管理操作**: 日志导出、清空等管理功能

## 🔧 RESTful API

### 系统信息
```http
GET /api/status
# 返回: 当前IP、域名数量、最后更新时间等
```

### 配置管理
```http
GET    /api/config              # 获取当前配置
POST   /api/config              # 更新配置
POST   /api/test_connectivity   # 测试连接和权限
```

### DDNS 操作
```http
POST   /api/manual_update       # 手动触发DDNS更新
GET    /api/last_ips            # 获取上次记录的IP地址
```

### 通知功能
```http
POST   /api/test_notification   # 测试Webhook通知
```

### 日志管理
```http
GET    /api/logs               # 获取日志列表
DELETE /api/logs/clear         # 清空日志文件
```

### IP 检测
```http
GET    /api/detect_ip          # 手动检测当前公网IP
```

#### API 响应示例
```json
{
  "success": true,
  "data": {
    "current_ipv4": "203.0.113.1",
    "current_ipv6": "2001:db8::1",
    "last_update": "2024-11-29T10:30:00Z",
    "total_domains": 5
  },
  "message": "操作成功"
}
```

## 📋 部署要求

### 系统要求
- **操作系统**: Linux (Ubuntu 18.04+, CentOS 7+) / Windows 10+ / macOS 10.15+
- **运行环境**: Docker 20.10+ 或 Python 3.8+
- **架构**: 64位操作系统 (x86_64 / ARM64)
- **内存**: 最小 128MB，推荐 256MB
- **存储**: 最小 100MB，推荐 500MB
- **网络**: 稳定的互联网连接

### 网络要求
- ✅ 必须能访问腾讯云 API (`cloud.tencent.com`)
- ✅ 必须能访问公网 IP 检测服务（系统内置11个备用）
- ✅ 如使用 Webhook 通知，需能访问对应服务
- ✅ 防火墙允许 4646 端口出站（API调用）

## 🐳 Docker 配置详解

### 托管卷管理
本项目使用 Docker 托管卷（Docker Managed Volumes）来管理配置和日志数据：

```yaml
volumes:
  ddns-config:    # 配置数据存储
    driver: local
  ddns-logs:      # 日志数据存储  
    driver: local
```

### 托管卷优势
- 🔧 **自动权限管理**：容器启动时自动设置正确的文件权限
- 🔄 **数据持久化**：容器重启或重新构建后数据不会丢失
- 🛡️ **避免权限冲突**：不再出现"Is a directory"错误
- 📁 **隔离存储**：数据和容器镜像分离，便于备份和迁移


## 🔒 安全最佳实践

### 1. API 密钥安全
```bash
# 使用环境变量存储敏感信息（推荐）
export TENCENT_SECRET_ID="your-secret-id"
export TENCENT_SECRET_KEY="your-secret-key"
```

### 2. 网络安全
- 🔒 仅在可信网络环境中部署
- 🔒 使用反向代理（Nginx/Caddy）添加 HTTPS
- 🔒 限制 4646 端口的访问权限
- 🔒 配置防火墙规则，仅允许必要IP访问

### 3. 容器安全
- ✅ 使用非 root 用户运行（已默认配置，UID/GID: 999:999）
- ✅ 使用 Docker 托管卷安全管理配置和日志存储
- ✅ 容器启动时自动设置正确的文件权限
- ✅ 定期更新基础镜像
- ✅ 限制容器资源使用

### 4. 日志安全
- 🗑️ 定期清理日志文件
- 🗑️ 避免在日志中记录敏感信息
- 🗑️ 使用日志轮转工具

## 🐛 故障排除指南

### 🔴 服务无法启动

#### Docker 环境
```bash
# 查看容器日志
docker logs edgeone-ddns

# 查看容器状态
docker ps -a | grep edgeone-ddns

# 重新构建镜像（无缓存）
docker-compose build --no-cache

# 检查 Docker 托管卷
docker volume ls | grep ddns

# 查看托管卷详细信息
docker volume inspect ddns-config
docker volume inspect ddns-logs
```

#### Docker 权限问题排查
```bash
# 如果遇到权限问题，重新创建托管卷
docker-compose down
docker volume rm ddns-config ddns-logs
docker-compose up -d

# 检查容器内权限
docker exec -it edgeone-ddns ls -la /app/
docker exec -it edgeone-ddns ls -la /app/config/
docker exec -it edgeone-ddn ls -la /app/logs/
```

#### 本地环境
```bash
# 检查Python版本
python --version  # 需要 3.8+

# 检查端口占用
netstat -tlnp | grep 4646  # Linux
netstat -ano | findstr 4646  # Windows

# 检查依赖安装
pip list | grep flask
```

### 🟡 DNS 更新失败

#### 权限问题
1. **检查 API 密钥权限**：确保有完整的 EdgeOne DNS 权限
2. **验证站点 ID**：格式应为 `zone-xxxxxxxx`
3. **确认域名状态**：域名必须在 EdgeOne 中正确接入

#### 网络问题
```bash
# 测试 API 连通性
curl -I https://teo.tencentcloudapi.com/

# 测试 DNS 解析
nslookup teo.tencentcloudapi.com
```

### 🟠 IP 检测问题

#### 内置检测服务失效
系统内置11个IP检测服务，自动故障转移：
- IPv4: 7个检测端点
- IPv6: 4个检测端点

#### 自定义检测端点
```bash
# 测试自定义端点
curl -4 "your-ipv4-endpoint"
curl -6 "your-ipv6-endpoint"
```

### 🔵 通知配置问题

#### Webhook 测试
使用 Web 界面的 **测试通知** 功能：
1. 检查 Webhook URL 格式
2. 验证请求头和请求体配置
3. 确认目标服务可达性

#### 常见通知服务配置示例

**钉钉机器人**
```json
{
  "url": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "body": {
    "msgtype": "text",
    "text": {"content": "DDNS更新: {ip_type}地址变更为{new_ip}"}
  }
}
```

**企业微信机器人**
```json
{
  "url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
  "method": "POST",
  "headers": {"Content-Type": "application/json"},
  "body": {
    "msgtype": "text",
    "text": {"content": "DDNS更新通知\n类型: {ip_type}\n新IP: {new_ip}"}
  }
}
```

### 🟢 系统健康检查

#### 检查 API 端点
```bash
# 检查系统状态
curl http://localhost:4646/api/status

# 测试手动更新
curl -X POST http://localhost:4646/api/manual_update

# 获取最新IP
curl http://localhost:4646/api/detect_ip
```

#### 日志分析
```bash
# 查看实时日志
tail -f logs/ddns.log

# 搜索错误日志
grep "ERROR" logs/ddns.log

# 统计更新记录
grep "DNS记录更新成功" logs/ddns.log | wc -l
```

## 📝 版本历史

### v2.0.0 (2024-11-29) - 重大功能更新
- ✨ **双栈支持**: 新增 IPv4/IPv6 双栈动态解析
- 🎯 **分离域名**: IPv4 和 IPv6 可配置不同域名列表
- 🔔 **自定义通知**: 重构通知系统，支持任意 Webhook 服务
- 🌍 **多源IP检测**: 内置 11 个 IP 检测服务，支持自定义端点
- 🔄 **灵活配置**: 支持独立启用/禁用 IPv4 或 IPv6
- 📱 **界面升级**: 基于 Bootstrap 5 的现代化界面
- 🐳 **Docker优化**: 改进日志目录映射，使用 Docker 托管卷解决权限问题
- 🔐 **权限管理**: 完善容器内文件权限管理，支持非 root 用户运行
- 📁 **配置管理**: 优化配置文件处理，支持 Web 界面动态创建

### v1.0.0 (2024-10-01) - 初始版本
- ✨ 基础 IPv4 DDNS 功能
- 🖥️ Web 管理界面
- 🔔 企业微信通知集成
- 🐳 Docker 容器化支持

## 🚀 路线图

### v2.1.0 (计划中)
- [ ] 批量域名管理
- [ ] DNS TTL 自定义设置
- [ ] 更多通知模板
- [ ] 系统备份/恢复功能

### v2.2.0 (规划中)
- [ ] 多站点支持
- [ ] 流量统计图表
- [ ] 移动端适配优化
- [ ] 国际化支持

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是 Bug 报告、功能建议还是代码提交。

### 🐛 报告问题
- 使用 [Issues](https://github.com/your-username/ddns-for-edgeone/issues) 报告 Bug
- 提供详细的重现步骤和环境信息
- 包含相关的错误日志

### 💡 功能建议
- 在 Issues 中使用 `enhancement` 标签
- 详细描述功能需求和使用场景
- 说明预期的行为和效果

### 🔧 代码贡献
1. **Fork** 本仓库到你的 GitHub 账户
2. **Clone** 你的 Fork 到本地：
   ```bash
   git clone https://github.com/your-username/ddns-for-edgeone.git
   cd ddns-for-edgeone
   ```
3. **创建** 功能分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **提交** 你的更改：
   ```bash
   git commit -m "feat: add your feature description"
   ```
5. **推送** 到你的 Fork：
   ```bash
   git push origin feature/your-feature-name
   ```
6. **创建** Pull Request

### 📋 开发规范
- 遵循 PEP 8 Python 代码规范
- 使用语义化提交信息
- 添加适当的测试用例
- 更新相关文档

## 📄 开源协议

本项目采用 [MIT 许可证](LICENSE) - 允许自由使用、修改和分发。

## 🌟 致谢

感谢以下开源项目和服务：

- **[Flask](https://flask.palletsprojects.com/)** - 优秀的 Python Web 框架
- **[Bootstrap](https://getbootstrap.com/)** - 现代化的前端 UI 框架
- **[腾讯云 EdgeOne](https://cloud.tencent.com/product/teo)** - 可靠的 DNS 服务
- **[Docker](https://www.docker.com/)** - 容器化技术支持

## 📞 获取帮助

### 📚 文档资源
- 📖 [完整文档](https://github.com/your-username/ddns-for-edgeone/wiki)
- 🔧 [配置指南](https://github.com/your-username/ddns-for-edgeone/wiki/Configuration)
- 🐛 [故障排除](https://github.com/your-username/ddns-for-edgeone/wiki/Troubleshooting)

### 💬 社区支持
- 🎯 [GitHub Issues](https://github.com/your-username/ddns-for-edgeone/issues) - 报告问题
- 💡 [GitHub Discussions](https://github.com/your-username/ddns-for-edgeone/discussions) - 讨论交流
- 🌟 [GitHub Wiki](https://github.com/your-username/ddns-for-edgeone/wiki) - 知识库

### ⭐ 支持项目
如果这个项目对你有帮助，请给我们一个 ⭐ Star！

---

<div align="center">

**[⬆️ 回到顶部](#edgeone-ddns-动态域名解析系统)**

Made with ❤️ by Open Source Community

</div>
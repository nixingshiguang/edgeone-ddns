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
    image: nixingshiguang/edgeone-ddns:latest
    container_name: edgeone-ddns
    volumes:
      - ddns-config:/app/config
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
git clone https://github.com/nixingshiguang/edgeone-ddns.git
cd edgeone-ddns
deploy.bat
```

#### Linux/Mac 用户
```bash
git clone https://github.com/nixingshiguang/edgeone-ddns.git
cd edgeone-ddns
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
git clone https://github.com/nixingshiguang/edgeone-ddns.git
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

## 📄 开源协议

本项目采用 [MIT 许可证](LICENSE) - 允许自由使用、修改和分发。

## 🌟 致谢

感谢以下开源项目和服务：

- **[Flask](https://flask.palletsprojects.com/)** - 优秀的 Python Web 框架
- **[Bootstrap](https://getbootstrap.com/)** - 现代化的前端 UI 框架
- **[腾讯云 EdgeOne](https://cloud.tencent.com/product/teo)** - 可靠的 DNS 服务
- **[Docker](https://www.docker.com/)** - 容器化技术支持

## 📞 获取帮助

### 💬 社区支持
- 🎯 [GitHub Issues](https://github.com/your-username/ddns-for-edgeone/issues) - 报告问题

### ⭐ 支持项目
如果这个项目对你有帮助，请给我们一个 ⭐ Star！

---

<div align="center">

**[⬆️ 回到顶部](#edgeone-ddns-动态域名解析系统)**

Made with ❤️

</div>
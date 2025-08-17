# GuiXiaoXiRag 部署指南

## 概述

本指南详细介绍了如何在不同环境中部署 GuiXiaoXiRag 服务，包括开发环境、测试环境和生产环境的部署方案。

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Ubuntu 18.04+, CentOS 7+, Windows 10+, macOS 10.14+
- **Python**: 3.8+

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 50GB SSD
- **网络**: 稳定的互联网连接（用于LLM API调用）

### 生产环境配置
- **CPU**: 8核心或更多
- **内存**: 16GB RAM 或更多
- **存储**: 100GB+ SSD
- **负载均衡**: Nginx 或 HAProxy
- **监控**: Prometheus + Grafana

## 环境准备

### 1. Python 环境设置

#### 使用 pyenv（推荐）
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.9
pyenv install 3.9.18
pyenv global 3.9.18

# 验证版本
python --version
```

#### 使用 conda
```bash
# 创建虚拟环境
conda create -n guixiaoxirag python=3.9
conda activate guixiaoxirag

# 验证环境
which python
python --version
```

#### 使用 venv
```bash
# 创建虚拟环境
python -m venv guixiaoxirag_env

# 激活环境
# Linux/macOS:
source guixiaoxirag_env/bin/activate
# Windows:
guixiaoxirag_env\Scripts\activate

# 验证环境
which python
```

### 2. 系统依赖安装

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    python3-dev \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev
```

#### CentOS/RHEL
```bash
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    python3-devel \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    openssl-devel \
    libffi-devel \
    libxml2-devel \
    libxslt-devel \
    zlib-devel
```

#### macOS
```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python@3.9 git curl wget
```

## 部署方式

### 方式一：直接部署

#### 1. 获取源码
```bash
# 克隆项目
git clone <repository-url>
cd server_new

# 或者下载压缩包
wget <download-url>
unzip server_new.zip
cd server_new
```

#### 2. 安装依赖
```bash
# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list | grep fastapi
```

#### 3. 配置环境
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

#### 4. 初始化目录
```bash
# 创建必要目录
mkdir -p knowledgeBase/default
mkdir -p logs
mkdir -p uploads

# 设置权限
chmod 755 knowledgeBase logs uploads
```

#### 5. 启动服务
```bash
# 开发模式启动
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

#### 6. 验证部署
```bash
# 健康检查
curl http://localhost:8002/api/v1/health

# 查看API文档
curl http://localhost:8002/docs
```

### 方式二：Docker 部署

#### 1. 创建 Dockerfile
```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p knowledgeBase/default logs uploads

# 设置权限
RUN chmod 755 knowledgeBase logs uploads

# 暴露端口
EXPOSE 8002

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/api/v1/health || exit 1

# 启动命令
CMD ["python", "main.py"]
```

#### 2. 构建镜像
```bash
# 构建镜像
docker build -t guixiaoxirag:latest .

# 查看镜像
docker images | grep guixiaoxirag
```

#### 3. 运行容器
```bash
# 基础运行
docker run -d \
    --name guixiaoxirag \
    -p 8002:8002 \
    guixiaoxirag:latest

# 带数据卷运行
docker run -d \
    --name guixiaoxirag \
    -p 8002:8002 \
    -v $(pwd)/knowledgeBase:/app/knowledgeBase \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/.env:/app/.env \
    guixiaoxirag:latest

# 查看容器状态
docker ps
docker logs guixiaoxirag
```

#### 4. Docker Compose 部署
```yaml
# docker-compose.yml
version: '3.8'

services:
  guixiaoxirag:
    build: .
    container_name: guixiaoxirag
    ports:
      - "8002:8002"
    volumes:
      - ./knowledgeBase:/app/knowledgeBase
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - LOG_LEVEL=INFO
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 可选：添加 Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: guixiaoxirag-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - guixiaoxirag
    restart: unless-stopped

networks:
  default:
    name: guixiaoxirag-network
```

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f guixiaoxirag
```

### 方式三：生产环境部署

#### 1. 使用 Gunicorn + Nginx

##### 安装 Gunicorn
```bash
pip install gunicorn
```

##### 创建 Gunicorn 配置
```python
# gunicorn.conf.py
import multiprocessing

# 服务器配置
bind = "127.0.0.1:8002"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = "./logs/gunicorn_access.log"
errorlog = "./logs/gunicorn_error.log"
loglevel = "info"

# 进程配置
daemon = False
pidfile = "./logs/gunicorn.pid"
user = "www-data"
group = "www-data"

# 性能配置
preload_app = True
timeout = 120
keepalive = 5
```

##### 启动 Gunicorn
```bash
# 使用配置文件启动
gunicorn -c gunicorn.conf.py main:app

# 或直接指定参数
gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8002 \
    --access-logfile ./logs/access.log \
    --error-logfile ./logs/error.log
```

##### 配置 Nginx
```nginx
# /etc/nginx/sites-available/guixiaoxirag
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 配置
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 日志配置
    access_log /var/log/nginx/guixiaoxirag_access.log;
    error_log /var/log/nginx/guixiaoxirag_error.log;

    # 上传大小限制
    client_max_body_size 50M;

    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 静态文件缓存
    location /static/ {
        alias /path/to/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 文档路径
    location /docs {
        proxy_pass http://127.0.0.1:8002/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/guixiaoxirag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 2. 使用 Supervisor 进程管理

##### 安装 Supervisor
```bash
sudo apt install supervisor
# 或
sudo yum install supervisor
```

##### 配置 Supervisor
```ini
# /etc/supervisor/conf.d/guixiaoxirag.conf
[program:guixiaoxirag]
command=/path/to/venv/bin/gunicorn -c /path/to/gunicorn.conf.py main:app
directory=/path/to/server_new
user=www-data
group=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/guixiaoxirag.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/path/to/venv/bin"
```

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start guixiaoxirag

# 查看状态
sudo supervisorctl status guixiaoxirag
```

#### 3. 系统服务配置

##### 创建 systemd 服务
```ini
# /etc/systemd/system/guixiaoxirag.service
[Unit]
Description=GuiXiaoXiRag FastAPI Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/server_new
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable guixiaoxirag

# 启动服务
sudo systemctl start guixiaoxirag

# 查看状态
sudo systemctl status guixiaoxirag

# 查看日志
sudo journalctl -u guixiaoxirag -f
```

## 配置管理

### 环境变量配置

#### 开发环境 (.env.development)
```bash
DEBUG=true
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8002

# 使用本地模拟服务
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
```

#### 测试环境 (.env.testing)
```bash
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8002

# 使用测试环境服务
OPENAI_API_BASE=http://test-llm-service:8100/v1
OPENAI_EMBEDDING_API_BASE=http://test-embedding-service:8200/v1
```

#### 生产环境 (.env.production)
```bash
DEBUG=false
LOG_LEVEL=WARNING
HOST=127.0.0.1
PORT=8002
WORKERS=4

# 使用生产环境服务
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_CHAT_API_KEY=${OPENAI_API_KEY}
OPENAI_EMBEDDING_API_KEY=${EMBEDDING_API_KEY}

# 性能优化配置
ENABLE_CACHE=true
CACHE_TTL=7200
MAX_CONCURRENT_REQUESTS=200
```

### 配置验证脚本

```python
#!/usr/bin/env python3
"""
配置验证脚本
"""
import os
import sys
from pathlib import Path

def validate_config():
    """验证配置"""
    errors = []
    warnings = []
    
    # 检查必需的环境变量
    required_vars = [
        'OPENAI_API_BASE',
        'OPENAI_CHAT_MODEL',
        'WORKING_DIR'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"缺少必需的环境变量: {var}")
    
    # 检查目录权限
    dirs_to_check = [
        os.getenv('WORKING_DIR', './knowledgeBase/default'),
        os.getenv('LOG_DIR', './logs'),
        os.getenv('UPLOAD_DIR', './uploads')
    ]
    
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if not path.exists():
            warnings.append(f"目录不存在，将自动创建: {dir_path}")
            path.mkdir(parents=True, exist_ok=True)
        elif not os.access(path, os.W_OK):
            errors.append(f"目录没有写权限: {dir_path}")
    
    # 检查端口
    port = os.getenv('PORT', '8002')
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            errors.append(f"端口号无效: {port}")
    except ValueError:
        errors.append(f"端口号格式错误: {port}")
    
    # 输出结果
    if warnings:
        print("⚠️  配置警告:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"   - {error}")
        return False
    else:
        print("✅ 配置验证通过")
        return True

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    if not validate_config():
        sys.exit(1)
```

## 监控和日志

### 日志配置

#### 日志轮转配置
```bash
# /etc/logrotate.d/guixiaoxirag
/path/to/server_new/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload guixiaoxirag
    endscript
}
```

#### 日志监控脚本
```bash
#!/bin/bash
# monitor_logs.sh

LOG_DIR="/path/to/server_new/logs"
ERROR_LOG="$LOG_DIR/guixiaoxirag_service.log"

# 监控错误日志
tail -f "$ERROR_LOG" | while read line; do
    if echo "$line" | grep -q "ERROR\|CRITICAL"; then
        echo "$(date): $line" | mail -s "GuiXiaoXiRag Error Alert" admin@example.com
    fi
done
```

### 性能监控

#### Prometheus 配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'guixiaoxirag'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 30s
```

#### Grafana 仪表板
```json
{
  "dashboard": {
    "title": "GuiXiaoXiRag Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8002
sudo lsof -i :8002

# 检查权限
ls -la /path/to/server_new
sudo chown -R www-data:www-data /path/to/server_new

# 检查依赖
pip check
pip list --outdated
```

#### 2. 内存不足
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 优化配置
# 减少 worker 数量
# 启用缓存清理
# 调整批处理大小
```

#### 3. 磁盘空间不足
```bash
# 检查磁盘使用
df -h
du -sh /path/to/server_new/*

# 清理日志
find /path/to/logs -name "*.log" -mtime +30 -delete

# 清理缓存
curl -X DELETE http://localhost:8002/api/v1/cache/clear
```

### 调试工具

#### 健康检查脚本
```bash
#!/bin/bash
# health_check.sh

API_BASE="http://localhost:8002/api/v1"

echo "=== GuiXiaoXiRag 健康检查 ==="

# 检查服务状态
echo "1. 检查服务状态..."
if curl -s "$API_BASE/health" > /dev/null; then
    echo "✅ 服务正常运行"
else
    echo "❌ 服务无响应"
    exit 1
fi

# 检查系统状态
echo "2. 检查系统状态..."
SYSTEM_STATUS=$(curl -s "$API_BASE/system/status" | jq -r '.data.status')
if [ "$SYSTEM_STATUS" = "running" ]; then
    echo "✅ 系统状态正常"
else
    echo "⚠️  系统状态异常: $SYSTEM_STATUS"
fi

# 检查性能指标
echo "3. 检查性能指标..."
METRICS=$(curl -s "$API_BASE/metrics")
ERROR_RATE=$(echo "$METRICS" | jq -r '.data.error_rate // 0')
if (( $(echo "$ERROR_RATE < 0.05" | bc -l) )); then
    echo "✅ 错误率正常: $ERROR_RATE"
else
    echo "⚠️  错误率过高: $ERROR_RATE"
fi

echo "=== 健康检查完成 ==="
```

## 安全配置

### SSL/TLS 配置

#### 获取 SSL 证书
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 安全头配置
```nginx
# 在 Nginx 配置中添加
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### 防火墙配置

#### UFW (Ubuntu)
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8002/tcp  # 只允许内部访问
```

#### iptables
```bash
# 允许 HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 拒绝直接访问应用端口
sudo iptables -A INPUT -p tcp --dport 8002 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8002 -j DROP
```

## 备份和恢复

### 数据备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/guixiaoxirag"
APP_DIR="/path/to/server_new"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 备份知识库
tar -czf "$BACKUP_DIR/knowledgeBase_$DATE.tar.gz" -C "$APP_DIR" knowledgeBase/

# 备份配置
cp "$APP_DIR/.env" "$BACKUP_DIR/env_$DATE"

# 备份日志（最近7天）
find "$APP_DIR/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR"
```

### 恢复脚本
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE="$1"
APP_DIR="/path/to/server_new"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    exit 1
fi

# 停止服务
sudo systemctl stop guixiaoxirag

# 备份当前数据
mv "$APP_DIR/knowledgeBase" "$APP_DIR/knowledgeBase.bak.$(date +%s)"

# 恢复数据
tar -xzf "$BACKUP_FILE" -C "$APP_DIR"

# 启动服务
sudo systemctl start guixiaoxirag

echo "恢复完成"
```

---

*本部署指南提供了完整的部署流程和最佳实践，确保 GuiXiaoXiRag 服务的稳定运行。*

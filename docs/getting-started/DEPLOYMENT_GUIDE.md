# GuiXiaoXiRag FastAPI 部署指南

## 🎯 部署概述

本指南提供了GuiXiaoXiRag FastAPI服务的完整部署方案，包括开发环境、测试环境和生产环境的部署配置。

## 📋 部署前检查清单

### 系统要求
- [ ] Linux服务器（推荐Ubuntu 20.04+或CentOS 8+）
- [ ] Python 3.8+（推荐3.10+）
- [ ] 16GB+ RAM（推荐32GB+）
- [ ] 100GB+ 可用磁盘空间
- [ ] NVIDIA GPU（可选，用于本地大模型推理）

### 服务依赖
- [ ] LLM服务（默认端口8100）
- [ ] Embedding服务（默认端口8200）
- [ ] Redis（可选，用于缓存）
- [ ] Nginx（可选，用于反向代理）

### 网络要求
- [ ] 确保端口8002可访问（API服务）
- [ ] 确保端口8501可访问（Web界面，可选）
- [ ] 确保可访问LLM和Embedding服务

## 🚀 快速部署

### 1. 环境准备

#### 克隆项目
```bash
git clone <repository_url>
cd guixiaoxi2
```

#### 创建Python环境
```bash
# 使用conda（推荐）
conda create -n guixiaoxirag python=3.10
conda activate guixiaoxirag

# 或使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 验证安装
python -c "import guixiaoxiRag; print('GuiXiaoXiRag installed successfully')"
```

### 3. 配置环境

#### 创建配置文件
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

#### 基础配置示例
```env
# 服务配置
HOST=0.0.0.0
PORT=8002
DEBUG=false
LOG_LEVEL=INFO

# 知识库配置
WORKING_DIR=./knowledgeBase/default

# 大模型配置
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=qwen14b
OPENAI_EMBEDDING_MODEL=embedding_qwen

# 性能配置
EMBEDDING_DIM=1536
MAX_TOKEN_SIZE=8192
MAX_FILE_SIZE=52428800

# 日志配置
LOG_DIR=./logs
```

### 4. 启动服务

#### 方式一：使用主启动文件（推荐）
```bash
# 基础启动
python main.py

# 生产环境启动
python main.py --host 0.0.0.0 --port 8002 --workers 4

# 开发环境启动
python main.py --reload --log-level debug
```

#### 方式二：使用uvicorn
```bash
# 单进程启动
uvicorn server.main:app --host 0.0.0.0 --port 8002

# 多进程启动
uvicorn server.main:app --host 0.0.0.0 --port 8002 --workers 4
```

### 5. 验证部署

```bash
# 健康检查
curl http://localhost:8002/health

# 查看API文档
open http://localhost:8002/docs

# 测试基本功能
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "这是一个测试文档"}'
```

## 🏭 生产环境部署

### 1. 系统优化

#### 系统参数调优
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化网络参数
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```

#### 创建系统用户
```bash
# 创建专用用户
sudo useradd -r -s /bin/false guixiaoxirag
sudo mkdir -p /opt/guixiaoxirag
sudo chown guixiaoxirag:guixiaoxirag /opt/guixiaoxirag
```

### 2. 使用Systemd管理服务

#### 创建服务文件
```bash
sudo vim /etc/systemd/system/guixiaoxirag.service
```

```ini
[Unit]
Description=GuiXiaoXiRag FastAPI Service
After=network.target

[Service]
Type=exec
User=guixiaoxirag
Group=guixiaoxirag
WorkingDirectory=/opt/guixiaoxirag
Environment=PATH=/opt/guixiaoxirag/venv/bin
ExecStart=/opt/guixiaoxirag/venv/bin/python main.py --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 启动和管理服务
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start guixiaoxirag

# 设置开机自启
sudo systemctl enable guixiaoxirag

# 查看服务状态
sudo systemctl status guixiaoxirag

# 查看日志
sudo journalctl -u guixiaoxirag -f
```

### 3. 使用Nginx反向代理

#### 安装Nginx
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 配置Nginx
```bash
sudo vim /etc/nginx/sites-available/guixiaoxirag
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # API服务代理
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 文件上传大小限制
        client_max_body_size 100M;
    }

    # Streamlit界面代理（可选）
    location /streamlit/ {
        proxy_pass http://127.0.0.1:8501/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 启用配置
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/guixiaoxirag /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 4. SSL/HTTPS配置

#### 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 🐳 Docker部署

### 1. 创建Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p logs knowledgeBase uploads

# 暴露端口
EXPOSE 8002

# 启动命令
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'

services:
  guixiaoxirag:
    build: .
    ports:
      - "8002:8002"
    environment:
      - HOST=0.0.0.0
      - PORT=8002
      - WORKERS=4
      - OPENAI_API_BASE=http://llm-service:8100/v1
      - OPENAI_EMBEDDING_API_BASE=http://embedding-service:8200/v1
    volumes:
      - ./knowledgeBase:/app/knowledgeBase
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - guixiaoxirag
    restart: unless-stopped
```

### 3. 构建和运行
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f guixiaoxirag

# 停止服务
docker-compose down
```

## 📊 监控和日志

### 1. 日志管理

#### 配置日志轮转
```bash
sudo vim /etc/logrotate.d/guixiaoxirag
```

```
/opt/guixiaoxirag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 guixiaoxirag guixiaoxirag
    postrotate
        systemctl reload guixiaoxirag
    endscript
}
```

### 2. 性能监控

#### 使用Prometheus监控
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'guixiaoxirag'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/metrics'
```

### 3. 健康检查

#### 创建健康检查脚本
```bash
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:8002/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

## 🔧 性能优化

### 1. 应用层优化

```env
# 生产环境配置
WORKERS=4                    # 根据CPU核心数调整
ENABLE_CACHE=true           # 启用缓存
CACHE_TTL=3600             # 缓存时间
MAX_CONCURRENT_REQUESTS=100 # 并发限制
```

### 2. 数据库优化

```bash
# 定期清理日志
find ./logs -name "*.log" -mtime +30 -delete

# 压缩旧的知识库
tar -czf backup_$(date +%Y%m%d).tar.gz knowledgeBase/
```

### 3. 系统优化

```bash
# 调整内核参数
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.dirty_ratio=15' >> /etc/sysctl.conf
echo 'vm.dirty_background_ratio=5' >> /etc/sysctl.conf
```

## 🔒 安全配置

### 1. 防火墙设置
```bash
# 使用ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. 应用安全
```env
# 限制CORS源
CORS_ORIGINS=["https://yourdomain.com"]

# 禁用调试模式
DEBUG=false

# 设置强密钥
OPENAI_CHAT_API_KEY=your_secure_api_key
```

## 🔗 相关文档

- [快速开始指南](QUICK_START.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [API文档](../api/README.md)

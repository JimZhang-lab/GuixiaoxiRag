# GuiXiaoXiRag FastAPI 配置指南

## 🎯 配置概述

GuiXiaoXiRag FastAPI 项目采用统一的配置管理系统，支持从根目录的 `.env` 文件中读取配置，同时支持环境变量覆盖。

## 📁 配置文件结构

```
guixiaoxi2/
├── .env                    # 主配置文件（需要创建）
├── .env.example           # 配置模板文件
├── server/config.py       # 服务器配置模块
├── streamlit_app/config.py # Streamlit配置模块
└── scripts/config_manager.py # 配置管理工具
```

## 🚀 快速开始

### 1. 创建配置文件

```bash
# 复制配置模板
cp .env.example .env

# 或使用配置管理工具
python scripts/config_manager.py --generate
```

### 2. 编辑配置文件

```bash
# 使用你喜欢的编辑器
vim .env
# 或
nano .env
```

### 3. 验证配置

```bash
# 验证所有配置
python scripts/config_manager.py --validate

# 查看配置摘要
python scripts/config_manager.py --summary

# 执行完整检查
python scripts/config_manager.py --all
```

## ⚙️ 配置项详解

### 🚀 应用基础配置

```env
# 应用信息
APP_NAME=GuiXiaoXiRag FastAPI Service
APP_VERSION=1.0.0

# 服务配置
HOST=0.0.0.0              # 服务监听地址
PORT=8002                 # 服务端口
DEBUG=false               # 调试模式
WORKERS=1                 # 工作进程数
```

### 🧠 大模型配置

```env
# OpenAI API 配置
OPENAI_API_BASE=http://localhost:8100/v1           # LLM服务地址
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1 # Embedding服务地址
OPENAI_CHAT_API_KEY=your_api_key_here              # API密钥
OPENAI_CHAT_MODEL=qwen14b                          # 聊天模型
OPENAI_EMBEDDING_MODEL=embedding_qwen              # 嵌入模型

# Embedding配置
EMBEDDING_DIM=1536        # 向量维度
MAX_TOKEN_SIZE=8192       # 最大token数
```

### 📁 存储配置

```env
# 知识库配置
WORKING_DIR=./knowledgeBase/default  # 默认知识库目录

# 日志配置
LOG_LEVEL=INFO            # 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_DIR=./logs           # 日志目录

# 文件上传配置
MAX_FILE_SIZE=52428800   # 最大文件大小(字节) 50MB
UPLOAD_DIR=./uploads     # 上传文件目录
```

### 🎨 Streamlit配置

```env
# Streamlit服务配置
STREAMLIT_HOST=0.0.0.0
STREAMLIT_PORT=8501
STREAMLIT_DEBUG=false

# Streamlit API配置
STREAMLIT_API_URL=http://localhost:8002
STREAMLIT_API_TIMEOUT=120
STREAMLIT_API_RETRY_TIMES=3
STREAMLIT_API_RETRY_DELAY=1.0

# Streamlit界面配置
STREAMLIT_MAX_UPLOAD_SIZE=50
STREAMLIT_ITEMS_PER_PAGE=10
STREAMLIT_AUTO_REFRESH_INTERVAL=30

# Streamlit主题配置
STREAMLIT_PRIMARY_COLOR=#FF6B6B
STREAMLIT_BACKGROUND_COLOR=#FFFFFF
STREAMLIT_SECONDARY_BACKGROUND_COLOR=#F0F2F6
STREAMLIT_TEXT_COLOR=#262730
```

### ⚡ 性能配置

```env
# 缓存配置
ENABLE_CACHE=true         # 启用缓存
CACHE_TTL=3600           # 缓存生存时间(秒)
STREAMLIT_CACHE_TTL=300  # Streamlit缓存时间

# 并发配置
MAX_CONCURRENT_REQUESTS=100  # 最大并发请求数
```

### 🔒 安全配置

```env
# CORS配置
CORS_ORIGINS=["*"]       # 允许的源
CORS_METHODS=["*"]       # 允许的方法
CORS_HEADERS=["*"]       # 允许的头部
```

## 🔧 配置管理工具

### 使用配置管理脚本

```bash
# 生成.env文件
python scripts/config_manager.py --generate

# 验证配置
python scripts/config_manager.py --validate

# 检查环境变量
python scripts/config_manager.py --check-env

# 测试API连接
python scripts/config_manager.py --test-api

# 显示配置摘要
python scripts/config_manager.py --summary

# 执行所有检查
python scripts/config_manager.py --all
```

### 配置验证

配置管理工具会自动验证：
- ✅ 端口号范围（1-65535）
- ✅ API密钥设置
- ✅ 目录路径有效性
- ✅ 文件大小限制
- ✅ API服务连通性

## 🌍 环境变量优先级

配置系统按以下优先级读取配置：

1. **环境变量** - 最高优先级
2. **项目根目录/.env** - 主配置文件
3. **项目根目录/.env.local** - 本地配置文件
4. **当前目录/.env** - 备用配置文件
5. **默认值** - 代码中的默认值

### 示例：覆盖配置

```bash
# 使用环境变量覆盖端口
export PORT=8003
python main.py

# 或在启动时指定
PORT=8003 python main.py
```

## 📊 配置最佳实践

### 🔒 安全配置

1. **保护API密钥**
   ```bash
   # 不要在代码中硬编码密钥
   OPENAI_CHAT_API_KEY=your_real_api_key_here
   
   # 使用环境变量在生产环境中设置
   export OPENAI_CHAT_API_KEY="your_production_key"
   ```

2. **限制CORS源**
   ```env
   # 生产环境中限制CORS源
   CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]
   ```

### ⚡ 性能配置

1. **调整工作进程数**
   ```env
   # 根据CPU核心数调整
   WORKERS=4  # 通常设置为CPU核心数
   ```

2. **优化缓存设置**
   ```env
   # 根据内存情况调整缓存时间
   CACHE_TTL=7200  # 2小时
   STREAMLIT_CACHE_TTL=600  # 10分钟
   ```

3. **调整文件大小限制**
   ```env
   # 根据需求调整文件大小限制
   MAX_FILE_SIZE=104857600  # 100MB
   ```

### 🚀 部署配置

1. **开发环境**
   ```env
   DEBUG=true
   LOG_LEVEL=DEBUG
   WORKERS=1
   ```

2. **生产环境**
   ```env
   DEBUG=false
   LOG_LEVEL=INFO
   WORKERS=4
   ENABLE_CACHE=true
   ```

## 🔍 故障排除

### 常见配置问题

1. **配置文件不存在**
   ```bash
   # 错误：.env 文件不存在
   # 解决：复制模板文件
   cp .env.example .env
   ```

2. **API密钥未设置**
   ```bash
   # 错误：API密钥为默认值
   # 解决：设置真实的API密钥
   OPENAI_CHAT_API_KEY=your_real_api_key
   ```

3. **端口被占用**
   ```bash
   # 错误：端口8002被占用
   # 解决：更换端口
   PORT=8003
   ```

4. **大模型服务连接失败**
   ```bash
   # 错误：无法连接到大模型服务
   # 解决：检查服务地址和状态
   OPENAI_API_BASE=http://your_llm_server:8100/v1
   ```

### 配置验证命令

```bash
# 完整的配置检查
python scripts/config_manager.py --all

# 检查特定问题
python scripts/config_manager.py --check-env
python scripts/config_manager.py --test-api
```

## 📝 配置模板

### 最小配置

```env
# 最小可运行配置
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=qwen14b
OPENAI_EMBEDDING_MODEL=embedding_qwen
```

### 完整配置

参考项目根目录的 `.env.example` 文件获取完整的配置模板。

## 🔗 相关文档

- [快速开始指南](QUICK_START.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [故障排除指南](TROUBLESHOOTING.md)
- [API参考文档](../api/API_REFERENCE.md)

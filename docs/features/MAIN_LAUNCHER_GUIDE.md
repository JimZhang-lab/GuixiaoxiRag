# GuiXiaoXiRag FastAPI 主启动器指南

## 🚀 主启动器概述

GuiXiaoXiRag FastAPI 项目的主启动器 (`main.py`) 是一个智能化的服务启动和管理工具，提供了完整的环境检查、配置验证、服务启动和状态管理功能。

## 🌟 核心特性

### 🔍 智能环境检查
- **依赖验证**: 自动检查必需的Python包是否已安装
- **配置检查**: 验证配置文件的存在性和有效性
- **服务检查**: 检查大模型服务的连接状态
- **目录检查**: 确保必要的目录结构存在

### ⚙️ 灵活配置管理
- **命令行参数**: 支持丰富的命令行参数配置
- **环境变量**: 支持通过环境变量覆盖配置
- **配置文件**: 自动读取和验证 `.env` 配置文件
- **默认值**: 提供合理的默认配置值

### 🚀 多种启动模式
- **开发模式**: 自动重载、详细日志、单进程
- **生产模式**: 多进程、优化性能、稳定运行
- **调试模式**: 详细调试信息、错误追踪
- **状态检查**: 服务状态查询和监控

## 📋 使用方法

### 基本启动命令

#### 默认启动
```bash
# 使用默认配置启动服务
python main.py
```

#### 开发模式启动
```bash
# 开发模式：自动重载 + 调试日志
python main.py --reload --log-level debug

# 开发模式：指定端口
python main.py --reload --port 8003

# 开发模式：详细输出
python main.py --reload --log-level debug --verbose
```

#### 生产模式启动
```bash
# 生产模式：多进程
python main.py --workers 4

# 生产模式：指定主机和端口
python main.py --host 0.0.0.0 --port 8002 --workers 4

# 生产模式：后台运行
nohup python main.py --workers 4 > /dev/null 2>&1 &
```

#### 状态管理
```bash
# 检查服务状态
python main.py status

# 查看帮助信息
python main.py --help

# 查看版本信息
python main.py --version
```

### 命令行参数详解

#### 服务配置参数
```bash
--host HOST              # 服务监听地址 (默认: 0.0.0.0)
--port PORT              # 服务端口 (默认: 8002)
--workers WORKERS        # 工作进程数 (默认: 1)
--reload                 # 开启自动重载 (开发模式)
```

#### 日志配置参数
```bash
--log-level LEVEL        # 日志级别: debug, info, warning, error
--log-file FILE          # 日志文件路径
--access-log             # 启用访问日志
--verbose                # 详细输出模式
```

#### 功能控制参数
```bash
--no-check               # 跳过环境检查
--no-config              # 跳过配置验证
--force                  # 强制启动（忽略警告）
--dry-run                # 模拟运行（不实际启动）
```

### 环境变量支持

主启动器支持通过环境变量配置：

```bash
# 服务配置
export HOST=0.0.0.0
export PORT=8002
export WORKERS=4

# 日志配置
export LOG_LEVEL=info
export LOG_FILE=./logs/main.log

# 启动服务
python main.py
```

## 🔧 启动流程详解

### 1. 环境检查阶段
```
检查Python版本 → 验证依赖包 → 检查配置文件 → 验证目录结构
```

**检查项目**:
- Python版本兼容性 (≥3.8)
- 必需依赖包的安装状态
- `.env` 配置文件存在性
- 日志、上传、知识库目录

### 2. 配置验证阶段
```
读取配置文件 → 解析命令行参数 → 合并配置 → 验证配置有效性
```

**验证内容**:
- 端口号范围和可用性
- API密钥和服务地址
- 文件路径和权限
- 资源限制和约束

### 3. 服务启动阶段
```
初始化应用 → 配置中间件 → 注册路由 → 启动服务器
```

**启动步骤**:
- 创建FastAPI应用实例
- 配置CORS和安全中间件
- 注册所有API路由
- 启动uvicorn服务器

### 4. 运行监控阶段
```
健康检查 → 性能监控 → 错误处理 → 优雅关闭
```

**监控功能**:
- 定期健康状态检查
- 性能指标收集
- 异常情况处理
- 信号处理和优雅关闭

## 🎯 使用场景

### 开发环境
```bash
# 快速开发和调试
python main.py --reload --log-level debug

# 特点：
# - 代码变更自动重载
# - 详细的调试信息
# - 单进程便于调试
# - 实时错误反馈
```

### 测试环境
```bash
# 模拟生产环境测试
python main.py --workers 2 --log-level info

# 特点：
# - 多进程测试并发性能
# - 适中的日志级别
# - 稳定的运行模式
# - 性能基准测试
```

### 生产环境
```bash
# 高性能生产部署
python main.py --host 0.0.0.0 --port 8002 --workers 4 --log-level warning

# 特点：
# - 多进程高并发处理
# - 优化的日志级别
# - 稳定可靠运行
# - 资源使用优化
```

### 容器化部署
```bash
# Docker容器启动
python main.py --host 0.0.0.0 --workers 4 --no-check

# 特点：
# - 适配容器环境
# - 跳过环境检查
# - 标准化配置
# - 容器编排支持
```

## 🔍 故障排除

### 常见启动问题

#### 端口被占用
```bash
# 错误信息
Error: [Errno 98] Address already in use

# 解决方案
python main.py --port 8003  # 使用其他端口
# 或
lsof -i :8002               # 查看端口占用
kill -9 <PID>               # 杀死占用进程
```

#### 依赖包缺失
```bash
# 错误信息
ModuleNotFoundError: No module named 'xxx'

# 解决方案
pip install -r requirements.txt  # 重新安装依赖
# 或
conda activate guixiaoxirag      # 激活正确环境
```

#### 配置文件问题
```bash
# 错误信息
Configuration validation failed

# 解决方案
python scripts/config_manager.py --validate  # 验证配置
cp .env.example .env                         # 重新创建配置
```

#### 权限问题
```bash
# 错误信息
Permission denied

# 解决方案
chmod +x main.py                    # 添加执行权限
sudo chown -R user:group ./logs     # 修改目录权限
```

### 调试技巧

#### 详细日志输出
```bash
# 启用详细日志
python main.py --log-level debug --verbose

# 查看启动日志
tail -f logs/main.log
```

#### 模拟运行
```bash
# 模拟运行检查配置
python main.py --dry-run

# 跳过检查强制启动
python main.py --force --no-check
```

#### 分步诊断
```bash
# 1. 检查环境
python -c "import guixiaoxiRag; print('OK')"

# 2. 验证配置
python scripts/config_manager.py --validate

# 3. 测试启动
python main.py --dry-run
```

## 🔧 高级配置

### 自定义启动脚本
```bash
#!/bin/bash
# start_production.sh

# 设置环境变量
export HOST=0.0.0.0
export PORT=8002
export WORKERS=4
export LOG_LEVEL=info

# 检查服务状态
if python main.py status; then
    echo "Service is already running"
    exit 1
fi

# 启动服务
echo "Starting GuiXiaoXiRag FastAPI service..."
python main.py --workers $WORKERS --log-level $LOG_LEVEL

# 验证启动
sleep 5
if python main.py status; then
    echo "Service started successfully"
else
    echo "Service failed to start"
    exit 1
fi
```

### 系统服务配置
```ini
# /etc/systemd/system/guixiaoxirag.service
[Unit]
Description=GuiXiaoXiRag FastAPI Service
After=network.target

[Service]
Type=exec
User=guixiaoxirag
WorkingDirectory=/opt/guixiaoxirag
ExecStart=/opt/guixiaoxirag/venv/bin/python main.py --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 监控脚本
```bash
#!/bin/bash
# monitor.sh

while true; do
    if ! python main.py status > /dev/null 2>&1; then
        echo "$(date): Service is down, restarting..."
        python main.py --workers 4 &
    fi
    sleep 60
done
```

## 🔗 相关文档

- [快速开始指南](../getting-started/QUICK_START.md)
- [配置指南](../getting-started/CONFIGURATION_GUIDE.md)
- [部署指南](../getting-started/DEPLOYMENT_GUIDE.md)
- [故障排除指南](../getting-started/TROUBLESHOOTING.md)
- [项目架构](../project/PROJECT_ARCHITECTURE.md)

## 💡 最佳实践

1. **开发阶段**: 使用 `--reload` 和 `--log-level debug` 进行开发
2. **测试阶段**: 使用多进程模式测试并发性能
3. **生产部署**: 使用适当的worker数量和日志级别
4. **监控运维**: 定期检查服务状态和日志
5. **配置管理**: 使用环境变量管理不同环境的配置

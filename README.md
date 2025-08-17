# GuiXiaoXiRag FastAPI 服务

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

**GuiXiaoXi检索增强生成（RAG）FastAPI 服务**

*提供企业级的智能问答和知识管理解决方案*

[📖 文档](docs/README.md) • [🚀 快速开始](docs/Quick_Start_Guide.md) • [🌐 API 文档](http://localhost:8002/docs)

</div>

## 项目简介

GuiXiaoXiRag 是一个基于 FastAPI 的智能知识问答系统，集成了知识图谱、向量检索、意图识别等多种AI技术。该系统提供强大的知识管理和智能查询功能，支持多种文档格式的处理和多模态的知识检索。

## 主要特性

### 🚀 核心功能
- **智能查询**: 支持多种查询模式（local/global/hybrid/naive/mix/bypass）
- **知识图谱**: 自动构建和管理知识图谱，支持可视化展示
- **文档管理**: 支持多种格式文档的上传、处理和索引
- **意图识别**: 智能分析查询意图和安全级别
- **多知识库**: 支持创建和管理多个独立的知识库

### 🛠️ 技术特性
- **模块化架构**: 清晰的分层设计，易于维护和扩展
- **异步处理**: 基于 FastAPI 的高性能异步处理
- **缓存机制**: 多层缓存优化，提升查询性能
- **安全检查**: 内置安全检查和内容过滤机制
- **性能监控**: 完整的性能指标和健康检查

### 📊 支持格式
- **文档格式**: PDF, DOCX, DOC, TXT, MD, JSON, XML, CSV
- **查询模式**: 文本查询、批量查询、流式查询
- **输出格式**: JSON, XML, CSV, HTML可视化

## 系统架构

```
GuiXiaoXiRag/
├── api/                    # API业务逻辑层
│   ├── query_api.py       # 查询API处理器
│   ├── document_api.py    # 文档管理API
│   ├── knowledge_base_api.py  # 知识库管理API
│   ├── knowledge_graph_api.py # 知识图谱API
│   ├── system_api.py      # 系统管理API
│   ├── intent_recogition_api.py # 意图识别API
│   └── cache_management_api.py  # 缓存管理API
├── routers/               # FastAPI路由层
│   ├── query_router.py    # 查询路由
│   ├── document_router.py # 文档管理路由
│   ├── knowledge_base_router.py # 知识库路由
│   ├── knowledge_graph_router.py # 知识图谱路由
│   ├── system_router.py   # 系统管理路由
│   ├── intent_recogition_router.py # 意图识别路由
│   └── cache_management_router.py  # 缓存管理路由
├── model/                 # 数据模型层
│   ├── base_models.py     # 基础模型
│   ├── request_models.py  # 请求模型
│   ├── response_models.py # 响应模型
│   └── ...
├── handler/               # 核心处理器
│   ├── guixiaoxirag_service.py # 核心服务
│   ├── document_processor.py   # 文档处理器
│   ├── knowledge_base_manager.py # 知识库管理器
│   └── query_processor.py      # 查询处理器
├── core/                  # 核心算法
│   ├── rag/              # RAG相关算法
│   ├── intent_recognition/ # 意图识别
│   └── quick_qa_base/    # 快速问答基础
├── common/                # 公共组件
│   ├── config.py         # 配置管理
│   ├── utils.py          # 工具函数
│   ├── logging_utils.py  # 日志工具
│   └── constants.py      # 常量定义
├── middleware/            # 中间件
│   ├── cors_middleware.py # CORS中间件
│   ├── logging_middleware.py # 日志中间件
│   └── security_middleware.py # 安全中间件
├── initialize/            # 初始化模块
├── knowledgeBase/         # 知识库存储
├── docs/                  # 文档目录
├── tests/                 # 测试目录
└── main.py               # 应用入口
```

## 快速开始

### 环境要求

- Python 3.8+
- 内存: 4GB+ (推荐 8GB+)
- 磁盘空间: 10GB+
- 操作系统: Windows/Linux/macOS

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd server_new
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
nano .env
```

4. **启动服务**
```bash
python main.py
```

5. **验证安装**
```bash
# 访问健康检查端点
curl http://localhost:8002/api/v1/health

# 或在浏览器中访问
http://localhost:8002/docs
```

### 配置说明

主要配置项（在 `.env` 文件中设置）：

```bash
# 应用配置
APP_NAME="GuiXiaoXiRag FastAPI Service"
APP_VERSION="2.0.0"
HOST="0.0.0.0"
PORT=8002
DEBUG=false

# LLM配置
OPENAI_API_BASE="http://localhost:8100/v1"
OPENAI_CHAT_API_KEY="your_api_key_here"
OPENAI_CHAT_MODEL="qwen14b"

# Embedding配置
OPENAI_EMBEDDING_API_BASE="http://localhost:8200/v1"
OPENAI_EMBEDDING_API_KEY="your_api_key_here"
OPENAI_EMBEDDING_MODEL="embedding_qwen"

# 知识库配置
WORKING_DIR="./knowledgeBase/default"
MAX_FILE_SIZE=52428800  # 50MB

# 日志配置
LOG_LEVEL="INFO"
LOG_DIR="./logs"
```

## 使用指南

### 基础查询

```python
import requests

# 智能查询
response = requests.post("http://localhost:8002/api/v1/query", json={
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "top_k": 10
})

print(response.json())
```

### 文档上传

```python
# 上传文档
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"knowledge_base": "my_kb"}
    response = requests.post(
        "http://localhost:8002/api/v1/insert/file", 
        files=files, 
        data=data
    )
```

### 知识库管理

```python
# 创建知识库
response = requests.post("http://localhost:8002/api/v1/knowledge-bases", json={
    "name": "ai_research",
    "description": "人工智能研究知识库",
    "language": "中文"
})

# 切换知识库
response = requests.post("http://localhost:8002/api/v1/knowledge-bases/switch", json={
    "name": "ai_research"
})
```

### 知识图谱查询

```python
# 获取知识图谱数据
response = requests.post("http://localhost:8002/api/v1/knowledge-graph", json={
    "node_label": "人工智能",
    "max_depth": 3,
    "max_nodes": 100
})
```

## API 文档

### 在线文档
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

### 详细文档
- [完整API文档](docs/API_Documentation.md)
- [测试示例](docs/API_Testing_Examples.md)

### 主要端点

| 分类 | 端点 | 方法 | 描述 |
|------|------|------|------|
| 系统 | `/api/v1/health` | GET | 健康检查 |
| 系统 | `/api/v1/system/status` | GET | 系统状态 |
| 查询 | `/api/v1/query` | POST | 智能查询 |
| 查询 | `/api/v1/query/batch` | POST | 批量查询 |
| 文档 | `/api/v1/insert/text` | POST | 插入文本 |
| 文档 | `/api/v1/insert/file` | POST | 上传文件 |
| 知识库 | `/api/v1/knowledge-bases` | GET | 知识库列表 |
| 知识库 | `/api/v1/knowledge-bases` | POST | 创建知识库 |
| 图谱 | `/api/v1/knowledge-graph` | POST | 获取图谱数据 |
| 图谱 | `/api/v1/knowledge-graph/stats` | GET | 图谱统计 |

## 开发指南

### 项目结构说明

- **api/**: 业务逻辑处理层，包含各功能模块的API处理器
- **routers/**: FastAPI路由定义，负责请求路由和参数验证
- **model/**: 数据模型定义，包括请求/响应模型和基础模型
- **handler/**: 核心业务处理器，实现具体的业务逻辑
- **core/**: 核心算法实现，包括RAG、意图识别等
- **common/**: 公共组件，包括配置、工具、常量等
- **middleware/**: 中间件，处理跨切面关注点

### 添加新功能

1. **定义数据模型** (model/)
2. **实现业务逻辑** (api/)
3. **添加路由定义** (routers/)
4. **注册路由** (main.py)
5. **编写测试** (tests/)

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写完整的文档字符串
- 添加适当的错误处理
- 编写单元测试

## 部署指南

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["python", "main.py"]
```

```bash
# 构建镜像
docker build -t guixiaoxirag .

# 运行容器
docker run -p 8002:8002 -v $(pwd)/knowledgeBase:/app/knowledgeBase guixiaoxirag
```

### 生产环境部署

```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002

# 使用 Supervisor 管理进程
# 配置 nginx 反向代理
# 设置 SSL 证书
```

## 性能优化

### 系统优化
- 启用缓存机制
- 调整并发参数
- 优化数据库查询
- 使用连接池

### 查询优化
- 选择合适的查询模式
- 设置合理的 top_k 值
- 使用批量查询
- 启用重排序

### 资源监控
```python
# 获取性能指标
response = requests.get("http://localhost:8002/api/v1/metrics")
print(response.json())

# 获取缓存统计
response = requests.get("http://localhost:8002/api/v1/cache/stats")
print(response.json())
```

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口占用: `netstat -an | grep 8002`
   - 检查依赖安装: `pip list`
   - 查看错误日志: `tail -f logs/guixiaoxirag_service.log`

2. **查询响应慢**
   - 检查系统资源使用
   - 优化查询参数
   - 清理缓存

3. **文件上传失败**
   - 检查文件大小限制
   - 验证文件格式支持
   - 检查磁盘空间

### 日志查看

```bash
# 查看应用日志
tail -f logs/guixiaoxirag_service.log

# 查看系统日志
curl http://localhost:8002/api/v1/logs?lines=100
```

## 测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api_comprehensive.py -v

# 生成覆盖率报告
pytest --cov=. tests/
```

### API 测试

```bash
# 运行综合API测试
python tests/test_api_comprehensive.py

# 使用curl测试
curl -X GET http://localhost:8002/api/v1/health
```

## 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v2.0.0 (当前版本)
- 重构API架构，提供更清晰的模块化设计
- 增强查询功能，支持多种查询模式
- 完善知识库管理功能
- 新增意图识别和安全检查
- 优化性能和缓存机制
- 完善错误处理和日志记录

### v1.x.x
- 基础功能实现
- 初始版本发布

## 依赖项说明

### 核心依赖
- **FastAPI**: 现代、快速的Web框架
- **Uvicorn**: ASGI服务器
- **Pydantic**: 数据验证和设置管理
- **LightRAG**: 轻量级RAG框架
- **NetworkX**: 图形和网络分析
- **OpenAI**: LLM和Embedding API客户端

### 文档处理
- **PyPDF2/pdfminer**: PDF文档处理
- **python-docx**: Word文档处理
- **BeautifulSoup4**: HTML/XML解析
- **pandas**: 数据处理和分析

### 系统工具
- **psutil**: 系统和进程监控
- **aiofiles**: 异步文件操作
- **python-multipart**: 文件上传支持

## 配置详解

### 环境变量配置

创建 `.env` 文件并配置以下参数：

```bash
# ===================
# 应用基础配置
# ===================
APP_NAME="GuiXiaoXiRag FastAPI Service"
APP_VERSION="2.0.0"
HOST="0.0.0.0"
PORT=8002
DEBUG=false
WORKERS=1

# ===================
# LLM服务配置
# ===================
# LLM API配置
OPENAI_API_BASE="http://localhost:8100/v1"
OPENAI_CHAT_API_KEY="your_api_key_here"
OPENAI_CHAT_MODEL="qwen14b"

# Embedding API配置
OPENAI_EMBEDDING_API_BASE="http://localhost:8200/v1"
OPENAI_EMBEDDING_API_KEY="your_api_key_here"
OPENAI_EMBEDDING_MODEL="embedding_qwen"

# LLM参数配置
LLM_ENABLED=true
LLM_PROVIDER="openai"
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=30

# Embedding参数配置
EMBEDDING_ENABLED=true
EMBEDDING_PROVIDER="openai"
EMBEDDING_DIM=2560
EMBEDDING_TIMEOUT=30

# ===================
# 知识库配置
# ===================
WORKING_DIR="./knowledgeBase/default"
MAX_TOKEN_SIZE=8192

# ===================
# 文件处理配置
# ===================
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR="./uploads"
ALLOWED_FILE_TYPES=".txt,.pdf,.docx,.doc,.md,.json,.xml,.csv"

# ===================
# 性能配置
# ===================
ENABLE_CACHE=true
CACHE_TTL=3600
MAX_CONCURRENT_REQUESTS=100

# ===================
# 安全配置
# ===================
CORS_ORIGINS="*"
CORS_METHODS="*"
CORS_HEADERS="*"

# ===================
# 日志配置
# ===================
LOG_LEVEL="INFO"
LOG_DIR="./logs"

# ===================
# Streamlit配置（可选）
# ===================
STREAMLIT_HOST="0.0.0.0"
STREAMLIT_PORT=8501
STREAMLIT_API_URL="http://localhost:8002"
```

### 高级配置选项

#### Azure OpenAI 配置
```bash
# Azure特定配置
LLM_PROVIDER="azure"
AZURE_API_VERSION="2023-12-01-preview"
AZURE_DEPLOYMENT_NAME="gpt-35-turbo"
```

#### Ollama 配置
```bash
# Ollama本地部署配置
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_CHAT_MODEL="llama2"
OLLAMA_EMBEDDING_MODEL="nomic-embed-text"
```

#### Rerank 配置
```bash
# 重排序服务配置
RERANK_ENABLED=false
RERANK_PROVIDER="openai"
RERANK_MODEL="rerank-multilingual-v3.0"
RERANK_TOP_K=10
```

## 详细使用示例

### 1. 完整的查询流程

```python
import requests
import json

class GuiXiaoXiRagClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()

    def health_check(self):
        """健康检查"""
        response = self.session.get(f"{self.api_base}/health")
        return response.json()

    def query(self, query_text, mode="hybrid", **kwargs):
        """智能查询"""
        data = {
            "query": query_text,
            "mode": mode,
            **kwargs
        }
        response = self.session.post(f"{self.api_base}/query", json=data)
        return response.json()

    def insert_text(self, text, knowledge_base=None, **kwargs):
        """插入文本"""
        data = {
            "text": text,
            "knowledge_base": knowledge_base,
            **kwargs
        }
        response = self.session.post(f"{self.api_base}/insert/text", json=data)
        return response.json()

    def upload_file(self, file_path, knowledge_base=None, **kwargs):
        """上传文件"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"knowledge_base": knowledge_base, **kwargs}
            response = self.session.post(
                f"{self.api_base}/insert/file",
                files=files,
                data=data
            )
        return response.json()

    def create_knowledge_base(self, name, description="", **config):
        """创建知识库"""
        data = {
            "name": name,
            "description": description,
            "config": config
        }
        response = self.session.post(f"{self.api_base}/knowledge-bases", json=data)
        return response.json()

    def switch_knowledge_base(self, name):
        """切换知识库"""
        data = {"name": name}
        response = self.session.post(f"{self.api_base}/knowledge-bases/switch", json=data)
        return response.json()

# 使用示例
client = GuiXiaoXiRagClient()

# 1. 检查服务状态
health = client.health_check()
print(f"服务状态: {health}")

# 2. 创建知识库
kb_result = client.create_knowledge_base(
    name="ai_tutorial",
    description="人工智能教程知识库",
    chunk_size=1024,
    chunk_overlap=50
)
print(f"知识库创建: {kb_result}")

# 3. 切换到新知识库
switch_result = client.switch_knowledge_base("ai_tutorial")
print(f"知识库切换: {switch_result}")

# 4. 插入文档内容
texts = [
    "人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。",
    "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
    "深度学习是机器学习的一个分支，使用神经网络来模拟人脑的学习过程。"
]

for i, text in enumerate(texts):
    result = client.insert_text(
        text=text,
        doc_id=f"ai_doc_{i+1}",
        knowledge_base="ai_tutorial"
    )
    print(f"文档插入 {i+1}: {result.get('success')}")

# 5. 执行查询
queries = [
    "什么是人工智能？",
    "机器学习和深度学习的区别是什么？",
    "如何开始学习AI？"
]

for query in queries:
    result = client.query(
        query_text=query,
        mode="hybrid",
        top_k=5,
        knowledge_base="ai_tutorial"
    )
    print(f"\n查询: {query}")
    if result.get('success'):
        answer = result.get('data', {}).get('answer', '')
        print(f"回答: {answer[:200]}...")
    else:
        print(f"查询失败: {result.get('message')}")
```

### 2. 批量文档处理

```python
import os
import glob

def batch_upload_documents(client, directory_path, knowledge_base):
    """批量上传目录中的文档"""
    supported_extensions = ['.txt', '.pdf', '.docx', '.md', '.json']

    results = []
    for ext in supported_extensions:
        files = glob.glob(os.path.join(directory_path, f"*{ext}"))

        for file_path in files:
            try:
                result = client.upload_file(
                    file_path=file_path,
                    knowledge_base=knowledge_base,
                    extract_metadata=True
                )
                results.append({
                    'file': os.path.basename(file_path),
                    'success': result.get('success'),
                    'message': result.get('message')
                })
                print(f"上传 {os.path.basename(file_path)}: {result.get('success')}")
            except Exception as e:
                results.append({
                    'file': os.path.basename(file_path),
                    'success': False,
                    'message': str(e)
                })
                print(f"上传失败 {os.path.basename(file_path)}: {e}")

    return results

# 使用示例
upload_results = batch_upload_documents(
    client=client,
    directory_path="./documents",
    knowledge_base="ai_tutorial"
)

# 统计结果
successful = sum(1 for r in upload_results if r['success'])
total = len(upload_results)
print(f"\n批量上传完成: {successful}/{total} 成功")
```

### 3. 知识图谱操作

```python
def explore_knowledge_graph(client, node_label="人工智能"):
    """探索知识图谱"""

    # 获取图谱数据
    graph_data = client.session.post(f"{client.api_base}/knowledge-graph", json={
        "node_label": node_label,
        "max_depth": 3,
        "max_nodes": 100,
        "include_metadata": True
    }).json()

    if graph_data.get('success'):
        data = graph_data.get('data', {})
        print(f"节点数量: {data.get('node_count', 0)}")
        print(f"边数量: {data.get('edge_count', 0)}")

        # 显示部分节点信息
        nodes = data.get('nodes', [])[:5]
        for node in nodes:
            print(f"节点: {node.get('label')} (ID: {node.get('id')})")

    # 获取图谱统计
    stats = client.session.get(f"{client.api_base}/knowledge-graph/stats").json()
    if stats.get('success'):
        stats_data = stats.get('data', {})
        print(f"\n图谱统计:")
        print(f"  总节点数: {stats_data.get('node_count', 0)}")
        print(f"  总边数: {stats_data.get('edge_count', 0)}")
        print(f"  图谱密度: {stats_data.get('density', 0):.4f}")

    # 生成可视化
    viz_result = client.session.post(f"{client.api_base}/knowledge-graph/visualize", json={
        "max_nodes": 50,
        "layout": "spring",
        "node_size_field": "degree"
    }).json()

    if viz_result.get('success'):
        viz_data = viz_result.get('data', {})
        html_path = viz_data.get('html_file_path')
        print(f"可视化文件已生成: {html_path}")

# 使用示例
explore_knowledge_graph(client)
```

## 监控和维护

### 系统监控脚本

```python
import time
import psutil
import requests
from datetime import datetime

class SystemMonitor:
    def __init__(self, api_base="http://localhost:8002/api/v1"):
        self.api_base = api_base
        self.session = requests.Session()

    def check_system_health(self):
        """检查系统健康状态"""
        try:
            # API健康检查
            health_response = self.session.get(f"{self.api_base}/health", timeout=5)
            api_healthy = health_response.status_code == 200

            # 系统资源检查
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 获取API指标
            metrics_response = self.session.get(f"{self.api_base}/metrics")
            api_metrics = metrics_response.json() if metrics_response.status_code == 200 else {}

            status = {
                'timestamp': datetime.now().isoformat(),
                'api_healthy': api_healthy,
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'api_metrics': api_metrics.get('data', {}) if api_metrics else {}
            }

            return status

        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'api_healthy': False
            }

    def monitor_loop(self, interval=60):
        """监控循环"""
        print("开始系统监控...")

        while True:
            status = self.check_system_health()

            print(f"\n[{status['timestamp']}]")
            print(f"API状态: {'健康' if status.get('api_healthy') else '异常'}")

            if 'system' in status:
                sys_info = status['system']
                print(f"CPU使用率: {sys_info['cpu_percent']:.1f}%")
                print(f"内存使用率: {sys_info['memory_percent']:.1f}%")
                print(f"磁盘使用率: {sys_info['disk_percent']:.1f}%")

            if 'api_metrics' in status and status['api_metrics']:
                metrics = status['api_metrics']
                print(f"请求总数: {metrics.get('request_count', 0)}")
                print(f"错误率: {metrics.get('error_rate', 0):.2%}")
                print(f"平均响应时间: {metrics.get('avg_response_time', 0):.2f}ms")

            # 检查告警条件
            if 'system' in status:
                sys_info = status['system']
                if sys_info['cpu_percent'] > 80:
                    print("⚠️  CPU使用率过高!")
                if sys_info['memory_percent'] > 85:
                    print("⚠️  内存使用率过高!")
                if sys_info['disk_percent'] > 90:
                    print("⚠️  磁盘空间不足!")

            if not status.get('api_healthy'):
                print("🚨 API服务异常!")

            time.sleep(interval)

# 使用示例
if __name__ == "__main__":
    monitor = SystemMonitor()

    # 单次检查
    status = monitor.check_system_health()
    print(json.dumps(status, indent=2, ensure_ascii=False))

    # 持续监控（可选）
    # monitor.monitor_loop(interval=30)
```

### 缓存管理脚本

```python
def manage_cache(client):
    """缓存管理"""

    # 获取缓存统计
    cache_stats = client.session.get(f"{client.api_base}/cache/stats").json()

    if cache_stats.get('success'):
        stats_data = cache_stats.get('data', {})
        total_memory = stats_data.get('total_memory_mb', 0)

        print(f"缓存总内存使用: {total_memory:.2f} MB")

        caches = stats_data.get('caches', {})
        for cache_type, cache_info in caches.items():
            size_mb = cache_info.get('size_mb', 0)
            hit_rate = cache_info.get('hit_rate', 0)
            print(f"  {cache_type}: {size_mb:.2f} MB, 命中率: {hit_rate:.2%}")

        # 如果内存使用过高，清理缓存
        if total_memory > 1000:  # 超过1GB
            print("内存使用过高，开始清理缓存...")

            # 清理特定类型缓存
            for cache_type in ['llm', 'vector']:
                clear_result = client.session.delete(
                    f"{client.api_base}/cache/clear/{cache_type}"
                ).json()

                if clear_result.get('success'):
                    freed_mb = clear_result.get('data', {}).get('freed_memory_mb', 0)
                    print(f"清理 {cache_type} 缓存，释放 {freed_mb:.2f} MB")

# 使用示例
manage_cache(client)
```
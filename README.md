# GuiXiaoXiRag FastAPI 服务

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)
![Tests](https://img.shields.io/badge/Tests-87.5%25%20Pass-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Test%20Coverage-8%2F8%20Core%20APIs-green.svg)

**GuiXiaoXi检索增强生成（RAG）FastAPI 服务**

*企业级智能问答和知识管理解决方案*

[📖 API 文档](docs/API_Documentation.md) • [🔗 网关对接](docs/gateway_collaboration.md) • [🌐 在线文档](http://localhost:8002/docs) • [🧪 测试套件](tests/system_test/README.md)

</div>

## 项目简介

GuiXiaoXiRag 是一个基于 FastAPI 的智能知识问答系统，集成了知识图谱、向量检索、意图识别等多种AI技术。该系统提供强大的知识管理和智能查询功能，支持多种文档格式的处理和多模态的知识检索。

**核心亮点**：
- 🔍 **智能检索**: 基于RAG架构的文档检索和知识图谱查询
- 💬 **固定问答**: 高精度的预设问答对匹配系统，支持FAQ、客服问答等场景
- 📚 **知识管理**: 多格式文档处理和多知识库管理
- 🚀 **企业级**: 支持网关协同、限流控制、性能监控等企业级功能
- 🧪 **测试保障**: 完整的测试套件

## 主要特性

### 🚀 核心功能
- **智能查询**: 支持多种查询模式（local/global/hybrid/naive/mix/bypass）
- **知识图谱**: 自动构建和管理知识图谱，支持可视化展示
- **文档管理**: 支持多种格式文档的上传、处理和索引
- **意图识别**: 智能分析查询意图和安全级别，支持动态配置管理
- **多知识库**: 支持创建和管理多个独立的知识库
- **固定问答系统**: 基于RAG架构的高精度问答系统，支持预设问答对的精确匹配和文件批量导入（JSON/CSV/Excel）

### 🛠️ 技术特性
- **模块化架构**: 清晰的分层设计，易于维护和扩展
- **异步处理**: 基于 FastAPI 的高性能异步处理
- **缓存机制**: 多层缓存优化，提升查询性能
- **网关协同**: 支持用户优先限流、分层限流与最小请求间隔
- **性能监控**: 完整的性能指标和健康检查
- **测试驱动**: 企业级测试套件，支持详细DEBUG日志和自动化测试

### 📊 支持格式
- **文档格式**: PDF, DOCX, DOC, TXT, MD, JSON, XML, CSV
- **问答导入**: JSON, CSV, Excel格式的问答对批量导入
- **查询模式**: 文本查询、批量查询、流式查询
- **输出格式**: JSON, XML, CSV, HTML可视化

## 系统架构

```
GuiXiaoXiRag/
├── api/                    # API业务逻辑层
├── routers/               # FastAPI路由层
├── model/                 # 数据模型层
├── handler/               # 核心处理器
├── core/                  # 核心算法
│   ├── rag/              # RAG相关算法
│   ├── intent_recognition/ # 意图识别
│   ├── quick_qa_base/    # 优化的问答系统
│   └── common/           # 通用组件（LLM客户端等）
├── common/                # 公共组件
├── middleware/            # 中间件
├── initialize/            # 初始化模块
├── knowledgeBase/         # 知识库存储
├── examples/              # 使用示例
│   └── qa_insert_example/ # 问答导入示例
├── docs/                  # API文档
├── tests/                 # 测试目录
│   ├── system_test/      # 系统测试套件 v0.0.1
│   │   ├── runners/      # 测试运行器
│   │   ├── utils/        # 测试工具类
│   │   ├── config/       # 测试配置
│   │   ├── fixtures/     # 测试数据和工具
│   │   └── logs/         # 测试日志和结果
│   └── unit_tests/       # 单元测试
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
cd GuiXiaoXiRag
```

2. **安装依赖**
```bash
# 安装textract依赖
unzip textract-16.5.zip
cd textract-16.5
pip install .
cd ../

# 安装项目依赖
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件，设置LLM和Embedding服务地址
nano .env
```

4. **启动服务**
```bash
# 使用默认配置启动
python start.py

# 或指定参数启动
python start.py --host 0.0.0.0 --port 8002 --debug
```

5. **验证安装**
```bash
# 访问健康检查端点
curl http://localhost:8002/api/v1/health

# 访问API文档
http://localhost:8002/docs

# 运行系统测试验证功能
cd tests/system_test
python main.py sync --no-text-insert --clean-after
```

### 配置说明

主要配置项（在 `.env` 文件中设置）：

```bash
# 应用配置
APP_NAME="GuiXiaoXiRag FastAPI Service"
APP_VERSION="0.1.0"
HOST="0.0.0.0"
PORT=8002

# LLM配置
OPENAI_API_BASE="http://localhost:8100/v1"
OPENAI_CHAT_API_KEY="your_api_key_here"
OPENAI_CHAT_MODEL="qwen14b"

# Embedding配置
OPENAI_EMBEDDING_API_BASE="http://localhost:8200/v1"
OPENAI_EMBEDDING_API_KEY="your_api_key_here"
OPENAI_EMBEDDING_MODEL="embedding_qwen"

# 知识库配置
DATA_DIR="./data"
WORKING_DIR="./data/knowledgeBase/default"
QA_STORAGE_DIR="./data/Q_A_Base"

# 网关协同配置
ENABLE_PROXY_HEADERS=true
TRUSTED_PROXY_IPS=["10.0.0.0/8","192.168.1.10"]
USER_ID_HEADER=x-user-id
CLIENT_ID_HEADER=x-client-id
USER_TIER_HEADER=x-user-tier
RATE_LIMIT_TIERS={"default":100,"free":60,"pro":600,"enterprise":3000}
MIN_INTERVAL_PER_USER=0.5
```

详细配置说明请参考 [.env.example](.env.example) 文件。
网关对接规范请参考 [Java网关对接文档](docs/gateway_collaboration.md)。

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

### 固定问答系统使用

固定问答系统是一个基于RAG架构的高精度问答模块，专门用于处理预设的问答对。它提供精确匹配和语义相似度匹配两种模式，适用于FAQ、客服问答、知识库问答等场景。

#### 核心特性
- **高精度匹配**: 基于向量相似度的语义匹配，支持0.98高阈值精确匹配
- **多格式导入**: 支持JSON、CSV、Excel格式的批量问答对导入
- **分类管理**: 支持问答对的分类组织和管理
- **批量查询**: 支持单个和批量问答查询
- **统计分析**: 提供详细的问答统计和分析功能

#### 基本使用

```python
# 1. 创建单个问答对
response = requests.post("http://localhost:8002/api/v1/qa/pairs", json={
    "question": "什么是人工智能？",
    "answer": "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。",
    "category": "technology",
    "confidence": 0.95,
    "keywords": ["人工智能", "AI", "机器学习"],
    "source": "技术文档"
})

# 2. 问答查询（语义匹配）
response = requests.post("http://localhost:8002/api/v1/qa/query", json={
    "question": "AI是什么？",
    "top_k": 3,
    "min_similarity": 0.8,  # 相似度阈值
    "category": "technology"  # 可选：指定分类
})

# 3. 批量查询
response = requests.post("http://localhost:8002/api/v1/qa/query/batch", json={
    "questions": [
        "什么是机器学习？",
        "深度学习的应用有哪些？",
        "如何开始学习AI？"
    ],
    "top_k": 2,
    "parallel": True
})

# 4. 批量导入问答对（支持JSON/CSV/Excel）
with open("qa_data.json", "rb") as f:
    files = {"file": f}
    data = {
        "file_type": "json",
        "default_category": "technology",
        "overwrite_existing": "false"  # 是否覆盖已存在的问答对
    }
    response = requests.post(
        "http://localhost:8002/api/v1/qa/import",
        files=files,
        data=data
    )

# 5. 获取问答统计信息
response = requests.get("http://localhost:8002/api/v1/qa/statistics")
print(f"总问答对数: {response.json()['data']['total_pairs']}")
print(f"分类统计: {response.json()['data']['categories']}")

# 6. 获取问答对列表
response = requests.get("http://localhost:8002/api/v1/qa/pairs", params={
    "page": 1,
    "page_size": 10,
    "category": "technology"  # 可选：按分类筛选
})
```

#### 文件导入格式

**JSON格式示例**:
```json
{
  "qa_pairs": [
    {
      "question": "什么是人工智能？",
      "answer": "人工智能是...",
      "category": "technology",
      "confidence": 0.95,
      "keywords": ["AI", "人工智能"],
      "source": "技术文档"
    }
  ]
}
```

**CSV格式示例**:
```csv
question,answer,category,confidence,keywords,source
"什么是人工智能？","人工智能是...","technology",0.95,"AI;人工智能","技术文档"
```

**Excel格式**: 支持多工作表，第一行为字段名，支持中文内容。

## API 文档

### 在线文档
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

### 详细文档
- [完整API文档](docs/API_Documentation.md)
- [网关对接规范](docs/gateway_collaboration.md)
- [API测试示例](docs/API_Testing_Examples.md)

### 主要端点

| 分类 | 端点 | 方法 | 描述 |
|------|------|------|------|
| 系统 | `/api/v1/health` | GET | 健康检查 |
| 查询 | `/api/v1/query` | POST | 智能查询（RAG检索） |
| 文档 | `/api/v1/insert/file` | POST | 上传文件到知识库 |
| 知识库 | `/api/v1/knowledge-bases` | GET/POST | 知识库管理 |
| 图谱 | `/api/v1/knowledge-graph` | POST | 获取图谱数据 |
| **意图识别** | `/api/v1/intent/health` | GET | 意图识别服务健康检查 |
| **意图识别** | `/api/v1/intent/analyze` | POST | 分析查询意图和安全级别 |
| **意图识别** | `/api/v1/intent/safety-check` | POST | 内容安全检查 |
| **意图识别** | `/api/v1/intent/status` | GET | 获取处理器状态 |
| **配置管理** | `/api/v1/intent-config/current` | GET | 获取当前配置 |
| **配置管理** | `/api/v1/intent-config/intent-types` | GET/POST | 意图类型管理 |
| **配置管理** | `/api/v1/intent-config/prompts` | GET/POST | 提示词管理 |
| **配置管理** | `/api/v1/intent-config/safety` | GET/POST | 安全配置管理 |
| **固定问答** | `/api/v1/qa/health` | GET | 问答系统健康检查 |
| **固定问答** | `/api/v1/qa/pairs` | POST | 创建问答对 |
| **固定问答** | `/api/v1/qa/pairs` | GET | 获取问答对列表 |
| **固定问答** | `/api/v1/qa/pairs/{pair_id}` | GET/PUT/DELETE | 问答对详情/更新/删除 |
| **固定问答** | `/api/v1/qa/query` | POST | 单个问答查询 |
| **固定问答** | `/api/v1/qa/query/batch` | POST | 批量问答查询 |
| **固定问答** | `/api/v1/qa/import` | POST | 批量导入问答对 |
| **固定问答** | `/api/v1/qa/export` | GET | 导出问答对 |
| **固定问答** | `/api/v1/qa/statistics` | GET | 问答统计信息 |
| **固定问答** | `/api/v1/qa/categories` | GET | 获取分类列表 |

## 示例和测试

### 🧪 系统测试套件 v0.0.1

GuiXiaoXiRag 配备了企业级的系统测试套件，提供全面的API功能验证和性能监控。

#### 📊 测试覆盖情况
- **测试通过率**: 87.5% (7/8 核心测试通过)
- **API覆盖**: 8个核心API端点全覆盖
- **平均响应时间**: 2.1-7.2秒
- **系统稳定性**: 58+分钟连续运行验证

#### 🔍 核心测试项目
| 测试项目 | 状态 | 平均耗时 | 说明 |
|---------|------|----------|------|
| 🏥 系统健康检查 | ✅ 通过 | ~2.1s | 服务状态、版本信息、运行时间 |
| 🔍 QA系统健康检查 | ✅ 通过 | ~2.1s | QA存储、嵌入状态、问答对统计 |
| ➕ 问答对创建 | ✅ 通过 | ~3.5s | 创建、验证、ID生成 |
| 🔎 QA查询 | ✅ 通过 | ~7.2s | 相似度匹配、结果排序 |
| 📝 文本插入 | ⚠️ 已知问题 | ~2.1s | 文件系统问题，可跳过 |
| 🌐 基本查询 | ✅ 通过 | ~2.1s | 混合模式查询、结果生成 |
| ⚙️ 查询模式获取 | ✅ 通过 | ~2.0s | 6种模式，推荐hybrid |
| 📊 QA统计信息 | ✅ 通过 | ~2.1s | 24个问答对，8个分类 |

#### 🚀 快速测试
```bash
# 进入测试目录
cd tests/system_test

# 推荐的日常测试（快速、稳定）
python main.py sync --no-text-insert --clean-after --verbose

# 完整功能测试（包含慢速操作）
python main.py sync --clean-after --timeout 180

# 查看测试帮助
python main.py --help

# 查看版本信息
python main.py --version
```

#### 🔍 详细DEBUG日志
测试套件提供详细的DEBUG级别日志，包括：
- **HTTP请求详情**: URL、超时、请求头、响应头
- **性能指标**: 响应时间、数据大小、服务器处理时间
- **系统状态**: 服务信息、QA统计、错误诊断
- **异常处理**: 完整的错误堆栈和诊断信息

#### 📋 测试报告
每次测试都会生成详细的JSON报告：
```bash
# 查看最新测试结果
cat logs/sync_test_*.json | jq .summary

# 查看详细日志
cat logs/test_*.log | grep DEBUG | head -20
```

#### 📖 测试文档
- [完整测试指南](tests/system_test/README.md)
- [DEBUG日志使用指南](tests/system_test/DEBUG_LOGGING_GUIDE.md)
- [故障排除指南](tests/system_test/README.md#故障排除)

### 固定问答导入示例
查看 [examples/qa_insert_example](examples/qa_insert_example/) 目录，包含完整的问答导入解决方案：

#### 📋 模板文件
- `qa_template.json` - JSON格式模板（包含字段说明和元数据）
- `qa_template.csv` - CSV格式模板（简洁格式）
- `qa_template.xlsx` - Excel格式模板（多工作表，包含字段说明）

#### 📊 示例数据
- `qa_example.json` - 15条高质量问答示例（技术、教育、效率等分类）
- `qa_example.csv` - 相同数据的CSV格式
- `qa_example.xlsx` - 相同数据的Excel格式（包含统计信息）

#### 🛠️ 导入工具
- `import_example.py` - 单文件导入示例脚本
- `batch_import.py` - 批量导入脚本
- `demo_complete.py` - 完整功能演示脚本

#### 📖 使用文档
- `README.md` - 详细使用说明
- `USAGE_GUIDE.md` - 快速上手指南

#### 快速开始
```bash
# 进入示例目录
cd examples/qa_insert_example

# 运行完整演示
python demo_complete.py

# 或者批量导入所有格式
python batch_import.py
```

### 运行测试

#### 🧪 系统测试（推荐）
```bash
# 进入系统测试目录
cd tests/system_test

# 日常快速测试
python main.py sync --no-text-insert --clean-after

# 完整功能测试
python main.py sync --timeout 180

# 详细调试模式
python main.py sync --verbose --no-text-insert

# 专门的DEBUG测试
python debug_test.py
```

#### 🔬 单元测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行所有单元测试
pytest tests/unit_tests/ -v

# 运行传统API测试
python tests/test_api_comprehensive.py
```

#### 📊 测试结果分析
```bash
# 查看测试摘要
cd tests/system_test
cat logs/sync_test_*.json | jq '.summary'

# 分析性能指标
grep "响应时间" logs/test_*.log

# 查看错误日志
grep -i "error\|失败\|异常" logs/test_*.log
```

## 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t guixiaoxirag .

# 运行容器
docker run -p 8002:8002 -v $(pwd)/knowledgeBase:/app/knowledgeBase guixiaoxirag
```

### 生产环境部署

```bash
# 使用 Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002
```

## 故障排除

### 🚨 常见问题

#### 1. **服务启动失败**
```bash
# 检查端口占用
netstat -an | grep 8002

# 检查依赖安装
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# 查看错误日志
tail -f logs/guixiaoxirag_service.log

# 使用测试套件验证
cd tests/system_test
python main.py sync --no-text-insert
```

#### 2. **查询响应慢**
```bash
# 使用测试套件分析性能
cd tests/system_test
python main.py sync --verbose | grep "响应时间"

# 检查系统资源
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# 优化查询参数
curl -X POST "http://localhost:8002/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "hybrid", "top_k": 3}'
```

#### 3. **文件上传失败**
```bash
# 检查文件大小限制
ls -lh your_file.pdf

# 验证文件格式支持
file your_file.pdf

# 检查磁盘空间
df -h

# 测试文本插入功能
cd tests/system_test
python main.py sync --verbose  # 包含文本插入测试
```

#### 4. **测试失败问题**
```bash
# 查看详细测试日志
cd tests/system_test
python main.py sync --verbose --no-text-insert

# 检查服务连接
curl http://localhost:8002/api/v1/health

# 运行专门的DEBUG测试
python debug_test.py

# 查看测试结果文件
cat logs/sync_test_*.json | jq '.summary'
```

#### 5. **QA查询无匹配结果**
```bash
# 检查相似度阈值设置（当前0.98可能过高）
curl http://localhost:8002/api/v1/qa/statistics

# 添加测试问答对
cd tests/system_test
python main.py sync  # 会自动创建测试问答对

# 查看问答对统计
curl http://localhost:8002/api/v1/qa/statistics | jq '.data'
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

### v0.1.0 (当前版本)
- 重构API架构，提供更清晰的模块化设计
- 增强查询功能，支持多种查询模式（local/global/hybrid/naive/mix/bypass）
- 完善知识库管理功能
- **🧠 意图识别系统优化**:
  - 清理重复的API接口，优化代码结构
  - 分离核心功能和配置管理，提供更清晰的接口边界
  - 支持动态配置管理、热更新和配置验证
  - 提供完整的意图类型、提示词和安全配置管理
- **🎯 新增固定问答系统**:
  - 基于RAG架构的高精度问答匹配（支持0.98高阈值）
  - 支持JSON/CSV/Excel格式的批量导入
  - 提供完整的问答对CRUD操作
  - 支持分类管理和统计分析
  - 包含完整的导入示例和工具脚本
- **🧪 企业级测试套件 v0.0.1**:
  - 87.5%测试通过率，覆盖8个核心API
  - 详细的DEBUG日志系统，支持请求/响应/性能分析
  - 自动化测试流程，支持CI/CD集成
  - 智能清理系统，保持测试环境整洁
  - 完整的故障排除和诊断工具
  - 美化的用户界面和进度跟踪
- **🔗 网关协同**: 支持用户优先限流、分层限流与最小请求间隔
- **⚡ 统一embedding配置**: 使用core.common.llm_client统一管理embedding服务
- **📊 性能优化**: 多层缓存机制，提升查询响应速度

---

**更多详细信息请参考:**
- [API 文档](docs/API_Documentation.md)
- [网关对接规范](docs/gateway_collaboration.md)
- [问答导入示例](examples/qa_insert_example/)
- [系统测试套件](tests/system_test/README.md)
- [DEBUG日志指南](tests/system_test/DEBUG_LOGGING_GUIDE.md)


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
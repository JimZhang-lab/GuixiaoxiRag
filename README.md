# GuiXiaoXiRag FastAPI 服务

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

**GuiXiaoXi检索增强生成（RAG）FastAPI 服务**

*提供企业级的智能问答和知识管理解决方案*

[📖 文档](docs/README.md) • [🚀 快速开始](docs/getting-started/QUICK_START.md) • [🌐 API 文档](http://localhost:8002/docs)

</div>

---

## 🌟 核心特性

### 🧠 智能检索引擎
- **多模式查询**: 支持 6 种查询模式（hybrid、local、global、naive、mix、bypass）
- **知识图谱**: 基于图谱技术，提供关系推理能力
- **语义理解**: 深度语义匹配，精准理解用户意图

### 📚 文档处理系统
- **多格式支持**: TXT、PDF、DOCX、MD、JSON、XML、CSV 等格式
- **批量处理**: 高效的批量文档导入和处理
- **智能解析**: 自动识别文档结构和关键信息

### 🗄️ 知识库管理
- **多租户支持**: 独立的知识库空间，数据隔离
- **动态切换**: 支持运行时切换不同知识库
- **可视化管理**: 知识图谱可视化和交互式管理

### ⚙️ 配置管理
- **动态配置**: 支持运行时配置更新，无需重启服务
- **智能验证**: 自动验证配置有效性和兼容性
- **多提供商支持**: 支持OpenAI、Azure、Ollama等多种服务提供商
- **API和CLI**: 通过API接口或命令行工具管理配置

### 🗑️ 缓存管理
- **智能缓存**: 多层缓存系统，提升查询性能
- **缓存统计**: 实时监控缓存使用情况和性能指标
- **灵活清理**: 支持全量清理和按类型清理缓存
- **内存优化**: 自动垃圾回收和内存使用优化

### 🌍 多语言支持
- **多语言处理**: 支持中文、英文等多种语言
- **跨语言检索**: 支持跨语言知识检索和回答生成

### 🎨 用户界面
- **Web 管理界面**: 基于 Streamlit 的直观管理界面
- **API 文档**: 完整的 Swagger/OpenAPI 文档
- **命令行工具**: 强大的 CLI 工具支持

## 🏗️ 项目架构

```
GuixiaoxiRag/
├── 📁 server/                    # FastAPI 服务端
│   ├── 🚀 api.py                # 主应用入口和路由定义
│   ├── ⚙️ config.py             # 配置管理和环境变量
│   ├── 🧠 guixiaoxirag_service.py # GuiXiaoXiRag 服务封装
│   ├── 📋 models.py             # Pydantic 数据模型
│   ├── 🔧 middleware.py         # 自定义中间件
│   ├── 🛠️ utils.py              # 工具函数和辅助方法
│   ├── 📊 knowledge_base_manager.py # 知识库管理器
│   └── ⚡ performance_config.py  # 性能配置管理
├── 📁 streamlit_app/            # Streamlit Web界面
│   ├── 🎨 main_interface.py     # 主界面
│   ├── 🔧 api_client.py         # API客户端
│   ├── 📊 components.py         # UI组件
│   └── ⚙️ config.py             # 界面配置
├── 📁 test/                     # 测试套件
│   ├── 🧪 test_api.py           # API 接口测试
│   ├── 🧪 test_guixiaoxirag_service.py # 服务层测试
│   └── 🏃 run_tests.py          # 测试运行器
├── 📁 scripts/                  # 脚本工具
│   └── 💻 guixiaoxirag_cli.py   # 命令行工具
├── 📁 examples/                 # 示例代码
│   └── 📘 api_client.py         # API 客户端示例
├── 📁 docs/                     # 项目文档
│   ├── 📁 getting-started/      # 快速上手指南
│   ├── 📁 api/                  # API文档
│   ├── 📁 features/             # 功能指南
│   └── 📁 project/              # 项目信息
├── 📁 deployment/               # 部署配置
│   ├── 🐳 Dockerfile           # Docker镜像
│   ├── 🐙 docker-compose.yml   # 容器编排
│   └── 🌐 nginx/               # 反向代理配置
├── 📁 logs/                     # 日志文件
├── 📁 knowledgeBase/            # 知识库存储
├── 📁 guixiaoxiRag/             # 核心RAG引擎
├── 🎨 start_streamlit.py        # Streamlit Web界面启动器
├── 🚀 main.py                   # 主启动文件
├── 📦 requirements.txt          # Python依赖
├── ⚙️ .env.example              # 环境配置模板
└── 📖 README.md                 # 项目说明
```

### 🔧 核心组件说明

- **🚀 main.py**: 智能启动器，自动环境检查和服务启动
- **🧠 GuiXiaoXiRag服务**: 基于 LightRAG 的核心引擎封装
- **📊 知识库管理器**: 多租户知识库的创建、管理和切换
- **🎨 Web界面**: 基于Streamlit的可视化管理界面
- **💻 CLI工具**: 强大的命令行操作工具
- **📖 完整文档**: 从快速开始到部署运维的全套文档

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd GuixiaoxiRag

# 创建Python环境（推荐Python 3.12+）
conda create -n guixiaoxirag python=3.12
conda activate guixiaoxirag

# 安装依赖
pip install -r requirements.txt

# 安装textract（如果需要处理PDF等文档）
unzip textract-16.5.zip
cd textract-16.5
pip install .
cd ..
```

### 2. 配置设置

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，设置API密钥等
vim .env
```

**重要配置项**（支持用户自定义，未配置时使用默认值）：
- `OPENAI_API_BASE`: LLM服务地址（默认：http://localhost:8100/v1）
- `OPENAI_EMBEDDING_API_BASE`: Embedding服务地址（默认：http://localhost:8200/v1）
- `OPENAI_CHAT_API_KEY`: LLM API密钥（默认：your_api_key_here）
- `OPENAI_EMBEDDING_API_KEY`: Embedding API密钥（默认：your_api_key_here）
- `OPENAI_CHAT_MODEL`: 聊天模型（默认：qwen14b）
- `OPENAI_EMBEDDING_MODEL`: 嵌入模型（默认：embedding_qwen）

**可选的高级配置**：
- `CUSTOM_LLM_PROVIDER`: 自定义LLM提供商（openai, azure, ollama等）
- `CUSTOM_EMBEDDING_PROVIDER`: 自定义Embedding提供商
- `AZURE_API_VERSION`: Azure OpenAI API版本
- `AZURE_DEPLOYMENT_NAME`: Azure部署名称

### 3. 启动服务

```bash
# 使用智能启动器（推荐）
python main.py

# 开发模式
python main.py --reload --log-level debug

# 生产模式
python main.py --workers 4
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8002/health

# 访问API文档
open http://localhost:8002/docs

# 启动Web界面（可选）
streamlit run start_streamlit.py --server.port 8501
open http://localhost:8501

# 验证配置（可选）
python scripts/guixiaoxirag_cli.py service effective-config

# 动态更新配置（可选）
python scripts/guixiaoxirag_cli.py service update-config --llm-model gpt-4 --log-level DEBUG
```

## 📖 使用指南

### 基础使用

```bash
# 插入文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能是计算机科学的一个分支"}'

# 查询知识库
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是人工智能？", "mode": "hybrid"}'

# 上传文件
curl -X POST "http://localhost:8002/insert/file" \
  -F "file=@document.pdf"
```

### 命令行工具

```bash
# 基础操作
python scripts/guixiaoxirag_cli.py health
python scripts/guixiaoxirag_cli.py insert --text "测试文档"
python scripts/guixiaoxirag_cli.py query "什么是人工智能？"

# 知识库管理
python scripts/guixiaoxirag_cli.py kb list
python scripts/guixiaoxirag_cli.py kb create my_kb
python scripts/guixiaoxirag_cli.py kb switch my_kb
```

### Web 管理界面

```bash
# 启动 Streamlit 界面
streamlit run start_streamlit.py --server.port 8501

# 访问界面
open http://localhost:8501
```

**界面功能**: 文档管理、智能查询、知识库管理、系统监控

## 🔧 配置说明

主要配置项（`.env` 文件）：

```env
# 应用信息
APP_NAME=GuiXiaoXiRag FastAPI Service
APP_VERSION=1.0.0

# 服务配置
HOST=0.0.0.0
PORT=8002
DEBUG=false
WORKERS=1

# 大模型配置
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=your_api_key_here
OPENAI_EMBEDDING_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=qwen14b
OPENAI_EMBEDDING_MODEL=embedding_qwen

# Embedding配置
EMBEDDING_DIM=1536
MAX_TOKEN_SIZE=8192

# 知识库配置
WORKING_DIR=./knowledgeBase/default
LOG_LEVEL=INFO
LOG_DIR=./logs

# Streamlit配置
STREAMLIT_HOST=0.0.0.0
STREAMLIT_PORT=8501
STREAMLIT_API_URL=http://localhost:8002
```

详细配置说明请参考：[配置指南](docs/getting-started/CONFIGURATION_GUIDE.md)

## 🧪 测试

```bash
# 运行所有测试
python test/run_tests.py

# API 测试
python test/test_api.py

# 服务测试
python test/test_guixiaoxirag_service.py
```

## ⚙️ 配置管理

```bash
# 查看当前配置
curl http://localhost:8002/service/effective-config

# 动态更新配置
curl -X POST "http://localhost:8002/service/config/update" \
  -H "Content-Type: application/json" \
  -d '{
    "openai_chat_model": "gpt-4",
    "log_level": "DEBUG",
    "embedding_dim": 1536
  }'

# 通过CLI更新配置
python scripts/guixiaoxirag_cli.py service update-config \
  --llm-model gpt-4 \
  --log-level DEBUG \
  --embedding-dim 1536
```

## 📚 文档管理

```bash
# 插入文本到指定知识库
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一个测试文档",
    "knowledge_base": "my_kb",
    "language": "中文"
  }'

# 上传文件到指定知识库
curl -X POST "http://localhost:8002/insert/file" \
  -F "file=@document.pdf" \
  -F "knowledge_base=my_kb" \
  -F "language=中文"

# 智能查询
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "knowledge_base": "my_kb",
    "language": "中文"
  }'
```

## �️ 缓存管理

```bash
# 获取缓存统计信息
curl http://localhost:8002/cache/stats

# 清理所有缓存
curl -X DELETE http://localhost:8002/cache/clear

# 清理指定类型缓存
curl -X DELETE http://localhost:8002/cache/clear/llm
curl -X DELETE http://localhost:8002/cache/clear/vector
curl -X DELETE http://localhost:8002/cache/clear/knowledge_graph
```

## �📊 监控

```bash
# 系统状态
curl http://localhost:8002/system/status

# 性能指标
curl http://localhost:8002/metrics

# 查看日志
curl "http://localhost:8002/logs?lines=100"
```

## 📖 完整文档

### 📚 文档导航
- **🏠 文档中心**: [docs/README.md](docs/README.md) - 完整文档导航
- **🌐 在线API文档**: [http://localhost:8002/docs](http://localhost:8002/docs) - Swagger UI
- **📖 美观API文档**: [http://localhost:8002/redoc](http://localhost:8002/redoc) - ReDoc

### 🚀 快速上手
- **⚡ 快速开始**: [docs/getting-started/QUICK_START.md](docs/getting-started/QUICK_START.md) - 5分钟上手指南
- **⚙️ 配置指南**: [docs/getting-started/CONFIGURATION_GUIDE.md](docs/getting-started/CONFIGURATION_GUIDE.md) - 详细配置说明
- **🚀 部署指南**: [docs/getting-started/DEPLOYMENT_GUIDE.md](docs/getting-started/DEPLOYMENT_GUIDE.md) - 生产环境部署
- **🔧 故障排除**: [docs/getting-started/TROUBLESHOOTING.md](docs/getting-started/TROUBLESHOOTING.md) - 常见问题解决

### 📚 API文档
- **📋 API参考**: [docs/api/API_REFERENCE.md](docs/api/API_REFERENCE.md) - 完整接口文档
- **💡 调用示例**: [docs/api/API_EXAMPLES.md](docs/api/API_EXAMPLES.md) - 实用代码示例

### 🌟 功能指南
- **🎨 Web界面**: [docs/features/STREAMLIT_INTERFACE_GUIDE.md](docs/features/STREAMLIT_INTERFACE_GUIDE.md) - 界面详细指南
- **🚀 主启动器**: [docs/features/MAIN_LAUNCHER_GUIDE.md](docs/features/MAIN_LAUNCHER_GUIDE.md) - 启动文件详解
- **🌍 多语言功能**: [docs/features/KNOWLEDGE_BASE_LANGUAGE_FEATURES.md](docs/features/KNOWLEDGE_BASE_LANGUAGE_FEATURES.md) - 语言和知识库特性

### 📊 项目信息
- **🏗️ 项目架构**: [docs/project/PROJECT_ARCHITECTURE.md](docs/project/PROJECT_ARCHITECTURE.md) - 架构详解
- **📈 项目总结**: [docs/project/PROJECT_SUMMARY.md](docs/project/PROJECT_SUMMARY.md) - 概览和特性

### 🛠️ 工具和示例
- **🎨 Web管理界面**: [start_streamlit.py](start_streamlit.py) - 可视化操作界面
- **💻 命令行工具**: [scripts/guixiaoxirag_cli.py](scripts/guixiaoxirag_cli.py) - CLI工具
- **⚙️ 配置管理**: [scripts/config_manager.py](scripts/config_manager.py) - 配置管理工具
- **📘 API客户端**: [examples/api_client.py](examples/api_client.py) - Python客户端示例


## 🚨 常见问题

### ❓ 服务启动问题
- **端口占用**: 使用 `python main.py --port 8003` 更换端口
- **依赖缺失**: 运行 `pip install -r requirements.txt` 重新安装
- **环境错误**: 确认激活了正确的conda环境

### ❓ 大模型连接问题
- **服务未启动**: 确保LLM服务运行在端口8100，Embedding服务运行在端口8200
- **网络问题**: 检查防火墙和网络连接
- **API密钥**: 验证 `.env` 文件中的API配置

### ❓ 查询和文档问题
- **空结果**: 确保已插入文档并等待处理完成
- **文件上传失败**: 检查文件大小（默认<50MB）和格式支持
- **查询慢**: 尝试使用 `naive` 模式或减少 `top_k` 参数

### ❓ 性能和资源问题
- **内存不足**: 减少 `embedding_dim` 或使用 `basic` 性能模式
- **CPU占用高**: 减少worker数量或启用缓存

**详细排错指南**: [故障排除文档](docs/getting-started/TROUBLESHOOTING.md)



## 📊 项目状态

### 🏆 项目特色
- ✅ **生产就绪**: 完整的企业级 RAG 解决方案
- ✅ **高性能**: 支持高并发查询和大规模文档处理
- ✅ **易部署**: 一键启动，支持 Docker 容器化部署
- ✅ **多语言**: 原生支持中英文等多种语言
- ✅ **可扩展**: 模块化设计，支持自定义扩展

### 📈 技术指标
- **🔍 查询模式**: 6 种智能检索模式
- **📚 文档格式**: 支持 7+ 种主流格式
- **⚡ 响应速度**: 毫秒级查询响应
- **🧪 测试覆盖**: 90%+ 功能测试覆盖率

### 🎯 适用场景
- **🏢 企业知识管理**: 内部文档智能检索和问答
- **🎓 教育科研**: 学术文献管理和研究辅助
- **💼 专业服务**: 法律、医疗、技术等专业领域
- **🤖 智能客服**: 客户服务和 FAQ 自动化



## 🙏 致谢

### 🧠 核心技术
- **[LightRAG](https://github.com/HKUDS/LightRAG)** - 提供强大的 RAG (检索增强生成) 核心技术
- **[FastAPI](https://fastapi.tiangolo.com/)** - 现代、快速的 Python Web 框架
- **[Streamlit](https://streamlit.io/)** - 快速构建数据应用的 Python 库
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - 数据验证和设置管理

### 🌟 特别感谢
- **香港大学数据科学研究所 (HKUDS)** - LightRAG 技术的原创团队
- **开源社区** - 为项目提供了丰富的开源工具和库

---

<div align="center">

**如果这个项目对您有帮助，请考虑给我们一个 ⭐ Star！**

*让我们一起构建更智能的知识管理系统* 🚀

</div>

# GuiXiaoXiRag FastAPI 快速开始

## 🚀 5分钟快速上手

### 前置条件

确保您已经：
- ✅ 安装了Python 3.8+
- ✅ 激活了正确的conda环境：`conda activate guixiaoxirag`
- ✅ 安装了项目依赖：`pip install -r requirements.txt`
- ✅ 配置了大模型服务（LLM和Embedding服务）

### 1. 启动服务

#### 方式一：使用主启动文件（推荐）

```bash
# 使用默认配置启动
python main.py

# 指定参数启动
python main.py --host 0.0.0.0 --port 8002 --workers 1

# 开发模式（自动重载）
python main.py --reload --log-level debug

# 生产模式（多进程）
python main.py --workers 4

# 检查服务状态
python main.py status
```

#### 方式二：直接使用uvicorn

```bash
# 单进程启动
uvicorn server.main:app --host 0.0.0.0 --port 8002

# 开发模式（自动重载）
uvicorn server.main:app --host 0.0.0.0 --port 8002 --reload

# 多进程启动
uvicorn server.main:app --host 0.0.0.0 --port 8002 --workers 4
```

#### 启动方式对比

| 方式 | 命令 | 特点 | 适用场景 |
|------|------|------|----------|
| **主启动文件** | `python main.py` | 🚀 功能完整、自动检查、参数丰富 | **推荐使用** |
| **uvicorn直接** | `uvicorn server.main:app` | ⚡ 简单直接、标准ASGI | 开发调试 |

### 2. 验证服务

#### 基础验证
```bash
# 健康检查
curl http://localhost:8002/health

# 查看服务信息
curl http://localhost:8002/

# 访问API文档
open http://localhost:8002/docs
```

#### 功能验证
```bash
# 插入测试文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"}'

# 查询测试
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是人工智能？", "mode": "hybrid"}'
```

### 3. 启动Web界面（可选）

```bash
# 启动Streamlit管理界面
python start_streamlit.py

# 或使用streamlit命令
streamlit run start_streamlit.py --server.port 8501

# 访问Web界面
open http://localhost:8501
```

### 4. 基本使用流程

#### 文档管理
1. **插入单个文档**
   ```bash
   curl -X POST "http://localhost:8002/insert/text" \
     -H "Content-Type: application/json" \
     -d '{"text": "您的文档内容", "doc_id": "doc_001"}'
   ```

2. **批量插入文档**
   ```bash
   curl -X POST "http://localhost:8002/insert/texts" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["文档1", "文档2"], "doc_ids": ["doc_001", "doc_002"]}'
   ```

3. **上传文件**
   ```bash
   curl -X POST "http://localhost:8002/insert/file" \
     -F "file=@your_document.pdf"
   ```

#### 智能查询
1. **基础查询**
   ```bash
   curl -X POST "http://localhost:8002/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "您的问题", "mode": "hybrid"}'
   ```

2. **指定查询模式**
   ```bash
   # 本地模式（快速）
   curl -X POST "http://localhost:8002/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "您的问题", "mode": "local", "top_k": 5}'
   
   # 全局模式（全面）
   curl -X POST "http://localhost:8002/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "您的问题", "mode": "global", "top_k": 10}'
   ```

#### 知识库管理
1. **查看知识库列表**
   ```bash
   curl http://localhost:8002/knowledge-bases
   ```

2. **创建新知识库**
   ```bash
   curl -X POST "http://localhost:8002/knowledge-bases" \
     -H "Content-Type: application/json" \
     -d '{"name": "my_kb", "description": "我的知识库"}'
   ```

3. **切换知识库**
   ```bash
   curl -X POST "http://localhost:8002/service/switch-kb" \
     -H "Content-Type: application/json" \
     -d '{"knowledge_base": "my_kb", "language": "中文"}'
   ```

### 5. 常用命令

#### 服务管理
```bash
# 查看服务状态
python main.py status

# 重启服务（开发模式）
python main.py --reload

# 生产模式启动
python main.py --workers 4 --host 0.0.0.0

# 查看帮助
python main.py --help
```

#### 配置管理
```bash
# 验证配置
python scripts/config_manager.py --validate

# 查看配置摘要
python scripts/config_manager.py --summary

# 生成配置文件
python scripts/config_manager.py --generate
```

#### 系统监控
```bash
# 查看系统指标
curl http://localhost:8002/metrics

# 查看知识图谱统计
curl http://localhost:8002/knowledge-graph/stats

# 查看日志
curl "http://localhost:8002/logs?lines=50"
```

### 6. 故障排除

#### 常见问题
1. **端口被占用**
   ```bash
   # 使用不同端口
   python main.py --port 8003
   ```

2. **大模型服务连接失败**
   ```bash
   # 检查服务状态
   curl http://localhost:8100/v1/models
   curl http://localhost:8200/v1/models
   ```

3. **配置问题**
   ```bash
   # 验证配置
   python scripts/config_manager.py --validate
   ```

#### 获取帮助
- 查看 [故障排除指南](TROUBLESHOOTING.md)
- 查看 [配置指南](CONFIGURATION_GUIDE.md)
- 访问 API 文档：http://localhost:8002/docs

### 7. 下一步

- 📖 阅读 [配置指南](CONFIGURATION_GUIDE.md) 了解详细配置
- 🚀 查看 [部署指南](DEPLOYMENT_GUIDE.md) 进行生产部署
- 🎨 使用 [Streamlit界面](../features/STREAMLIT_INTERFACE_GUIDE.md) 进行可视化管理
- 📚 参考 [API文档](../api/API_REFERENCE.md) 进行深度集成

## 🔗 相关文档

- [配置指南](CONFIGURATION_GUIDE.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [故障排除](TROUBLESHOOTING.md)
- [API文档](../api/README.md)
- [功能指南](../features/README.md)

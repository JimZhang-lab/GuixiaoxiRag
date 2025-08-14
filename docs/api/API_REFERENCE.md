# GuiXiaoXiRag FastAPI 接口文档

## 📋 目录

- [基础信息](#基础信息)
- [快速开始](#快速开始)
- [认证方式](#认证方式)
- [响应格式](#响应格式)
- [系统管理接口](#系统管理接口)
- [文档管理接口](#文档管理接口)
- [查询接口](#查询接口)
- [知识图谱接口](#知识图谱接口)
- [知识库管理接口](#知识库管理接口)
- [语言管理接口](#语言管理接口)
- [性能优化接口](#性能优化接口)
- [监控接口](#监控接口)
- [错误码说明](#错误码说明)
- [最佳实践](#最佳实践)

## 基础信息

- **基础URL**: `http://localhost:8002`
- **API版本**: v1.0.0
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **交互式文档**: `http://localhost:8002/docs` (Swagger UI)
- **文档**: `http://localhost:8002/redoc` (ReDoc)

## 快速开始

### 1. 启动服务
```bash
# 使用主启动文件（推荐）
python main.py

# 或使用uvicorn
uvicorn server.api:app --host 0.0.0.0 --port 8002
```

### 2. 验证服务
```bash
# 健康检查
curl http://localhost:8002/health

# 访问API文档
open http://localhost:8002/docs
```

### 3. 基本使用流程
```bash
# 1. 插入文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "人工智能是计算机科学的一个分支"}'

# 2. 查询知识库
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是人工智能？", "mode": "hybrid"}'
```

## 认证方式

当前版本无需认证，所有接口均为公开访问。生产环境建议配置适当的认证机制。

## 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体响应数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    // 错误详情
  }
}
```

## 系统管理接口

### 健康检查
- **接口**: `GET /health`
- **描述**: 检查服务健康状态
- **响应**: 服务状态信息

```bash
curl http://localhost:8002/health
```

### 系统状态
- **接口**: `GET /system/status`
- **描述**: 获取详细系统状态
- **响应**: 完整的系统信息

```bash
curl http://localhost:8002/system/status
```

### 系统重置
- **接口**: `POST /system/reset`
- **描述**: 重置系统（清空所有数据）
- **注意**: ⚠️ 危险操作，会清空所有数据

```bash
curl -X POST http://localhost:8002/system/reset
```

## 文档管理接口

### 插入单个文本
- **接口**: `POST /insert/text`
- **描述**: 插入单个文本到知识库

```bash
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "您的文档内容",
    "doc_id": "doc_001",
    "metadata": {"source": "manual"}
  }'
```

### 批量插入文本
- **接口**: `POST /insert/texts`
- **描述**: 批量插入多个文本

```bash
curl -X POST "http://localhost:8002/insert/texts" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["文档1", "文档2"],
    "doc_ids": ["doc_001", "doc_002"]
  }'
```

### 上传文件
- **接口**: `POST /insert/file`
- **描述**: 上传并处理单个文件到指定知识库

```bash
curl -X POST "http://localhost:8002/insert/file" \
  -F "file=@document.pdf" \
  -F "knowledge_base=my_kb" \
  -F "language=中文" \
  -F "track_id=upload_001"
```

**表单参数**：
- `file`: 必填，要上传的文件
- `knowledge_base`: 可选，目标知识库名称
- `language`: 可选，处理语言
- `track_id`: 可选，跟踪ID

### 批量文件上传
- **接口**: `POST /insert/files`
- **描述**: 批量上传多个文件到指定知识库

```bash
curl -X POST "http://localhost:8002/insert/files" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "knowledge_base=my_kb" \
  -F "language=中文"
```

**表单参数**：
- `files`: 必填，要上传的文件列表
- `knowledge_base`: 可选，目标知识库名称
- `language`: 可选，处理语言
- `track_id`: 可选，跟踪ID

### 目录文件处理
- **接口**: `POST /insert/directory`
- **描述**: 处理指定目录下的所有文件

```bash
curl -X POST "http://localhost:8002/insert/directory" \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/path/to/documents"}'
```

## 查询接口

### 基础查询
- **接口**: `POST /query`
- **描述**: 智能知识查询

```bash
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "top_k": 10,
    "max_tokens": 2000
  }'
```

### 查询模式
- **接口**: `GET /query/modes`
- **描述**: 获取支持的查询模式

```bash
curl http://localhost:8002/query/modes
```

### 批量查询
- **接口**: `POST /query/batch`
- **描述**: 批量处理多个查询

```bash
curl -X POST "http://localhost:8002/query/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["问题1", "问题2"],
    "mode": "hybrid"
  }'
```

### 优化查询
- **接口**: `POST /query/optimized`
- **描述**: 使用优化参数进行查询

```bash
curl -X POST "http://localhost:8002/query/optimized" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "您的问题",
    "performance_level": "balanced"
  }'
```

## 知识图谱接口

### 获取知识图谱
- **接口**: `POST /knowledge-graph`
- **描述**: 获取知识图谱数据

```bash
curl -X POST "http://localhost:8002/knowledge-graph" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能",
    "max_depth": 2
  }'
```

### 图谱统计
- **接口**: `GET /knowledge-graph/stats`
- **描述**: 获取知识图谱统计信息

```bash
curl http://localhost:8002/knowledge-graph/stats
```

### 清空图谱
- **接口**: `DELETE /knowledge-graph/clear`
- **描述**: 清空知识图谱数据
- **注意**: ⚠️ 危险操作

```bash
curl -X DELETE http://localhost:8002/knowledge-graph/clear
```

## 知识图谱可视化接口

### 图谱状态
- **接口**: `GET /knowledge-graph/status`
- **描述**: 获取知识图谱文件状态

```bash
curl "http://localhost:8002/knowledge-graph/status?knowledge_base=default"
```

### 格式转换
- **接口**: `POST /knowledge-graph/convert`
- **描述**: 转换GraphML到JSON格式

```bash
curl -X POST "http://localhost:8002/knowledge-graph/convert?knowledge_base=default"
```

### 获取图谱数据
- **接口**: `POST /knowledge-graph/data`
- **描述**: 获取图谱数据（JSON或GraphML格式）

```bash
curl -X POST "http://localhost:8002/knowledge-graph/data" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base": "default",
    "format": "json"
  }'
```

### 生成可视化
- **接口**: `POST /knowledge-graph/visualize`
- **描述**: 生成知识图谱可视化

```bash
curl -X POST "http://localhost:8002/knowledge-graph/visualize" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base": "default",
    "max_nodes": 100,
    "layout": "spring"
  }'
```

### 列出图谱文件
- **接口**: `GET /knowledge-graph/files`
- **描述**: 列出知识库中的图谱文件

```bash
curl "http://localhost:8002/knowledge-graph/files?knowledge_base=default"
```

## 知识库管理接口

### 列出知识库
- **接口**: `GET /knowledge-bases`
- **描述**: 获取所有知识库列表

```bash
curl http://localhost:8002/knowledge-bases
```

### 创建知识库
- **接口**: `POST /knowledge-bases`
- **描述**: 创建新的知识库

```bash
curl -X POST "http://localhost:8002/knowledge-bases" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_knowledge_base",
    "description": "我的知识库"
  }'
```

### 删除知识库
- **接口**: `DELETE /knowledge-bases/{name}`
- **描述**: 删除指定知识库
- **注意**: ⚠️ 危险操作

```bash
curl -X DELETE http://localhost:8002/knowledge-bases/my_kb
```

### 切换知识库
- **接口**: `POST /knowledge-bases/switch`
- **描述**: 切换当前使用的知识库

```bash
curl -X POST "http://localhost:8002/knowledge-bases/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "target_kb",
    "language": "中文"
  }'
```

### 导出知识库
- **接口**: `GET /knowledge-bases/{name}/export`
- **描述**: 导出知识库数据

```bash
curl http://localhost:8002/knowledge-bases/my_kb/export
```

## 语言管理接口

### 获取支持语言
- **接口**: `GET /languages`
- **描述**: 获取支持的语言列表

```bash
curl http://localhost:8002/languages
```

### 设置语言
- **接口**: `POST /languages/set`
- **描述**: 设置默认回答语言

```bash
curl -X POST "http://localhost:8002/languages/set" \
  -H "Content-Type: application/json" \
  -d '{"language": "中文"}'
```

## 性能优化接口

### 性能优化
- **接口**: `POST /performance/optimize`
- **描述**: 执行性能优化

```bash
curl -X POST "http://localhost:8002/performance/optimize" \
  -H "Content-Type: application/json" \
  -d '{"mode": "balanced"}'
```

### 性能配置
- **接口**: `GET /performance/configs`
- **描述**: 获取性能配置选项

```bash
curl http://localhost:8002/performance/configs
```

## 监控接口

### 系统指标
- **接口**: `GET /metrics`
- **描述**: 获取系统性能指标

```bash
curl http://localhost:8002/metrics
```

### 日志查看
- **接口**: `GET /logs`
- **描述**: 获取系统日志

```bash
curl "http://localhost:8002/logs?lines=100&level=ERROR"
```

### 服务配置
- **接口**: `GET /service/config`
- **描述**: 获取当前服务配置

```bash
curl http://localhost:8002/service/config
```

### 有效配置
- **接口**: `GET /service/effective-config`
- **描述**: 获取完整的有效配置信息（包含用户自定义和默认值）

```bash
curl http://localhost:8002/service/effective-config
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "app_name": "GuiXiaoXiRag FastAPI Service",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8002,
    "llm": {
      "api_base": "http://localhost:8100/v1",
      "api_key": "***",
      "model": "qwen14b",
      "provider": "openai"
    },
    "embedding": {
      "api_base": "http://localhost:8200/v1",
      "api_key": "***",
      "model": "embedding_qwen",
      "dim": 1536,
      "provider": "openai"
    }
  }
}
```

### 更新服务配置
- **接口**: `POST /service/config/update`
- **描述**: 动态更新服务配置，支持运行时配置修改

```bash
curl -X POST "http://localhost:8002/service/config/update" \
  -H "Content-Type: application/json" \
  -d '{
    "openai_chat_model": "gpt-4",
    "log_level": "DEBUG",
    "embedding_dim": 1536
  }'
```

**请求参数**：
- `openai_api_base`: LLM API基础URL
- `openai_embedding_api_base`: Embedding API基础URL
- `openai_chat_api_key`: LLM API密钥
- `openai_embedding_api_key`: Embedding API密钥
- `openai_chat_model`: LLM模型名称
- `openai_embedding_model`: Embedding模型名称
- `embedding_dim`: Embedding维度
- `max_token_size`: 最大Token数
- `log_level`: 日志级别
- `custom_llm_provider`: 自定义LLM提供商
- `custom_embedding_provider`: 自定义Embedding提供商
- `azure_api_version`: Azure API版本
- `azure_deployment_name`: Azure部署名称

**响应示例**：
```json
{
  "success": true,
  "message": "配置更新成功",
  "data": {
    "updated_fields": ["openai_chat_model", "log_level"],
    "effective_config": {
      "llm": {
        "model": "gpt-4",
        "api_base": "https://api.openai.com/v1"
      }
    },
    "restart_required": false
  }
}
```

### 切换服务知识库
- **接口**: `POST /service/switch-kb`
- **描述**: 切换服务使用的知识库

```bash
curl -X POST "http://localhost:8002/service/switch-kb" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base": "new_kb",
    "language": "中文"
  }'
```

## 错误码说明

| 错误码 | HTTP状态码 | 描述 | 解决方案 |
|--------|------------|------|----------|
| VALIDATION_ERROR | 422 | 请求参数验证失败 | 检查请求参数格式 |
| NOT_FOUND | 404 | 资源不存在 | 确认资源路径正确 |
| INTERNAL_ERROR | 500 | 服务器内部错误 | 查看服务器日志 |
| SERVICE_UNAVAILABLE | 503 | 服务不可用 | 检查服务状态 |

## 最佳实践

### 1. 错误处理
```python
import requests

try:
    response = requests.post(
        "http://localhost:8002/query",
        json={"query": "test", "mode": "hybrid"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    
    if result.get("success"):
        data = result.get("data")
        # 处理成功响应
    else:
        # 处理业务错误
        print(f"Error: {result.get('message')}")
        
except requests.exceptions.RequestException as e:
    # 处理网络错误
    print(f"Request failed: {e}")
```

### 2. 批量操作
```python
# 推荐：使用批量接口
texts = ["文档1", "文档2", "文档3"]
response = requests.post(
    "http://localhost:8002/insert/texts",
    json={"texts": texts}
)

# 避免：循环调用单个接口
for text in texts:
    requests.post(
        "http://localhost:8002/insert/text",
        json={"text": text}
    )
```

### 3. 查询优化
```python
# 根据需求选择合适的查询模式
query_configs = {
    "fast": {"mode": "naive", "top_k": 5},
    "balanced": {"mode": "hybrid", "top_k": 10},
    "comprehensive": {"mode": "global", "top_k": 20}
}

config = query_configs["balanced"]
response = requests.post(
    "http://localhost:8002/query",
    json={"query": "your question", **config}
)
```

### 4. 文件上传
```python
# 单文件上传
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8002/insert/file",
        files=files
    )

# 多文件上传
files = [
    ("files", open("doc1.pdf", "rb")),
    ("files", open("doc2.docx", "rb"))
]
response = requests.post(
    "http://localhost:8002/insert/files",
    files=files
)
```

## 缓存管理接口

### 获取缓存统计
- **接口**: `GET /cache/stats`
- **描述**: 获取系统中各种缓存的统计信息

```bash
curl http://localhost:8002/cache/stats
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "total_memory_mb": 512.3,
    "caches": {
      "llm_response": {
        "size_mb": 128.5,
        "item_count": 256,
        "hit_rate": 0.85
      },
      "vector": {
        "size_mb": 256.8,
        "item_count": 1024,
        "hit_rate": 0.92
      }
    },
    "system_memory": {
      "total_mb": 8192,
      "available_mb": 4096,
      "used_percent": 50.0
    }
  }
}
```

### 清理所有缓存
- **接口**: `DELETE /cache/clear`
- **描述**: 清理系统中的所有缓存数据

```bash
curl -X DELETE http://localhost:8002/cache/clear
```

**响应示例**：
```json
{
  "success": true,
  "message": "缓存清理成功",
  "data": {
    "cleared_caches": ["llm_response", "vector", "knowledge_graph"],
    "freed_memory_mb": 256.5,
    "gc_collected_objects": 128,
    "cache_stats": {
      "before": {"memory_mb": 512.3},
      "after": {"memory_mb": 255.8}
    }
  }
}
```

### 清理指定类型缓存
- **接口**: `DELETE /cache/clear/{cache_type}`
- **描述**: 清理指定类型的缓存数据

**支持的缓存类型**：
- `llm`: LLM响应缓存
- `vector`: 向量计算缓存
- `knowledge_graph`: 知识图谱缓存
- `documents`: 文档处理缓存
- `queries`: 查询结果缓存

```bash
# 清理LLM缓存
curl -X DELETE http://localhost:8002/cache/clear/llm

# 清理向量缓存
curl -X DELETE http://localhost:8002/cache/clear/vector

# 清理知识图谱缓存
curl -X DELETE http://localhost:8002/cache/clear/knowledge_graph
```

**响应示例**：
```json
{
  "success": true,
  "message": "LLM缓存清理成功",
  "data": {
    "cache_type": "llm",
    "cleared_items": 128,
    "gc_collected_objects": 64,
    "freed_memory_mb": 64.2
  }
}
```

## 🔗 相关文档

- [API调用示例](API_EXAMPLES.md)
- [快速开始指南](../getting-started/QUICK_START.md)
- [配置指南](../getting-started/CONFIGURATION_GUIDE.md)
- [故障排除指南](../getting-started/TROUBLESHOOTING.md)

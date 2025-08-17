# GuiXiaoXiRag FastAPI 服务 API 文档

## 项目概述

GuiXiaoXiRag 是一个基于 FastAPI 的智能知识问答系统，集成了知识图谱、向量检索、意图识别等多种AI技术，提供强大的知识管理和智能查询功能。

## 服务信息

- **服务名称**: GuiXiaoXiRag FastAPI Service
- **版本**: 2.0.0
- **默认端口**: 8002
- **API 基础路径**: `/api/v1`
- **文档地址**: `/docs` (Swagger UI)
- **ReDoc 地址**: `/redoc`

## 认证方式

当前版本暂不需要认证，所有API端点均可直接访问。

## 通用响应格式

所有API响应都遵循统一的格式：

```json
{
    "success": true,
    "message": "操作成功",
    "data": {
        // 具体的响应数据
    },
    "error_code": null,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## API 端点分类

### 1. 系统管理 API

#### 1.1 健康检查

**端点**: `GET /api/v1/health`

**描述**: 检查系统的整体健康状态和各组件运行情况

**响应示例**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "system": {
        "service_name": "GuiXiaoXiRag FastAPI Service",
        "version": "2.0.0",
        "uptime": 3600
    },
    "dependencies": {
        "database": "healthy",
        "file_system": "healthy",
        "llm_service": "healthy"
    }
}
```

#### 1.2 系统状态

**端点**: `GET /api/v1/system/status`

**描述**: 获取系统的详细运行状态和配置信息

**响应示例**:
```json
{
    "success": true,
    "data": {
        "service_name": "GuiXiaoXiRag FastAPI Service",
        "version": "2.0.0",
        "status": "running",
        "initialized": true,
        "working_dir": "./knowledgeBase/default",
        "uptime": 3600,
        "performance": {
            "cpu_usage": 15.2,
            "memory_usage": 512.5
        }
    }
}
```

#### 1.3 性能指标

**端点**: `GET /api/v1/metrics`

**描述**: 获取系统的性能监控指标和统计信息

**响应示例**:
```json
{
    "success": true,
    "data": {
        "request_count": 1024,
        "error_count": 5,
        "error_rate": 0.0049,
        "avg_response_time": 250.5,
        "response_time_percentiles": {
            "p50": 200,
            "p95": 500,
            "p99": 1000
        },
        "resource_usage": {
            "cpu_percent": 15.2,
            "memory_mb": 512.5,
            "disk_usage_percent": 45.8
        }
    }
}
```

#### 1.4 系统日志

**端点**: `GET /api/v1/logs?lines=100`

**参数**:
- `lines` (可选): 日志行数，默认100，最大1000

**描述**: 获取系统的最近日志记录

#### 1.5 配置管理

**端点**: `GET /api/v1/service/config`

**描述**: 获取当前服务配置

**端点**: `POST /api/v1/service/config/update`

**描述**: 更新服务配置

**请求体示例**:
```json
{
    "openai_api_base": "http://localhost:8100/v1",
    "openai_chat_model": "qwen14b",
    "log_level": "INFO"
}
```

### 2. 查询 API

#### 2.1 智能知识查询

**端点**: `POST /api/v1/query`

**描述**: 基于知识图谱的智能查询，支持多种查询模式

**请求体**:
```json
{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "top_k": 20,
    "knowledge_base": "ai_kb",
    "language": "中文",
    "performance_mode": "balanced"
}
```

**参数说明**:
- `query` (必填): 查询内容
- `mode` (可选): 查询模式，支持 local/global/hybrid/naive/mix/bypass
- `top_k` (可选): 返回结果数量，默认20
- `stream` (可选): 是否流式返回，默认false
- `knowledge_base` (可选): 知识库名称
- `language` (可选): 回答语言
- `performance_mode` (可选): 性能模式，支持 fast/balanced/quality

**响应示例**:
```json
{
    "success": true,
    "data": {
        "answer": "人工智能（AI）是计算机科学的一个分支...",
        "sources": [
            {
                "content": "相关文档内容",
                "score": 0.95,
                "metadata": {}
            }
        ],
        "query_time": 1.25,
        "mode": "hybrid"
    }
}
```

#### 2.2 查询意图分析

**端点**: `POST /api/v1/query/analyze`

**描述**: 分析查询的意图类型、安全级别，并提供查询优化建议

**请求体**:
```json
{
    "query": "如何学习机器学习？",
    "context": {"domain": "education"},
    "enable_enhancement": true,
    "safety_check": true
}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "intent_type": "knowledge_query",
        "safety_level": "safe",
        "confidence": 0.95,
        "enhanced_query": "如何系统性地学习机器学习的基础知识和实践技能？",
        "suggestions": ["建议从基础数学开始", "推荐实践项目"]
    }
}
```

#### 2.3 安全智能查询

**端点**: `POST /api/v1/query/safe`

**描述**: 结合意图分析和安全检查的智能查询

**请求体**:
```json
{
    "query": "人工智能的发展历史",
    "mode": "hybrid",
    "enable_intent_analysis": true,
    "enable_query_enhancement": true,
    "safety_check": true
}
```

#### 2.4 批量查询

**端点**: `POST /api/v1/query/batch`

**描述**: 批量处理多个查询请求

**请求体**:
```json
{
    "queries": [
        "什么是机器学习？",
        "深度学习的应用领域有哪些？",
        "如何选择合适的算法？"
    ],
    "mode": "hybrid",
    "parallel": true,
    "timeout": 300
}
```

#### 2.5 查询模式列表

**端点**: `GET /api/v1/query/modes`

**描述**: 获取所有支持的查询模式及其详细说明

### 3. 文档管理 API

#### 3.1 插入单个文本

**端点**: `POST /api/v1/insert/text`

**描述**: 插入单个文本文档到指定知识库

**请求体**:
```json
{
    "text": "这是一段要插入的文本内容",
    "knowledge_base": "my_kb",
    "language": "中文"
}
```

#### 3.2 批量插入文本

**端点**: `POST /api/v1/insert/texts`

**描述**: 批量插入多个文本文档

**请求体**:
```json
{
    "texts": [
        "第一段文本内容",
        "第二段文本内容",
        "第三段文本内容"
    ],
    "knowledge_base": "my_kb",
    "language": "中文"
}
```

#### 3.3 上传文件

**端点**: `POST /api/v1/insert/file`

**描述**: 上传单个文件并插入到知识库

**请求**: multipart/form-data
- `file`: 上传的文件
- `knowledge_base`: 目标知识库名称
- `language`: 处理语言
- `extract_metadata`: 是否提取元数据

**支持的文件格式**:
- 文本文件: .txt, .md
- 文档文件: .pdf, .docx, .doc
- 数据文件: .json, .xml, .csv

#### 3.4 批量上传文件

**端点**: `POST /api/v1/insert/files`

**描述**: 批量上传多个文件

#### 3.5 从目录插入

**端点**: `POST /api/v1/insert/directory`

**描述**: 从指定目录读取所有支持的文件并插入到知识库

**请求体**:
```json
{
    "directory_path": "/path/to/documents",
    "knowledge_base": "my_kb",
    "recursive": true,
    "file_patterns": ["*.pdf", "*.txt"]
}
```

### 4. 知识库管理 API

#### 4.1 获取知识库列表

**端点**: `GET /api/v1/knowledge-bases`

**描述**: 获取所有可用知识库的列表和详细信息

**响应示例**:
```json
{
    "success": true,
    "data": {
        "knowledge_bases": [
            {
                "name": "default",
                "description": "默认知识库",
                "status": "ready",
                "document_count": 150,
                "node_count": 1200,
                "edge_count": 3500,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total_count": 1,
        "current_kb": "default"
    }
}
```

#### 4.2 创建知识库

**端点**: `POST /api/v1/knowledge-bases`

**描述**: 创建一个新的知识库

**请求体**:
```json
{
    "name": "ai_research",
    "description": "人工智能研究知识库",
    "language": "中文",
    "config": {
        "chunk_size": 1024,
        "chunk_overlap": 50,
        "enable_auto_update": true
    }
}
```

#### 4.3 删除知识库

**端点**: `DELETE /api/v1/knowledge-bases/{name}?force=false`

**描述**: 删除指定的知识库

**参数**:
- `name`: 知识库名称
- `force`: 是否强制删除

#### 4.4 切换知识库

**端点**: `POST /api/v1/knowledge-bases/switch`

**描述**: 切换到指定的知识库

**请求体**:
```json
{
    "name": "ai_research",
    "create_if_not_exists": false
}
```

#### 4.5 获取当前知识库信息

**端点**: `GET /api/v1/knowledge-bases/current`

**描述**: 获取当前正在使用的知识库信息

#### 4.6 更新知识库配置

**端点**: `PUT /api/v1/knowledge-bases/{name}/config`

**描述**: 更新指定知识库的配置参数

#### 4.7 备份知识库

**端点**: `POST /api/v1/knowledge-bases/{name}/backup`

**描述**: 创建指定知识库的完整备份

#### 4.8 恢复知识库

**端点**: `POST /api/v1/knowledge-bases/{name}/restore`

**描述**: 从备份文件恢复知识库

### 5. 知识图谱 API

#### 5.1 获取知识图谱数据

**端点**: `POST /api/v1/knowledge-graph`

**描述**: 根据指定节点标签获取知识图谱的子图数据

**请求体**:
```json
{
    "node_label": "人工智能",
    "max_depth": 3,
    "max_nodes": 100,
    "include_metadata": true
}
```

**响应示例**:
```json
{
    "success": true,
    "data": {
        "nodes": [
            {
                "id": "node_1",
                "label": "人工智能",
                "properties": {},
                "type": "concept"
            }
        ],
        "edges": [
            {
                "source": "node_1",
                "target": "node_2",
                "relationship": "包含",
                "properties": {}
            }
        ],
        "node_count": 50,
        "edge_count": 120,
        "metadata": {}
    }
}
```

#### 5.2 获取图谱统计信息

**端点**: `GET /api/v1/knowledge-graph/stats`

**描述**: 获取当前知识库的知识图谱统计信息

#### 5.3 清空知识图谱

**端点**: `DELETE /api/v1/knowledge-graph/clear`

**描述**: 清空当前知识库的知识图谱数据

#### 5.4 获取图谱状态

**端点**: `GET /api/v1/knowledge-graph/status`

**描述**: 获取知识图谱文件状态信息

#### 5.5 转换图谱格式

**端点**: `POST /api/v1/knowledge-graph/convert`

**描述**: 将GraphML格式转换为JSON格式

#### 5.6 图谱可视化

**端点**: `POST /api/v1/knowledge-graph/visualize`

**描述**: 生成知识图谱的交互式可视化HTML页面

**请求体**:
```json
{
    "knowledge_base": "my_kb",
    "max_nodes": 100,
    "layout": "spring",
    "node_size_field": "degree",
    "edge_width_field": "weight"
}
```

### 6. 意图识别 API

#### 6.1 健康检查

**端点**: `GET /api/v1/intent/health`

**描述**: 检查意图识别服务的健康状态

#### 6.2 意图分析

**端点**: `POST /api/v1/intent/analyze`

**描述**: 分析查询的意图类型、安全级别并提供增强建议

**请求体**:
```json
{
    "query": "如何学习Python编程？",
    "context": {"domain": "programming"}
}
```

#### 6.3 安全检查

**端点**: `POST /api/v1/intent/safety-check`

**描述**: 检查内容的安全性，识别潜在风险

**请求体**:
```json
{
    "content": "要检查的内容",
    "check_type": "query"
}
```

#### 6.4 获取意图类型

**端点**: `GET /api/v1/intent/intent-types`

**描述**: 获取支持的意图类型列表

#### 6.5 获取安全级别

**端点**: `GET /api/v1/intent/safety-levels`

**描述**: 获取支持的安全级别列表

### 7. 缓存管理 API

#### 7.1 清理所有缓存

**端点**: `DELETE /api/v1/cache/clear`

**描述**: 清理系统中的所有缓存数据

#### 7.2 清理指定缓存

**端点**: `DELETE /api/v1/cache/clear/{cache_type}`

**描述**: 清理指定类型的缓存数据

**支持的缓存类型**:
- `llm`: LLM响应缓存
- `vector`: 向量计算缓存
- `knowledge_graph`: 知识图谱缓存
- `documents`: 文档处理缓存
- `queries`: 查询结果缓存

#### 7.3 获取缓存统计

**端点**: `GET /api/v1/cache/stats`

**描述**: 获取系统中各种缓存的统计信息

## 错误处理

### 错误响应格式

```json
{
    "success": false,
    "message": "错误描述",
    "error_code": "ERROR_CODE",
    "details": {},
    "path": "/api/v1/endpoint"
}
```

### 常见错误码

- `400`: 请求参数错误
- `404`: 资源不存在
- `422`: 请求验证失败
- `500`: 服务器内部错误

## 使用示例

### Python 客户端示例

```python
import requests

# 基础配置
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api/v1"

# 健康检查
response = requests.get(f"{API_BASE}/health")
print(response.json())

# 智能查询
query_data = {
    "query": "什么是机器学习？",
    "mode": "hybrid",
    "top_k": 10
}
response = requests.post(f"{API_BASE}/query", json=query_data)
print(response.json())

# 上传文件
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"knowledge_base": "my_kb"}
    response = requests.post(f"{API_BASE}/insert/file", files=files, data=data)
    print(response.json())
```

### JavaScript 客户端示例

```javascript
const BASE_URL = "http://localhost:8002";
const API_BASE = `${BASE_URL}/api/v1`;

// 智能查询
async function query(queryText) {
    const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: queryText,
            mode: 'hybrid',
            top_k: 10
        })
    });
    return await response.json();
}

// 获取知识库列表
async function getKnowledgeBases() {
    const response = await fetch(`${API_BASE}/knowledge-bases`);
    return await response.json();
}
```

## 性能优化建议

1. **查询优化**:
   - 使用合适的查询模式
   - 设置合理的 top_k 值
   - 启用缓存机制

2. **文件上传**:
   - 批量上传多个小文件
   - 使用支持的文件格式
   - 合理设置文件大小限制

3. **知识库管理**:
   - 定期备份重要数据
   - 合理配置分块参数
   - 监控存储空间使用

4. **系统监控**:
   - 定期检查系统健康状态
   - 监控性能指标
   - 及时清理缓存

## 版本更新日志

### v2.0.0
- 重构API架构，提供更清晰的模块化设计
- 增强查询功能，支持多种查询模式
- 完善知识库管理功能
- 新增意图识别和安全检查
- 优化性能和缓存机制
- 完善错误处理和日志记录

## 技术支持

如有问题或建议，请通过以下方式联系：

- 查看项目文档: `/docs`
- 在线API文档: `/docs` (Swagger UI)
- 项目仓库: [GitHub链接]

---

*本文档最后更新时间: 2024-01-01*

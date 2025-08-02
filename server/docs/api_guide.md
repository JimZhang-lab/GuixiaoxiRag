# GuiXiaoXiRag FastAPI 服务 API 文档

## 概述

GuiXiaoXiRag FastAPI 服务提供了基于知识图谱的检索增强生成（RAG）功能。本服务封装了 GuiXiaoXiRag 的核心功能，提供了简单易用的 REST API 接口。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1.0.0
- **文档地址**: `http://localhost:8000/docs`
- **OpenAPI规范**: `http://localhost:8000/openapi.json`

## 认证

当前版本不需要认证，所有API端点都是公开的。

## 响应格式

所有API响应都遵循统一的格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体的响应数据
  }
}
```

错误响应格式：

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

## API 端点

### 1. 系统管理

#### 健康检查
- **端点**: `GET /health`
- **描述**: 检查服务健康状态
- **响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "system": {
    "service_name": "GuiXiaoXiRag FastAPI Service",
    "version": "1.0.0",
    "status": "running",
    "initialized": true,
    "working_dir": "./knowledgeBase/default",
    "uptime": 3600.5
  }
}
```

#### 系统状态
- **端点**: `GET /system/status`
- **描述**: 获取详细的系统状态信息

#### 系统重置
- **端点**: `POST /system/reset`
- **描述**: 重置系统，清空所有数据

### 2. 文档管理

#### 插入单个文本
- **端点**: `POST /insert/text`
- **描述**: 插入单个文本文档到知识库
- **请求体**:
```json
{
  "text": "要插入的文本内容",
  "doc_id": "可选的文档ID",
  "file_path": "可选的文件路径",
  "track_id": "可选的跟踪ID"
}
```
- **响应示例**:
```json
{
  "success": true,
  "data": {
    "track_id": "insert_20240101_120000_abc123",
    "message": "插入成功"
  }
}
```

#### 批量插入文本
- **端点**: `POST /insert/texts`
- **描述**: 批量插入多个文本文档
- **请求体**:
```json
{
  "texts": ["文本1", "文本2", "文本3"],
  "doc_ids": ["doc1", "doc2", "doc3"],
  "file_paths": ["path1", "path2", "path3"],
  "track_id": "可选的跟踪ID"
}
```

#### 文件上传
- **端点**: `POST /insert/file`
- **描述**: 上传并插入文件（支持 .txt, .pdf, .docx, .doc）
- **请求**: multipart/form-data
- **参数**: `file` (文件)

#### 批量文件上传
- **端点**: `POST /insert/files`
- **描述**: 批量上传并插入多个文件

#### 目录插入
- **端点**: `POST /insert/directory`
- **描述**: 从指定目录插入所有支持的文件
- **参数**: `directory_path` (字符串)

### 3. 查询功能

#### 基础查询
- **端点**: `POST /query`
- **描述**: 执行知识库查询
- **请求体**:
```json
{
  "query": "查询问题",
  "mode": "hybrid",
  "top_k": 20,
  "stream": false,
  "only_need_context": false,
  "only_need_prompt": false,
  "response_type": "Multiple Paragraphs",
  "max_entity_tokens": 1000,
  "max_relation_tokens": 1000,
  "max_total_tokens": 5000,
  "hl_keywords": ["关键词1", "关键词2"],
  "ll_keywords": ["低级关键词1"],
  "conversation_history": [
    {"role": "user", "content": "之前的问题"},
    {"role": "assistant", "content": "之前的回答"}
  ],
  "user_prompt": "自定义提示",
  "enable_rerank": true
}
```

#### 查询模式
支持的查询模式：
- `local`: 本地模式 - 专注于上下文相关信息
- `global`: 全局模式 - 利用全局知识
- `hybrid`: 混合模式 - 结合本地和全局检索方法（推荐）
- `naive`: 朴素模式 - 执行基本搜索
- `mix`: 混合模式 - 整合知识图谱和向量检索
- `bypass`: 绕过模式 - 直接返回结果

#### 获取查询模式
- **端点**: `GET /query/modes`
- **描述**: 获取所有支持的查询模式及其说明

#### 批量查询
- **端点**: `POST /query/batch`
- **描述**: 批量执行多个查询
- **参数**: 
  - `queries`: 查询列表
  - `mode`: 查询模式（可选，默认hybrid）
  - `top_k`: 返回结果数量（可选，默认20）

### 4. 知识图谱管理

#### 获取知识图谱
- **端点**: `POST /knowledge-graph`
- **描述**: 获取指定节点的知识图谱
- **请求体**:
```json
{
  "node_label": "节点标签",
  "max_depth": 3,
  "max_nodes": 100
}
```

#### 知识图谱统计
- **端点**: `GET /knowledge-graph/stats`
- **描述**: 获取知识图谱的统计信息

#### 清空知识图谱
- **端点**: `DELETE /knowledge-graph/clear`
- **描述**: 清空所有知识图谱数据

### 5. 监控功能

#### 性能指标
- **端点**: `GET /metrics`
- **描述**: 获取系统性能指标

#### 日志查看
- **端点**: `GET /logs`
- **描述**: 获取最近的系统日志
- **参数**: `lines` (可选，默认100行)

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio

async def example_usage():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 检查服务状态
        response = await client.get(f"{base_url}/health")
        print("健康检查:", response.json())
        
        # 2. 插入文档
        insert_data = {
            "text": "人工智能是计算机科学的一个分支。",
            "doc_id": "ai_doc_1"
        }
        response = await client.post(f"{base_url}/insert/text", json=insert_data)
        print("插入结果:", response.json())
        
        # 3. 查询
        query_data = {
            "query": "什么是人工智能？",
            "mode": "hybrid",
            "top_k": 10
        }
        response = await client.post(f"{base_url}/query", json=query_data)
        print("查询结果:", response.json())

# 运行示例
asyncio.run(example_usage())
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/health"

# 插入文本
curl -X POST "http://localhost:8000/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "这是一个测试文档", "doc_id": "test_1"}'

# 查询
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "测试文档的内容是什么？", "mode": "hybrid"}'

# 文件上传
curl -X POST "http://localhost:8000/insert/file" \
  -F "file=@document.txt"
```

## 错误处理

常见错误代码：
- `400`: 请求参数错误
- `413`: 文件过大
- `422`: 数据验证错误
- `500`: 服务器内部错误

## 性能建议

1. **批量操作**: 对于大量文档，使用批量插入API而不是单个插入
2. **查询模式**: 推荐使用 `hybrid` 模式获得最佳查询效果
3. **文件大小**: 单个文件建议不超过50MB
4. **并发请求**: 建议控制并发请求数量，避免过载

## 限制

- 最大文件大小: 50MB
- 支持的文件格式: .txt, .pdf, .docx, .doc
- 最大并发请求: 建议不超过10个
- 查询超时: 30秒

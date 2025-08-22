# 流式响应修复总结

## 问题描述

当使用 `stream: true` 参数进行查询时，API 返回的不是正确的流式数据，而是异步生成器对象的字符串表示：

```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "result": "<async_generator object openai_complete_if_cache.<locals>.inner at 0x7fbdc4f72980>",
    "mode": "mix",
    "query": "什么是人工智能？",
    "knowledge_base": null,
    "language": "中文",
    "context_sources": null,
    "confidence": null,
    "response_time": 0.7038366794586182
  }
}
```

## 问题原因

在 `api/query_api.py` 文件的第 81 行，代码将所有结果都转换为字符串：

```python
query_response = QueryResponse(
    result=result if isinstance(result, str) else str(result),  # 问题在这里
    # ...
)
```

当 `stream=True` 时，RAG 系统返回的是 `AsyncIterator[str]`（异步生成器），但被强制转换为字符串，导致显示异步生成器对象的内存地址。

## 修复方案

### 1. 修改 `api/query_api.py`

- 添加必要的导入：
  ```python
  import json
  from typing import AsyncIterator
  from fastapi.responses import StreamingResponse
  ```

- 在查询执行后添加流式响应检测和处理：
  ```python
  # 如果是流式响应，返回StreamingResponse
  if request.stream and hasattr(result, '__aiter__'):
      async def generate_stream():
          # 发送元数据
          metadata = {...}
          yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
          
          # 流式输出内容
          async for chunk in result:
              if chunk:
                  chunk_data = {"type": "content", "data": chunk}
                  yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
          
          # 发送结束标记
          end_data = {"type": "done", "data": {"response_time": elapsed}}
          yield f"data: {json.dumps(end_data, ensure_ascii=False)}\n\n"
      
      return StreamingResponse(
          generate_stream(),
          media_type="text/event-stream",
          headers={
              "Cache-Control": "no-cache",
              "Connection": "keep-alive",
              "Access-Control-Allow-Origin": "*",
              "Access-Control-Allow-Headers": "*"
          }
      )
  ```

### 2. 修改 `routers/query_router.py`

- 移除固定的 `response_model=BaseResponse`，允许返回不同类型的响应
- 更新 API 文档，添加流式响应示例

### 3. 更新文档

在 `docs/API_Testing_Examples.md` 中添加正确的流式响应示例。

## 修复后的效果

### 正确的流式响应格式 (Server-Sent Events)

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"type": "metadata", "data": {"mode": "mix", "query": "什么是人工智能？", "knowledge_base": "cs_college", "language": "中文", "stream": true}}

data: {"type": "content", "data": "人工智能"}

data: {"type": "content", "data": "（AI）是"}

data: {"type": "content", "data": "计算机科学的一个分支"}

data: {"type": "done", "data": {"response_time": 1.25}}
```

### 响应类型说明

- `metadata`: 查询元数据（模式、查询内容、知识库等）
- `content`: 流式内容块
- `done`: 查询完成标记，包含响应时间
- `error`: 错误信息（如果发生错误）

## 测试验证

可以使用以下 curl 命令测试修复效果：

```bash
curl -X POST "http://localhost:8002/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "mix",
    "top_k": 10,
    "stream": true,
    "language": "中文", 
    "knowledge_base": "cs_college"
  }'
```

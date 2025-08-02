# GuiXiaoXiRag FastAPI 服务快速开始指南

## 1. 环境准备

### 系统要求
- Python 3.8+
- 8GB+ RAM
- 10GB+ 可用磁盘空间

### 依赖安装

```bash
# 激活conda环境
conda activate guixiaoxiRag312

# 安装依赖
pip install -r requirements.txt
```

## 2. 配置设置

### 环境变量配置

创建 `.env` 文件（可选）：

```env
# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# GuiXiaoXiRag配置
WORKING_DIR=./knowledgeBase/default

# 大模型配置
OPENAI_API_BASE=http://localhost:8100/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_CHAT_API_KEY=sk-gdXw028PJ6JtobnBLeQiArQLnmqahdXUQSjIbyFgAhJdHb1Q
OPENAI_CHAT_MODEL=qwen14b
OPENAI_EMBEDDING_MODEL=embedding_qwen

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=./logs
```

### 目录结构确认

确保以下目录存在：
```
project/
├── server/           # 服务端代码
├── logs/            # 日志文件
├── test/            # 测试文件
├── knowledgeBase/   # 知识库存储
└── uploads/         # 文件上传目录
```

## 3. 启动服务

### 开发模式启动

```bash
# 方法1: 直接运行
python -m server.api

# 方法2: 使用uvicorn
uvicorn server.api:app --host 0.0.0.0 --port 8000 --reload
```

### 生产模式启动

```bash
uvicorn server.api:app --host 0.0.0.0 --port 8000 --workers 4
```

## 4. 验证安装

### 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "system": {
    "service_name": "GuiXiaoXiRag FastAPI Service",
    "version": "1.0.0",
    "status": "running",
    "initialized": true
  }
}
```

### 访问文档

打开浏览器访问：
- API文档: http://localhost:8000/docs
- 替代文档: http://localhost:8000/redoc

## 5. 基础使用示例

### 5.1 插入文档

```python
import httpx
import asyncio

async def insert_document():
    async with httpx.AsyncClient() as client:
        # 插入文本
        response = await client.post(
            "http://localhost:8000/insert/text",
            json={
                "text": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                "doc_id": "ai_intro"
            }
        )
        print("插入结果:", response.json())

asyncio.run(insert_document())
```

### 5.2 查询知识库

```python
async def query_knowledge():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/query",
            json={
                "query": "什么是人工智能？",
                "mode": "hybrid",
                "top_k": 10
            }
        )
        print("查询结果:", response.json())

asyncio.run(query_knowledge())
```

### 5.3 上传文件

```python
async def upload_file():
    async with httpx.AsyncClient() as client:
        with open("document.txt", "rb") as f:
            response = await client.post(
                "http://localhost:8000/insert/file",
                files={"file": ("document.txt", f, "text/plain")}
            )
        print("上传结果:", response.json())

asyncio.run(upload_file())
```

## 6. 常见问题

### Q1: 服务启动失败
**A**: 检查以下项目：
- 确认大模型服务正在运行（端口8100和8200）
- 检查Python环境和依赖
- 查看日志文件获取详细错误信息

### Q2: 查询返回空结果
**A**: 可能的原因：
- 知识库中没有相关文档
- 查询模式不合适，尝试使用"hybrid"模式
- 文档还在处理中，等待几秒后重试

### Q3: 文件上传失败
**A**: 检查：
- 文件大小是否超过50MB限制
- 文件格式是否支持（.txt, .pdf, .docx, .doc）
- 磁盘空间是否充足

### Q4: 内存不足
**A**: 优化建议：
- 减少embedding_dim参数
- 限制并发请求数量
- 增加系统内存

## 7. 性能优化

### 7.1 批量操作

```python
# 推荐：批量插入
await client.post("/insert/texts", json={
    "texts": ["文档1", "文档2", "文档3"]
})

# 不推荐：逐个插入
for text in texts:
    await client.post("/insert/text", json={"text": text})
```

### 7.2 查询优化

```python
# 使用合适的top_k值
query_data = {
    "query": "问题",
    "mode": "hybrid",  # 推荐模式
    "top_k": 20,       # 适中的值
    "enable_rerank": True  # 启用重排序
}
```

## 8. 监控和维护

### 8.1 查看系统状态

```bash
curl http://localhost:8000/system/status
```

### 8.2 查看性能指标

```bash
curl http://localhost:8000/metrics
```

### 8.3 查看日志

```bash
curl "http://localhost:8000/logs?lines=50"
```

### 8.4 清理数据

```bash
# 清空知识图谱
curl -X DELETE http://localhost:8000/knowledge-graph/clear

# 重置系统
curl -X POST http://localhost:8000/system/reset
```

## 9. 下一步

- 阅读完整的 [API文档](api_guide.md)
- 查看 [示例代码](../examples/)
- 了解 [部署指南](deployment.md)
- 参与 [开发贡献](contributing.md)

## 10. 获取帮助

如果遇到问题：
1. 查看日志文件：`./logs/guixiaoxiRag_service.log`
2. 检查系统状态：`GET /system/status`
3. 运行测试：`python test/run_tests.py`
4. 查看GitHub Issues或提交新问题

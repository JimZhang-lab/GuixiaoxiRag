# GuiXiaoXiRag 快速开始指南

## 概述

本指南将帮助您在 5 分钟内快速启动 GuiXiaoXiRag 服务，并进行基本的功能测试。

## 前置要求

- Python 3.8+ 已安装
- 至少 4GB 可用内存
- 稳定的网络连接（用于下载依赖）

## 快速安装

### 步骤 1: 获取项目

```bash
# 方式一：Git 克隆（推荐）
git clone <repository-url>
cd server_new

# 方式二：下载压缩包
# 下载并解压到 server_new 目录
```

### 步骤 2: 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 3: 基础配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（可选，使用默认配置也可以运行）
# nano .env
```

### 步骤 4: 启动服务

```bash
# 启动服务
python main.py
```

看到以下输出表示启动成功：
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
```

### 步骤 5: 验证安装

打开浏览器访问：
- 服务状态: http://localhost:8002
- API 文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/api/v1/health

## 基础使用

### 1. 健康检查

```bash
curl http://localhost:8002/api/v1/health
```

预期响应：
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "system": {
        "service_name": "GuiXiaoXiRag FastAPI Service",
        "version": "2.0.0"
    }
}
```

### 2. 插入文档

```bash
curl -X POST "http://localhost:8002/api/v1/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工智能（AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
    "knowledge_base": "demo",
    "language": "中文"
  }'
```

### 3. 执行查询

```bash
curl -X POST "http://localhost:8002/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "top_k": 5
  }'
```

### 4. 查看知识库

```bash
curl http://localhost:8002/api/v1/knowledge-bases
```

## 使用 Python 客户端

### 安装客户端依赖

```bash
pip install requests
```

### 基础客户端示例

```python
import requests
import json

class GuiXiaoXiRagClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.api_base}/health")
        return response.json()
    
    def insert_text(self, text, knowledge_base="demo"):
        """插入文本"""
        data = {
            "text": text,
            "knowledge_base": knowledge_base,
            "language": "中文"
        }
        response = requests.post(f"{self.api_base}/insert/text", json=data)
        return response.json()
    
    def query(self, query_text, mode="hybrid", top_k=5):
        """执行查询"""
        data = {
            "query": query_text,
            "mode": mode,
            "top_k": top_k
        }
        response = requests.post(f"{self.api_base}/query", json=data)
        return response.json()

# 使用示例
client = GuiXiaoXiRagClient()

# 1. 检查服务状态
print("=== 健康检查 ===")
health = client.health_check()
print(f"服务状态: {health.get('status')}")

# 2. 插入示例文档
print("\n=== 插入文档 ===")
sample_texts = [
    "机器学习是人工智能的一个重要分支，它使计算机能够在没有明确编程的情况下学习。",
    "深度学习是机器学习的一个子集，它模仿人脑的工作方式来处理数据。",
    "自然语言处理（NLP）是人工智能的一个领域，专注于计算机与人类语言之间的交互。"
]

for i, text in enumerate(sample_texts):
    result = client.insert_text(text)
    print(f"文档 {i+1}: {'成功' if result.get('success') else '失败'}")

# 3. 执行查询
print("\n=== 执行查询 ===")
queries = [
    "什么是机器学习？",
    "深度学习和机器学习的关系是什么？",
    "NLP是什么？"
]

for query in queries:
    result = client.query(query)
    if result.get('success'):
        answer = result.get('data', {}).get('answer', '')
        print(f"问题: {query}")
        print(f"回答: {answer[:100]}...")
        print()
    else:
        print(f"查询失败: {query}")
```

## 文件上传示例

### 上传单个文件

```python
import requests

def upload_file(file_path, knowledge_base="demo"):
    """上传文件到知识库"""
    url = "http://localhost:8002/api/v1/insert/file"
    
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {
            "knowledge_base": knowledge_base,
            "language": "中文",
            "extract_metadata": "true"
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

# 使用示例
# result = upload_file("document.pdf", "my_kb")
# print(f"上传结果: {result}")
```

### 批量上传文件

```python
import os
import glob

def batch_upload_files(directory_path, knowledge_base="demo"):
    """批量上传目录中的文件"""
    supported_extensions = ['.txt', '.pdf', '.docx', '.md']
    results = []
    
    for ext in supported_extensions:
        files = glob.glob(os.path.join(directory_path, f"*{ext}"))
        
        for file_path in files:
            try:
                result = upload_file(file_path, knowledge_base)
                results.append({
                    'file': os.path.basename(file_path),
                    'success': result.get('success'),
                    'message': result.get('message')
                })
                print(f"上传 {os.path.basename(file_path)}: {'成功' if result.get('success') else '失败'}")
            except Exception as e:
                results.append({
                    'file': os.path.basename(file_path),
                    'success': False,
                    'message': str(e)
                })
                print(f"上传失败 {os.path.basename(file_path)}: {e}")
    
    return results

# 使用示例
# results = batch_upload_files("./documents", "my_kb")
```

## Web 界面使用

### 访问 Swagger UI

1. 打开浏览器访问: http://localhost:8002/docs
2. 在界面中可以：
   - 查看所有 API 端点
   - 测试 API 功能
   - 查看请求/响应格式
   - 下载 OpenAPI 规范

### 常用操作

#### 1. 测试查询 API
1. 找到 `POST /api/v1/query` 端点
2. 点击 "Try it out"
3. 输入查询参数：
   ```json
   {
     "query": "什么是人工智能？",
     "mode": "hybrid",
     "top_k": 10
   }
   ```
4. 点击 "Execute" 执行

#### 2. 上传文件
1. 找到 `POST /api/v1/insert/file` 端点
2. 点击 "Try it out"
3. 选择文件并填写参数
4. 点击 "Execute" 上传

#### 3. 管理知识库
1. 使用 `GET /api/v1/knowledge-bases` 查看知识库列表
2. 使用 `POST /api/v1/knowledge-bases` 创建新知识库
3. 使用 `POST /api/v1/knowledge-bases/switch` 切换知识库

## 常见问题

### Q1: 服务启动失败，提示端口被占用

**解决方案**:
```bash
# 检查端口占用
netstat -an | grep 8002
# 或
lsof -i :8002

# 修改端口（在 .env 文件中）
PORT=8003

# 或者杀死占用进程
kill -9 <进程ID>
```

### Q2: 查询没有返回结果

**可能原因**:
1. 知识库中没有相关文档
2. 查询内容与文档内容相关性较低

**解决方案**:
```bash
# 1. 检查知识库状态
curl http://localhost:8002/api/v1/knowledge-bases/current

# 2. 插入相关文档
curl -X POST "http://localhost:8002/api/v1/insert/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "相关内容文档", "knowledge_base": "demo"}'

# 3. 调整查询参数
# 增加 top_k 值，尝试不同的查询模式
```

### Q3: 文件上传失败

**检查项目**:
1. 文件大小是否超过限制（默认50MB）
2. 文件格式是否支持
3. 磁盘空间是否充足

**解决方案**:
```bash
# 检查支持的文件格式
curl http://localhost:8002/api/v1/system/status

# 检查磁盘空间
df -h

# 调整文件大小限制（在 .env 文件中）
MAX_FILE_SIZE=104857600  # 100MB
```

### Q4: 内存使用过高

**解决方案**:
```bash
# 清理缓存
curl -X DELETE http://localhost:8002/api/v1/cache/clear

# 检查缓存统计
curl http://localhost:8002/api/v1/cache/stats

# 调整配置（在 .env 文件中）
ENABLE_CACHE=true
CACHE_TTL=1800  # 减少缓存时间
```

## 性能优化建议

### 1. 基础优化

```bash
# 在 .env 文件中调整以下参数

# 启用缓存
ENABLE_CACHE=true
CACHE_TTL=3600

# 调整并发数
MAX_CONCURRENT_REQUESTS=50

# 优化日志级别
LOG_LEVEL=WARNING
```

### 2. 查询优化

```python
# 使用合适的查询模式
modes = {
    "fast": "naive",      # 快速查询
    "balanced": "hybrid", # 平衡模式
    "accurate": "global"  # 精确查询
}

# 设置合理的 top_k 值
top_k_values = {
    "quick": 5,
    "normal": 10,
    "detailed": 20
}
```

### 3. 批量处理

```python
# 批量插入文档
def batch_insert_texts(texts, batch_size=10):
    """批量插入文本"""
    url = "http://localhost:8002/api/v1/insert/texts"
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        data = {
            "texts": batch,
            "knowledge_base": "demo",
            "language": "中文"
        }
        
        response = requests.post(url, json=data)
        print(f"批次 {i//batch_size + 1}: {'成功' if response.status_code == 200 else '失败'}")

# 批量查询
def batch_query(queries):
    """批量查询"""
    url = "http://localhost:8002/api/v1/query/batch"
    
    data = {
        "queries": queries,
        "mode": "hybrid",
        "top_k": 10,
        "parallel": True
    }
    
    response = requests.post(url, json=data)
    return response.json()
```

## 下一步

完成快速开始后，您可以：

1. **深入学习**: 阅读 [完整API文档](API_Documentation.md)
2. **高级配置**: 查看 [部署指南](Deployment_Guide.md)
3. **开发扩展**: 参考 [开发者指南](Developer_Guide.md)
4. **架构了解**: 学习 [系统架构](Architecture_Overview.md)

## 获取帮助

- 📖 查看完整文档: `/docs` 目录
- 🌐 在线API文档: http://localhost:8002/docs
- 🐛 问题反馈: [GitHub Issues]
- 💬 社区讨论: [GitHub Discussions]

---

**恭喜！** 您已经成功启动了 GuiXiaoXiRag 服务。现在可以开始探索更多功能了！

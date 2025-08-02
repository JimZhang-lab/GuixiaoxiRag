# GuiXiaoXiRag FastAPI API 调用示例

## 📋 目录

- [基础示例](#基础示例)
- [Python客户端示例](#python客户端示例)
- [JavaScript示例](#javascript示例)
- [cURL命令示例](#curl命令示例)
- [批量操作示例](#批量操作示例)
- [高级功能示例](#高级功能示例)
- [错误处理示例](#错误处理示例)
- [性能优化示例](#性能优化示例)

## 基础示例

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8002/health

# 响应示例
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "uptime": "2 days, 3 hours, 45 minutes"
}
```

### 插入单个文档
```bash
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "doc_id": "ai_intro_001",
    "metadata": {
      "source": "manual_input",
      "category": "technology",
      "author": "system"
    }
  }'

# 响应示例
{
  "success": true,
  "message": "文档插入成功",
  "data": {
    "doc_id": "ai_intro_001",
    "chunks_created": 1,
    "processing_time": 2.34
  }
}
```

### 基础查询
```bash
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "top_k": 5
  }'

# 响应示例
{
  "success": true,
  "data": {
    "answer": "人工智能是计算机科学的一个分支...",
    "sources": [
      {
        "doc_id": "ai_intro_001",
        "chunk_id": "chunk_001",
        "score": 0.95,
        "content": "人工智能是计算机科学的一个分支..."
      }
    ],
    "query_time": 1.23,
    "mode": "hybrid"
  }
}
```

## Python客户端示例

### 基础客户端类
```python
import requests
import json
from typing import Dict, List, Optional

class GuiXiaoXiRagClient:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """检查服务健康状态"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def insert_text(self, text: str, doc_id: Optional[str] = None, 
                   metadata: Optional[Dict] = None) -> Dict:
        """插入文本文档"""
        data = {"text": text}
        if doc_id:
            data["doc_id"] = doc_id
        if metadata:
            data["metadata"] = metadata
        
        response = self.session.post(
            f"{self.base_url}/insert/text",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def query(self, query: str, mode: str = "hybrid", 
             top_k: int = 10, **kwargs) -> Dict:
        """查询知识库"""
        data = {
            "query": query,
            "mode": mode,
            "top_k": top_k,
            **kwargs
        }
        
        response = self.session.post(
            f"{self.base_url}/query",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path: str) -> Dict:
        """上传文件"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/insert/file",
                files=files
            )
        response.raise_for_status()
        return response.json()

# 使用示例
client = GuiXiaoXiRagClient()

# 检查服务状态
health = client.health_check()
print(f"Service status: {health['status']}")

# 插入文档
result = client.insert_text(
    text="深度学习是机器学习的一个子领域，使用神经网络来模拟人脑的学习过程。",
    doc_id="dl_intro_001",
    metadata={"category": "AI", "level": "beginner"}
)
print(f"Document inserted: {result['data']['doc_id']}")

# 查询
answer = client.query("什么是深度学习？", mode="hybrid", top_k=5)
print(f"Answer: {answer['data']['answer']}")
```

### 批量操作示例
```python
def batch_insert_texts(client: GuiXiaoXiRagClient, texts: List[str]) -> List[Dict]:
    """批量插入文本"""
    results = []
    
    # 使用批量接口
    response = client.session.post(
        f"{client.base_url}/insert/texts",
        json={"texts": texts}
    )
    response.raise_for_status()
    return response.json()

def batch_query(client: GuiXiaoXiRagClient, queries: List[str]) -> List[Dict]:
    """批量查询"""
    response = client.session.post(
        f"{client.base_url}/query/batch",
        json={"queries": queries, "mode": "hybrid"}
    )
    response.raise_for_status()
    return response.json()

# 使用示例
texts = [
    "机器学习是人工智能的一个重要分支。",
    "自然语言处理用于让计算机理解人类语言。",
    "计算机视觉让机器能够理解和分析图像。"
]

# 批量插入
batch_result = batch_insert_texts(client, texts)
print(f"Batch insert completed: {len(batch_result['data']['results'])} documents")

# 批量查询
queries = ["什么是机器学习？", "NLP的作用是什么？"]
batch_answers = batch_query(client, queries)
for i, answer in enumerate(batch_answers['data']['results']):
    print(f"Query {i+1}: {answer['answer']}")
```

### 异步客户端示例
```python
import asyncio
import aiohttp
from typing import Dict, List

class AsyncGuiXiaoXiRagClient:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def query(self, query: str, mode: str = "hybrid") -> Dict:
        """异步查询"""
        async with self.session.post(
            f"{self.base_url}/query",
            json={"query": query, "mode": mode}
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def concurrent_queries(self, queries: List[str]) -> List[Dict]:
        """并发查询"""
        tasks = [self.query(query) for query in queries]
        return await asyncio.gather(*tasks)

# 使用示例
async def main():
    async with AsyncGuiXiaoXiRagClient() as client:
        queries = [
            "什么是人工智能？",
            "机器学习的应用有哪些？",
            "深度学习和传统机器学习的区别？"
        ]
        
        # 并发查询
        results = await client.concurrent_queries(queries)
        
        for i, result in enumerate(results):
            print(f"Query {i+1}: {result['data']['answer'][:100]}...")

# 运行异步示例
# asyncio.run(main())
```

## JavaScript示例

### 基础JavaScript客户端
```javascript
class GuiXiaoXiRagClient {
    constructor(baseUrl = 'http://localhost:8002') {
        this.baseUrl = baseUrl;
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    
    async insertText(text, docId = null, metadata = null) {
        const data = { text };
        if (docId) data.doc_id = docId;
        if (metadata) data.metadata = metadata;
        
        const response = await fetch(`${this.baseUrl}/insert/text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    
    async query(query, mode = 'hybrid', topK = 10) {
        const response = await fetch(`${this.baseUrl}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                mode: mode,
                top_k: topK
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/insert/file`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }
}

// 使用示例
const client = new GuiXiaoXiRagClient();

// 检查服务状态
client.healthCheck()
    .then(health => console.log('Service status:', health.status))
    .catch(error => console.error('Health check failed:', error));

// 插入文档
client.insertText(
    '区块链是一种分布式账本技术，具有去中心化、不可篡改的特点。',
    'blockchain_001',
    { category: 'technology', level: 'intermediate' }
)
.then(result => console.log('Document inserted:', result.data.doc_id))
.catch(error => console.error('Insert failed:', error));

// 查询
client.query('什么是区块链？', 'hybrid', 5)
    .then(result => console.log('Answer:', result.data.answer))
    .catch(error => console.error('Query failed:', error));
```

### React组件示例
```jsx
import React, { useState, useEffect } from 'react';

const GuiXiaoXiRagInterface = () => {
    const [client] = useState(new GuiXiaoXiRagClient());
    const [query, setQuery] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [health, setHealth] = useState(null);
    
    useEffect(() => {
        // 检查服务状态
        client.healthCheck()
            .then(setHealth)
            .catch(console.error);
    }, [client]);
    
    const handleQuery = async () => {
        if (!query.trim()) return;
        
        setLoading(true);
        try {
            const result = await client.query(query);
            setAnswer(result.data.answer);
        } catch (error) {
            console.error('Query failed:', error);
            setAnswer('查询失败，请稍后重试。');
        } finally {
            setLoading(false);
        }
    };
    
    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        try {
            const result = await client.uploadFile(file);
            alert(`文件上传成功: ${result.data.doc_id}`);
        } catch (error) {
            console.error('Upload failed:', error);
            alert('文件上传失败');
        }
    };
    
    return (
        <div className="guixiaoxirag-interface">
            <div className="status">
                状态: {health ? health.status : '检查中...'}
            </div>
            
            <div className="upload-section">
                <input 
                    type="file" 
                    onChange={handleFileUpload}
                    accept=".txt,.pdf,.docx,.md"
                />
            </div>
            
            <div className="query-section">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="请输入您的问题..."
                    onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                />
                <button onClick={handleQuery} disabled={loading}>
                    {loading ? '查询中...' : '查询'}
                </button>
            </div>
            
            {answer && (
                <div className="answer-section">
                    <h3>回答:</h3>
                    <p>{answer}</p>
                </div>
            )}
        </div>
    );
};

export default GuiXiaoXiRagInterface;
```

## cURL命令示例

### 完整的工作流程
```bash
#!/bin/bash

# 1. 检查服务状态
echo "=== 检查服务状态 ==="
curl -s http://localhost:8002/health | jq '.'

# 2. 插入测试文档
echo -e "\n=== 插入测试文档 ==="
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "云计算是一种通过互联网提供计算服务的模式，包括服务器、存储、数据库、网络、软件等。",
    "doc_id": "cloud_computing_001",
    "metadata": {"category": "technology", "level": "basic"}
  }' | jq '.'

# 3. 批量插入文档
echo -e "\n=== 批量插入文档 ==="
curl -X POST "http://localhost:8002/insert/texts" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "大数据是指无法在一定时间范围内用常规软件工具进行捕捉、管理和处理的数据集合。",
      "物联网是指通过信息传感设备，将任何物品与互联网相连接，进行信息交换和通信。"
    ],
    "doc_ids": ["bigdata_001", "iot_001"]
  }' | jq '.'

# 4. 上传文件
echo -e "\n=== 上传文件 ==="
curl -X POST "http://localhost:8002/insert/file" \
  -F "file=@example.pdf" | jq '.'

# 5. 不同模式的查询
echo -e "\n=== 混合模式查询 ==="
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是云计算？",
    "mode": "hybrid",
    "top_k": 5
  }' | jq '.data.answer'

echo -e "\n=== 本地模式查询 ==="
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "大数据的特点是什么？",
    "mode": "local",
    "top_k": 3
  }' | jq '.data.answer'

# 6. 知识库管理
echo -e "\n=== 创建知识库 ==="
curl -X POST "http://localhost:8002/knowledge-bases" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tech_kb",
    "description": "技术知识库"
  }' | jq '.'

echo -e "\n=== 查看知识库列表 ==="
curl -s http://localhost:8002/knowledge-bases | jq '.'

# 7. 获取系统统计
echo -e "\n=== 系统统计 ==="
curl -s http://localhost:8002/knowledge-graph/stats | jq '.'

# 8. 获取性能指标
echo -e "\n=== 性能指标 ==="
curl -s http://localhost:8002/metrics | jq '.'
```

### 高级查询示例
```bash
# 流式查询
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "解释机器学习的工作原理",
    "mode": "global",
    "stream": true,
    "max_tokens": 1000
  }' --no-buffer

# 带上下文的查询
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "它的优势是什么？",
    "mode": "hybrid",
    "context": "我们刚才讨论了云计算的概念",
    "top_k": 5
  }' | jq '.'

# 多语言查询
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "mode": "hybrid",
    "language": "English",
    "response_language": "中文"
  }' | jq '.'
```

## 批量操作示例

### Python批量处理脚本
```python
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_directory(client: GuiXiaoXiRagClient, directory_path: str):
    """批量处理目录中的文件"""
    directory = Path(directory_path)
    supported_extensions = {'.txt', '.md', '.pdf', '.docx', '.doc'}
    
    files_to_process = [
        f for f in directory.rglob('*') 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    print(f"Found {len(files_to_process)} files to process")
    
    def upload_file(file_path):
        try:
            result = client.upload_file(str(file_path))
            return {"file": file_path.name, "success": True, "result": result}
        except Exception as e:
            return {"file": file_path.name, "success": False, "error": str(e)}
    
    # 并发上传文件
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(upload_file, file_path): file_path 
            for file_path in files_to_process
        }
        
        results = []
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            if result["success"]:
                print(f"✅ {result['file']} uploaded successfully")
            else:
                print(f"❌ {result['file']} failed: {result['error']}")
    
    return results

# 使用示例
client = GuiXiaoXiRagClient()
results = process_directory(client, "./documents")

success_count = sum(1 for r in results if r["success"])
print(f"\nProcessing completed: {success_count}/{len(results)} files successful")
```

### 批量查询和分析
```python
def analyze_queries(client: GuiXiaoXiRagClient, queries: List[str]):
    """批量查询并分析结果"""
    results = []
    
    for i, query in enumerate(queries):
        print(f"Processing query {i+1}/{len(queries)}: {query[:50]}...")
        
        try:
            # 尝试不同的查询模式
            modes = ["hybrid", "local", "global"]
            query_results = {}
            
            for mode in modes:
                start_time = time.time()
                result = client.query(query, mode=mode, top_k=5)
                end_time = time.time()
                
                query_results[mode] = {
                    "answer": result["data"]["answer"],
                    "sources_count": len(result["data"]["sources"]),
                    "response_time": end_time - start_time
                }
            
            results.append({
                "query": query,
                "results": query_results
            })
            
        except Exception as e:
            print(f"Error processing query: {e}")
            results.append({
                "query": query,
                "error": str(e)
            })
    
    return results

# 分析查询性能
queries = [
    "什么是人工智能？",
    "机器学习的主要算法有哪些？",
    "深度学习在图像识别中的应用",
    "自然语言处理的发展历程",
    "云计算的安全性如何保障？"
]

analysis_results = analyze_queries(client, queries)

# 生成性能报告
for result in analysis_results:
    if "error" not in result:
        print(f"\nQuery: {result['query']}")
        for mode, data in result['results'].items():
            print(f"  {mode}: {data['response_time']:.2f}s, {data['sources_count']} sources")
```

## 错误处理示例

### 完整的错误处理
```python
import logging
from requests.exceptions import RequestException, Timeout, ConnectionError

class GuiXiaoXiRagClientWithErrorHandling(GuiXiaoXiRagClient):
    def __init__(self, base_url: str = "http://localhost:8002", 
                 timeout: int = 30, max_retries: int = 3):
        super().__init__(base_url)
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """带重试机制的请求方法"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避
                
            except ConnectionError:
                self.logger.warning(f"Connection error (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
                
            except RequestException as e:
                if e.response and e.response.status_code >= 500:
                    # 服务器错误，重试
                    self.logger.warning(f"Server error {e.response.status_code} (attempt {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)
                else:
                    # 客户端错误，不重试
                    raise
    
    def query_with_fallback(self, query: str, modes: List[str] = None) -> Dict:
        """带降级策略的查询"""
        if modes is None:
            modes = ["hybrid", "local", "naive"]
        
        last_error = None
        
        for mode in modes:
            try:
                self.logger.info(f"Trying query with mode: {mode}")
                return self._make_request(
                    "POST", "/query",
                    json={"query": query, "mode": mode}
                )
            except Exception as e:
                self.logger.warning(f"Query failed with mode {mode}: {e}")
                last_error = e
                continue
        
        # 所有模式都失败
        raise last_error or Exception("All query modes failed")

# 使用示例
logging.basicConfig(level=logging.INFO)
robust_client = GuiXiaoXiRagClientWithErrorHandling()

try:
    result = robust_client.query_with_fallback("什么是人工智能？")
    print("Query successful:", result["data"]["answer"])
except Exception as e:
    print(f"All query attempts failed: {e}")
```

## 性能优化示例

### 连接池和会话管理
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedGuiXiaoXiRagClient(GuiXiaoXiRagClient):
    def __init__(self, base_url: str = "http://localhost:8002"):
        super().__init__(base_url)
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # 配置HTTP适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认超时
        self.session.timeout = 30
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

# 使用上下文管理器
with OptimizedGuiXiaoXiRagClient() as client:
    # 批量操作
    for i in range(100):
        result = client.query(f"Query {i}")
        print(f"Query {i} completed")
```

### 缓存查询结果
```python
from functools import lru_cache
import hashlib

class CachedGuiXiaoXiRagClient(GuiXiaoXiRagClient):
    def __init__(self, base_url: str = "http://localhost:8002", cache_size: int = 128):
        super().__init__(base_url)
        self.cache_size = cache_size
    
    def _cache_key(self, query: str, mode: str, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{query}:{mode}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @lru_cache(maxsize=128)
    def _cached_query(self, cache_key: str, query: str, mode: str, **kwargs):
        """缓存的查询方法"""
        return super().query(query, mode, **kwargs)
    
    def query(self, query: str, mode: str = "hybrid", **kwargs):
        """带缓存的查询"""
        cache_key = self._cache_key(query, mode, **kwargs)
        return self._cached_query(cache_key, query, mode, **kwargs)

# 使用缓存客户端
cached_client = CachedGuiXiaoXiRagClient()

# 第一次查询会调用API
result1 = cached_client.query("什么是人工智能？")

# 第二次相同查询会使用缓存
result2 = cached_client.query("什么是人工智能？")  # 从缓存返回
```

## 🔗 相关文档

- [API参考文档](API_REFERENCE.md)
- [快速开始指南](../getting-started/QUICK_START.md)
- [配置指南](../getting-started/CONFIGURATION_GUIDE.md)
- [故障排除指南](../getting-started/TROUBLESHOOTING.md)
- [Python客户端示例](../../examples/api_client.py)

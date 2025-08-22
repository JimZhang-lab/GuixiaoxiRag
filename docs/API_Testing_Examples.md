# GuiXiaoXiRag API 测试示例

## 概述

本文档提供了 GuiXiaoXiRag FastAPI 服务的详细测试示例，包括各种API端点的测试用例、请求示例和预期响应。

## 测试环境配置

### 基础配置

```bash
# 服务地址
BASE_URL="http://localhost:8002"
API_BASE="http://localhost:8002/api/v1"

# 测试工具
# 1. curl 命令行工具
# 2. Postman 或 Insomnia
# 3. Python requests 库
# 4. JavaScript fetch API
```

```
curl -X POST "http://localhost:8002/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何学习机器学习？",
    "mode": "mix",
    "top_k": 10,
    "stream": true,
    "language": "中文",
    "knowledge_base": "cs_college"
  }'
```

**正确的流式响应格式 (Server-Sent Events):**
```
data: {"type": "metadata", "data": {"mode": "mix", "query": "如何学习机器学习？", "knowledge_base": "cs_college", "language": "中文", "stream": true}}

data: {"type": "content", "data": "机器学习"}

data: {"type": "content", "data": "是人工智能的一个重要分支"}

data: {"type": "content", "data": "，它通过算法让计算机从数据中学习模式..."}

data: {"type": "done", "data": {"response_time": 1.25}}
```

**错误的响应格式示例 (已修复):**
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

## 网关对接与标准请求头

在通过 Java 网关转发到算法服务时，请统一携带如下头部以实现“用户优先”的限流与分层：

- X-User-Id: 稳定用户标识（必）
- X-Client-Id: 客户端/会话标识（建议）
- X-User-Tier: 用户套餐等级（free/pro/enterprise…）

Shell 示例（可作为基础别名复用）：
```bash
API_BASE="http://localhost:8002/api/v1"
CURL_JSON="curl -sS -H 'Accept: application/json' -H 'Content-Type: application/json' \
  -H 'X-User-Id: user_12345' -H 'X-Client-Id: web-session-abc' -H 'X-User-Tier: pro'"
```
# 也可仅定义标准网关头（适用于 multipart/form-data 等非 JSON 请求）
GATEWAY_HDRS=(
  -H 'X-User-Id: user_12345'
  -H 'X-Client-Id: web-session-abc'
  -H 'X-User-Tier: pro'
)


说明：
- 若有受信任代理（trusted_proxy_ips），可由网关注入 X-Forwarded-For / X-Real-IP；算法端仅对受信任代理来源读取这些头部
- 算法端默认大模型请求超时 240s，可通过 .env 配置 LLM_TIMEOUT/EMBEDDING_TIMEOUT/RERANK_TIMEOUT


### 启动服务

```bash
# 进入项目目录
cd /path/to/server_new

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

## 1. 系统管理 API 测试

### 1.1 健康检查测试

```bash
# curl 测试（网关头）
$CURL_JSON -X GET "$API_BASE/health"
```

```python
# Python 测试
import requests

response = requests.get("http://localhost:8002/api/v1/health")
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
```

**预期响应**:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "system": {
        "service_name": "GuiXiaoXiRag FastAPI Service",
        "version": "0.1.0",
        "uptime": 3600
    },
    "dependencies": {
        "database": "healthy",
        "file_system": "healthy",
        "llm_service": "healthy"
    }
}
```

### 1.2 系统状态测试

```bash
$CURL_JSON -X GET "$API_BASE/system/status"
```

### 1.3 性能指标测试

```bash
$CURL_JSON -X GET "$API_BASE/metrics"

# 通过网关头部的 cURL 示例

```bash
# 基础智能查询（hybrid）
$CURL_JSON -X POST "$API_BASE/query" -d '{
  "query": "什么是人工智能？",
  "mode": "hybrid",
  "top_k": 10
}'

# 本地模式查询（local）
$CURL_JSON -X POST "$API_BASE/query" -d '{
  "query": "机器学习的基本概念",
  "mode": "local",
  "top_k": 5
}'

# 全局模式 + 质量优先（global + quality）
$CURL_JSON -X POST "$API_BASE/query" -d '{
  "query": "深度学习算法",
  "mode": "global",
  "top_k": 15,
  "performance_mode": "quality"
}'

# 批量查询（batch）
$CURL_JSON -X POST "$API_BASE/query/batch" -d '{
  "queries": ["什么是机器学习？", "深度学习的应用领域有哪些？", "如何选择合适的算法？"],
  "mode": "hybrid",
  "top_k": 10,
  "parallel": true,
  "timeout": 300
}'

# 问答查询（QA）
$CURL_JSON -X POST "$API_BASE/qa/query" -d '{
  "question": "什么是RAG？",
  "top_k": 3,
  "min_similarity": 0.85
}'

# 批量问答查询（QA batch）
$CURL_JSON -X POST "$API_BASE/qa/query/batch" -d '{
  "questions": ["什么是RAG？", "RAG的优势是什么？"],
  "top_k": 3,
  "min_similarity": 0.8
}'
```

```

## 2. 查询 API 测试

### 2.1 基础查询测试

```bash
# 基础 query（hybrid）
$CURL_JSON -X POST "$API_BASE/query" -d '{
  "query": "什么是人工智能？",
  "mode": "hybrid",
  "top_k": 10
}'
```

```python
# Python 详细测试
import requests
import json

def test_query_api():
    url = "http://localhost:8002/api/v1/query"

    test_cases = [
        {
            "name": "基础查询",
            "data": {
                "query": "什么是人工智能？",
                "mode": "hybrid",
                "top_k": 10
            }
        },
        {
            "name": "本地模式查询",
            "data": {
                "query": "机器学习的基本概念",
                "mode": "local",
                "top_k": 5
            }
        },
        {
            "name": "全局模式查询",
            "data": {
                "query": "深度学习算法",
                "mode": "global",
                "top_k": 15
            }
        },
        {
            "name": "高级参数查询",
            "data": {
                "query": "神经网络的应用",
                "mode": "hybrid",
                "top_k": 20,
                "performance_mode": "quality",
                "enable_rerank": True,
                "language": "中文"
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        try:
            response = requests.post(url, json=test_case['data'])
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"成功: {result.get('success')}")
                print(f"消息: {result.get('message')}")
                if result.get('data'):
                    data = result['data']
                    print(f"答案长度: {len(data.get('answer', ''))}")
                    print(f"查询时间: {data.get('query_time')}秒")
            else:
                print(f"错误: {response.text}")

        except Exception as e:
            print(f"异常: {str(e)}")

# 运行测试
test_query_api()
```

### 2.2 意图分析测试

```bash
$CURL_JSON -X POST "$API_BASE/query/analyze" -d '{
  "query": "如何学习机器学习？",
  "context": {"domain": "education"},
  "enable_enhancement": true,
  "safety_check": true
}'
```

### 2.3 安全查询测试

```bash
$CURL_JSON -X POST "$API_BASE/query/safe" -d '{
  "query": "人工智能的发展历史",
  "mode": "hybrid",
  "enable_intent_analysis": true,
  "enable_query_enhancement": true,
  "safety_check": true
}'
```

### 2.4 批量查询测试

```python
def test_batch_query():
    url = "http://localhost:8002/api/v1/query/batch"

    data = {
        "queries": [
            "什么是机器学习？",
            "深度学习的应用领域有哪些？",
            "如何选择合适的算法？",
            "神经网络的基本原理",
            "人工智能的发展趋势"
        ],
        "mode": "hybrid",
        "top_k": 10,
        "parallel": True,
        "timeout": 300
    }

    headers={"X-User-Id":"user_12345","X-Client-Id":"web-session-abc","X-User-Tier":"pro"}
response = requests.post(url, json=data, headers=headers)
    print(f"批量查询状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"成功处理: {len(result.get('data', {}).get('results', []))} 个查询")
    else:
        print(f"错误: {response.text}")
```

## 3. 文档管理 API 测试

### 3.1 插入文本测试

```bash
$CURL_JSON -X POST "$API_BASE/insert/text" -d '{
  "text": "人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
  "knowledge_base": "test_kb",
  "language": "中文"
}'
```

```python
def test_insert_text():
    url = "http://localhost:8002/api/v1/insert/text"

    test_texts = [
        "机器学习是人工智能的一个重要分支，它使计算机能够在没有明确编程的情况下学习。",
        "深度学习是机器学习的一个子集，它模仿人脑的工作方式来处理数据。",
        "神经网络是深度学习的基础，由多个相互连接的节点组成。"
    ]

    for i, text in enumerate(test_texts):
        data = {
            "text": text,
            "doc_id": f"test_doc_{i+1}",
            "knowledge_base": "test_kb",
            "language": "中文"
        }

        response = requests.post(url, json=data)
        print(f"插入文本 {i+1}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  成功: {result.get('success')}")
            print(f"  跟踪ID: {result.get('data', {}).get('track_id')}")
```

### 3.2 批量插入文本测试

```python
def test_batch_insert_texts():
    url = "http://localhost:8002/api/v1/insert/texts"

    data = {
        "texts": [
            "自然语言处理（NLP）是人工智能的一个重要应用领域。",
            "计算机视觉使机器能够理解和解释视觉信息。",
            "强化学习是一种通过与环境交互来学习的机器学习方法。",
            "知识图谱是一种结构化的知识表示方法。"
        ],
        "knowledge_base": "test_kb",
        "language": "中文"
    }

    response = requests.post(url, json=data)
    print(f"批量插入状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"批量插入成功: {result.get('success')}")
        print(f"处理数量: {len(data['texts'])}")
```

### 3.3 文件上传测试

```python
def test_file_upload():
    url = "http://localhost:8002/api/v1/insert/file"

    # 创建测试文件
    test_content = """
    # 人工智能简介

    人工智能（AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。

    ## 主要领域

    1. 机器学习
    2. 自然语言处理
    3. 计算机视觉
    4. 机器人学

    ## 应用场景

    - 语音识别
    - 图像识别
    - 推荐系统
    - 自动驾驶
    """

    # 保存为临时文件
    with open("test_ai_intro.md", "w", encoding="utf-8") as f:
        f.write(test_content)

    # 上传文件
    with open("test_ai_intro.md", "rb") as f:
        files = {"file": ("test_ai_intro.md", f, "text/markdown")}
        data = {
            "knowledge_base": "test_kb",
            "language": "中文",
            "extract_metadata": "true"
        }

        response = requests.post(url, files=files, data=data)
        print(f"文件上传状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"上传成功: {result.get('success')}")
            print(f"文件信息: {result.get('data', {}).get('file_info')}")

    # 清理临时文件
    import os
    os.remove("test_ai_intro.md")
```

## 4. 知识库管理 API 测试

### 4.1 获取知识库列表

```bash
$CURL_JSON -X GET "$API_BASE/knowledge-bases"
```

### 4.2 创建知识库测试

```python
def test_create_knowledge_base():
    url = "http://localhost:8002/api/v1/knowledge-bases"

    data = {
        "name": "test_ai_kb",
        "description": "人工智能测试知识库",
        "language": "中文",
        "config": {
            "chunk_size": 1024,
            "chunk_overlap": 50,
            "enable_auto_update": True
        }
    }

    response = requests.post(url, json=data)
    print(f"创建知识库状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"创建成功: {result.get('success')}")
        print(f"知识库信息: {result.get('data')}")
    else:
        print(f"创建失败: {response.text}")
```

### 4.3 切换知识库测试

```python
def test_switch_knowledge_base():
    url = "http://localhost:8002/api/v1/knowledge-bases/switch"

    data = {
        "name": "test_ai_kb",
        "create_if_not_exists": True
    }

    response = requests.post(url, json=data)
    print(f"切换知识库状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"切换成功: {result.get('success')}")
        print(f"当前知识库: {result.get('data', {}).get('current_kb')}")
```

## 5. 知识图谱 API 测试

### 5.1 获取图谱数据测试

```python
def test_knowledge_graph():
    url = "http://localhost:8002/api/v1/knowledge-graph"

    data = {
        "node_label": "人工智能",
        "max_depth": 2,
        "max_nodes": 50,
        "include_metadata": True
    }

    response = requests.post(url, json=data)
    print(f"获取图谱数据状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            graph_data = result.get('data', {})
            print(f"节点数量: {graph_data.get('node_count', 0)}")
            print(f"边数量: {graph_data.get('edge_count', 0)}")
        else:
            print(f"获取失败: {result.get('message')}")
```

### 5.2 图谱统计信息测试

```bash
$CURL_JSON -X GET "$API_BASE/knowledge-graph/stats"
```

### 5.3 图谱状态测试

```bash
$CURL_JSON -X GET "$API_BASE/knowledge-graph/status"
```

## 6. 意图识别 API 测试

### 6.1 意图分析测试

```python
def test_intent_analysis():
    url = "http://localhost:8002/api/v1/intent/analyze"

    test_queries = [
        "如何学习Python编程？",
        "今天天气怎么样？",
        "什么是机器学习？",
        "你好，请问你是谁？"
    ]

    for query in test_queries:
        data = {
            "query": query,
            "context": {"domain": "general"}
        }

        response = requests.post(url, json=data)
        print(f"\n查询: {query}")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"意图类型: {result.get('intent_type')}")
            print(f"安全级别: {result.get('safety_level')}")
            print(f"置信度: {result.get('confidence')}")
```

### 6.2 安全检查测试

```python
def test_safety_check():
    url = "http://localhost:8002/api/v1/intent/safety-check"

    test_contents = [
        "如何制作蛋糕？",
        "学习编程的最佳方法",
        "人工智能的发展前景"
    ]

    for content in test_contents:
        data = {
            "content": content,
            "check_type": "query"
        }

        response = requests.post(url, json=data)
        print(f"\n内容: {content}")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"安全级别: {result.get('safety_level')}")
            print(f"风险因素: {result.get('risk_factors', [])}")
```

## 7. 缓存管理 API 测试

### 7.1 获取缓存统计

```bash
$CURL_JSON -X GET "$API_BASE/cache/stats"
```

### 7.2 清理缓存测试

```python
def test_cache_management():
    # 获取缓存统计
    stats_url = "http://localhost:8002/api/v1/cache/stats"
    response = requests.get(stats_url)
    print(f"缓存统计状态码: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print(f"缓存统计: {stats.get('data')}")

    # 清理特定缓存
    clear_url = "http://localhost:8002/api/v1/cache/clear/llm"
    response = requests.delete(clear_url)
    print(f"清理LLM缓存状态码: {response.status_code}")

    # 清理所有缓存
    clear_all_url = "http://localhost:8002/api/v1/cache/clear"
    response = requests.delete(clear_all_url)
    print(f"清理所有缓存状态码: {response.status_code}")
```

## 8. 综合测试脚本

```python
#!/usr/bin/env python3
"""
GuiXiaoXiRag API 综合测试脚本
"""
import requests
import time
import json

class APITester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.results = []

    def log_result(self, test_name, success, message, data=None):
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def run_all_tests(self):
        """运行所有测试"""
        print("开始运行 GuiXiaoXiRag API 综合测试...")
        print("=" * 50)

        # 系统测试
        self.test_health_check()
        self.test_system_status()

        # 查询测试
        self.test_basic_query()
        self.test_intent_analysis()

        # 文档管理测试
        self.test_insert_text()

        # 知识库测试
        self.test_knowledge_bases()

        # 缓存测试
        self.test_cache_stats()

        # 输出测试结果
        self.print_summary()

    def test_health_check(self):
        try:
            response = self.session.get(f"{self.api_base}/health")
            if response.status_code == 200:
                self.log_result("健康检查", True, "服务健康状态正常")
            else:
                self.log_result("健康检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("健康检查", False, f"请求失败: {str(e)}")

    def test_system_status(self):
        try:
            response = self.session.get(f"{self.api_base}/system/status")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result("系统状态", True, "系统状态获取成功")
                else:
                    self.log_result("系统状态", False, data.get("message"))
            else:
                self.log_result("系统状态", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("系统状态", False, f"请求失败: {str(e)}")

    def test_basic_query(self):
        try:
            data = {
                "query": "什么是人工智能？",
                "mode": "hybrid",
                "top_k": 10
            }
            headers = {"X-User-Id":"user_12345","X-Client-Id":"web-session-abc","X-User-Tier":"pro"}
            response = self.session.post(f"{self.api_base}/query", json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("基础查询", True, "查询执行成功")
                else:
                    self.log_result("基础查询", False, result.get("message"))
            else:
                self.log_result("基础查询", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("基础查询", False, f"请求失败: {str(e)}")

    def test_intent_analysis(self):
        try:
            data = {
                "query": "如何学习机器学习？",
                "context": {"domain": "education"}
            }
            response = self.session.post(f"{self.api_base}/query/analyze", json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("意图分析", True, "意图分析成功")
                else:
                    self.log_result("意图分析", False, result.get("message"))
            else:
                self.log_result("意图分析", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("意图分析", False, f"请求失败: {str(e)}")

    def test_insert_text(self):
        try:
            data = {
                "text": "这是一个测试文本，用于验证文档插入功能。",
                "knowledge_base": "test_kb",
                "language": "中文"
            }
            response = self.session.post(f"{self.api_base}/insert/text", json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("文本插入", True, "文本插入成功")
                else:
                    self.log_result("文本插入", False, result.get("message"))
            else:
                self.log_result("文本插入", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("文本插入", False, f"请求失败: {str(e)}")

    def test_knowledge_bases(self):
        try:
            response = self.session.get(f"{self.api_base}/knowledge-bases")
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    kb_count = len(result.get("data", {}).get("knowledge_bases", []))
                    self.log_result("知识库列表", True, f"获取到 {kb_count} 个知识库")
                else:
                    self.log_result("知识库列表", False, result.get("message"))
            else:
                self.log_result("知识库列表", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("知识库列表", False, f"请求失败: {str(e)}")

    def test_cache_stats(self):
        try:
            response = self.session.get(f"{self.api_base}/cache/stats")
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log_result("缓存统计", True, "缓存统计获取成功")
                else:
                    self.log_result("缓存统计", False, result.get("message"))
            else:
                self.log_result("缓存统计", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_result("缓存统计", False, f"请求失败: {str(e)}")

    def print_summary(self):
        print("\n" + "=" * 50)
        print("测试结果汇总")
        print("=" * 50)

        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests

        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
```

## 运行测试

```bash
# 保存测试脚本为 test_api.py
python test_api.py

# 或者使用 pytest
pip install pytest
pytest test_api.py -v
```

## 测试注意事项

1. **服务状态**: 确保服务正在运行
2. **网络连接**: 检查网络连接和端口访问
3. **数据准备**: 某些测试可能需要预先准备数据
4. **权限设置**: 确保有足够的文件系统权限
5. **资源限制**: 注意内存和磁盘空间限制

## 故障排除

### 常见问题

1. **连接拒绝**: 检查服务是否启动，端口是否正确
2. **超时错误**: 增加请求超时时间
3. **权限错误**: 检查文件和目录权限
4. **内存不足**: 监控系统资源使用情况

### 调试技巧

1. 启用详细日志记录
2. 使用浏览器开发者工具
3. 检查服务器日志文件
4. 使用API文档进行交互式测试

---

*本文档提供了全面的API测试示例，帮助开发者验证系统功能和性能。*

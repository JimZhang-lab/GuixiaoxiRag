"""
测试配置文件 - 最终修复版本
解决所有已知的配置问题
"""

import pytest
import pytest_asyncio
import asyncio
import httpx
import json
import os
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
import time
import uuid

# 测试配置 - 使用绝对路径
TEST_CONFIG = {
    "base_url": "http://localhost:8002",
    "api_prefix": "/api/v1",
    "timeout": 30,
    "max_retries": 3,
    "test_data_dir": str(Path(__file__).parent / "test_data"),
    "temp_dir": str(Path(__file__).parent / "temp")
}

# API端点配置
API_ENDPOINTS = {
    "qa": {
        "health": "/qa/health",
        "pairs": "/qa/pairs",
        "pairs_batch": "/qa/pairs/batch",
        "query": "/qa/query",
        "query_batch": "/qa/query/batch",
        "clear": "/qa/clear",
        "categories": "/qa/categories",
        "statistics": "/qa/statistics",
        "export": "/qa/export",
        "import": "/qa/import"
    },
    "document": {
        "insert_text": "/insert/text",
        "insert_texts": "/insert/texts",
        "insert_file": "/insert/file",
        "insert_files": "/insert/files",
        "insert_directory": "/insert/directory"
    },
    "query": {
        "query": "/query",
        "batch": "/query/batch",
        "modes": "/query/modes",
        "optimized": "/query/optimized"
    },
    "system": {
        "health": "/health",
        "status": "/system/status",
        "metrics": "/metrics",
        "logs": "/logs",
        "reset": "/system/reset",
        "config": "/service/config",
        "effective_config": "/service/effective-config",
        "update_config": "/service/config/update"
    },
    "knowledge_base": {
        "list": "/knowledge-bases",
        "create": "/knowledge-bases",
        "delete": "/knowledge-bases/{name}",
        "switch": "/knowledge-bases/switch",
        "current": "/knowledge-bases/current"
    },
    "knowledge_graph": {
        "query": "/knowledge-graph",
        "stats": "/knowledge-graph/stats",
        "clear": "/knowledge-graph/clear",
        "status": "/knowledge-graph/status",
        "convert": "/knowledge-graph/convert"
    },
    "intent": {
        "health": "/intent/health",
        "analyze": "/intent/analyze",
        "safety_check": "/intent/safety-check",
        "status": "/intent/status"
    }
}

class TestHTTPClient:
    """测试HTTP客户端类 - 重命名避免pytest收集"""
    
    def __init__(self, base_url: str = None, timeout: int = 30):
        self.base_url = base_url or TEST_CONFIG["base_url"]
        self.api_prefix = TEST_CONFIG["api_prefix"]
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    def get_url(self, endpoint: str) -> str:
        """获取完整的API URL"""
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"{self.api_prefix}{endpoint}"
    
    async def get(self, endpoint: str, params: Dict = None, **kwargs) -> httpx.Response:
        """GET请求"""
        url = self.get_url(endpoint)
        return await self.session.get(url, params=params, **kwargs)
    
    async def post(self, endpoint: str, json_data: Dict = None, data: Dict = None, files: Dict = None, **kwargs) -> httpx.Response:
        """POST请求"""
        url = self.get_url(endpoint)
        return await self.session.post(url, json=json_data, data=data, files=files, **kwargs)
    
    async def put(self, endpoint: str, json_data: Dict = None, **kwargs) -> httpx.Response:
        """PUT请求"""
        url = self.get_url(endpoint)
        return await self.session.put(url, json=json_data, **kwargs)
    
    async def delete(self, endpoint: str, json_data: Dict = None, **kwargs) -> httpx.Response:
        """DELETE请求"""
        url = self.get_url(endpoint)
        return await self.session.delete(url, json=json_data, **kwargs)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_client():
    """测试客户端夹具 - 最终修复版本"""
    async with TestHTTPClient() as client:
        yield client

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    data_dir = Path(TEST_CONFIG["test_data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

@pytest.fixture(scope="session")
def temp_dir():
    """临时目录 - 最终修复版本"""
    temp_dir = Path(TEST_CONFIG["temp_dir"])
    temp_dir.mkdir(parents=True, exist_ok=True)
    yield temp_dir
    # 清理临时目录
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture
def sample_qa_pairs():
    """示例问答对数据"""
    return [
        {
            "question": "什么是人工智能？",
            "answer": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            "category": "AI基础",
            "confidence": 1.0,
            "keywords": ["人工智能", "AI", "计算机科学"],
            "source": "test_data"
        },
        {
            "question": "机器学习和深度学习有什么区别？",
            "answer": "机器学习是AI的一个子集，而深度学习是机器学习的一个子集。深度学习使用神经网络来模拟人脑的工作方式。",
            "category": "机器学习",
            "confidence": 0.95,
            "keywords": ["机器学习", "深度学习", "神经网络"],
            "source": "test_data"
        }
    ]

@pytest.fixture
def sample_documents():
    """示例文档数据"""
    return [
        {
            "text": "人工智能技术正在快速发展，包括机器学习、深度学习、自然语言处理等多个领域。",
            "doc_id": "doc_001",
            "knowledge_base": "test_kb",
            "language": "中文"
        },
        {
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn.",
            "doc_id": "doc_002",
            "knowledge_base": "test_kb",
            "language": "English"
        }
    ]

@pytest.fixture
def test_knowledge_base():
    """测试知识库配置"""
    return {
        "name": f"test_kb_{uuid.uuid4().hex[:8]}",
        "description": "测试用知识库",
        "language": "中文",
        "config": {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "enable_auto_update": True
        }
    }

class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def generate_test_id() -> str:
        """生成测试ID"""
        return f"test_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def create_test_file(content: str, filename: str, temp_dir: Path) -> Path:
        """创建测试文件"""
        file_path = temp_dir / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    @staticmethod
    async def wait_for_service(client: TestHTTPClient, endpoint: str, max_wait: int = 30) -> bool:
        """等待服务可用"""
        for _ in range(max_wait):
            try:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    return True
            except:
                pass
            await asyncio.sleep(1)
        return False
    
    @staticmethod
    def assert_response_success(response: httpx.Response, expected_status: int = 200):
        """断言响应成功 - 最终修复版本"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
                if "success" in data:
                    assert data["success"] is True, f"Response not successful: {data}"
            except:
                pass  # 如果不是有效的JSON，跳过检查
    
    @staticmethod
    def assert_response_error(response: httpx.Response, expected_status: int = None):
        """断言响应错误"""
        if expected_status:
            assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        else:
            assert response.status_code >= 400, f"Expected error status, got {response.status_code}"

@pytest.fixture
def test_utils():
    """测试工具夹具"""
    return TestUtils()

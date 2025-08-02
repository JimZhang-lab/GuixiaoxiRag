"""
API测试用例
"""
import pytest
import asyncio
import httpx
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

from test_config import TEST_CONFIG, SAMPLE_DOCUMENT, SAMPLE_QUERIES, setup_test_environment, cleanup_test_environment


class TestGuiXiaoXiRagAPI:
    """GuiXiaoXiRag API测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.base_url = TEST_CONFIG["base_url"]
        cls.timeout = TEST_CONFIG["timeout"]
        cls.test_dir = setup_test_environment()
        
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        cleanup_test_environment()
    
    @pytest.fixture
    async def client(self):
        """HTTP客户端fixture"""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            yield client
    
    async def test_health_check(self, client):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "system" in data
    
    async def test_root_endpoint(self, client):
        """测试根端点"""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
    
    async def test_insert_text(self, client):
        """测试插入单个文本"""
        payload = {
            "text": SAMPLE_DOCUMENT,
            "doc_id": "test_doc_1"
        }
        
        response = await client.post("/insert/text", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "track_id" in data["data"]
    
    async def test_insert_texts(self, client):
        """测试批量插入文本"""
        payload = {
            "texts": TEST_CONFIG["sample_texts"],
            "doc_ids": ["test_doc_2", "test_doc_3", "test_doc_4"]
        }
        
        response = await client.post("/insert/texts", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "track_id" in data["data"]
    
    async def test_query_modes(self, client):
        """测试获取查询模式"""
        response = await client.get("/query/modes")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "modes" in data["data"]
        assert "default" in data["data"]
        assert "recommended" in data["data"]
    
    async def test_query_hybrid(self, client):
        """测试混合模式查询"""
        # 先插入一些数据
        await self.test_insert_text(client)
        
        # 等待一段时间让数据处理完成
        await asyncio.sleep(2)
        
        payload = {
            "query": SAMPLE_QUERIES[0],
            "mode": "hybrid",
            "top_k": 10
        }
        
        response = await client.post("/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "result" in data["data"]
        assert data["data"]["mode"] == "hybrid"
    
    async def test_query_local(self, client):
        """测试本地模式查询"""
        payload = {
            "query": SAMPLE_QUERIES[1],
            "mode": "local",
            "top_k": 5
        }
        
        response = await client.post("/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mode"] == "local"
    
    async def test_query_global(self, client):
        """测试全局模式查询"""
        payload = {
            "query": SAMPLE_QUERIES[2],
            "mode": "global",
            "top_k": 15
        }
        
        response = await client.post("/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["mode"] == "global"
    
    async def test_batch_query(self, client):
        """测试批量查询"""
        queries = SAMPLE_QUERIES[:2]
        
        response = await client.post(
            "/query/batch",
            params={"mode": "hybrid", "top_k": 10},
            json=queries
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "results" in data["data"]
        assert len(data["data"]["results"]) == len(queries)
    
    async def test_knowledge_graph_stats(self, client):
        """测试知识图谱统计"""
        response = await client.get("/knowledge-graph/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total_nodes" in data["data"]
        assert "total_edges" in data["data"]
    
    async def test_system_status(self, client):
        """测试系统状态"""
        response = await client.get("/system/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "service_name" in data["data"]
        assert "version" in data["data"]
        assert "initialized" in data["data"]
    
    async def test_metrics(self, client):
        """测试性能指标"""
        response = await client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "total_requests" in data["data"]
        assert "total_errors" in data["data"]
    
    async def test_file_upload(self, client):
        """测试文件上传"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(SAMPLE_DOCUMENT)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test_upload.txt", f, "text/plain")}
                response = await client.post("/insert/file", files=files)
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "filename" in data["data"]
            assert "track_id" in data["data"]
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
    
    async def test_error_handling(self, client):
        """测试错误处理"""
        # 测试无效的查询模式
        payload = {
            "query": "测试查询",
            "mode": "invalid_mode"
        }
        
        response = await client.post("/query", json=payload)
        assert response.status_code == 422  # 验证错误
    
    async def test_large_text_insert(self, client):
        """测试大文本插入"""
        large_text = SAMPLE_DOCUMENT * 100  # 创建较大的文本
        
        payload = {
            "text": large_text,
            "doc_id": "large_test_doc"
        }
        
        response = await client.post("/insert/text", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True


# 运行测试的辅助函数
async def run_all_tests():
    """运行所有测试"""
    test_instance = TestGuiXiaoXiRagAPI()
    test_instance.setup_class()
    
    try:
        async with httpx.AsyncClient(
            base_url=test_instance.base_url, 
            timeout=test_instance.timeout
        ) as client:
            
            print("开始运行API测试...")
            
            # 运行各个测试
            await test_instance.test_health_check(client)
            print("✓ 健康检查测试通过")
            
            await test_instance.test_root_endpoint(client)
            print("✓ 根端点测试通过")
            
            await test_instance.test_insert_text(client)
            print("✓ 文本插入测试通过")
            
            await test_instance.test_query_modes(client)
            print("✓ 查询模式测试通过")
            
            await test_instance.test_query_hybrid(client)
            print("✓ 混合查询测试通过")
            
            await test_instance.test_system_status(client)
            print("✓ 系统状态测试通过")
            
            await test_instance.test_metrics(client)
            print("✓ 性能指标测试通过")
            
            print("所有测试完成！")
            
    except Exception as e:
        print(f"测试失败: {e}")
        raise
    finally:
        test_instance.teardown_class()


if __name__ == "__main__":
    asyncio.run(run_all_tests())

"""
问答系统测试
测试问答系统的所有功能，包括CRUD操作、查询、批量处理等
"""

import pytest
import asyncio
import json
from typing import List, Dict, Any
from conftest import TestClient, TestUtils, API_ENDPOINTS


class TestQASystem:
    """问答系统测试类"""
    
    @pytest.mark.asyncio
    async def test_qa_health_check(self, test_client: TestClient, test_utils: TestUtils):
        """测试问答系统健康检查"""
        response = await test_client.get(API_ENDPOINTS["qa"]["health"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        health_data = data["data"]
        assert "status" in health_data
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_create_qa_pair(self, test_client: TestClient, test_utils: TestUtils, sample_qa_pairs: List[Dict]):
        """测试创建单个问答对"""
        qa_pair = sample_qa_pairs[0]
        
        response = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_pair)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        assert "qa_id" in data["data"]
        
        # 返回创建的ID用于后续测试
        return data["data"]["qa_id"]
    
    @pytest.mark.asyncio
    async def test_create_qa_pair_validation(self, test_client: TestClient, test_utils: TestUtils):
        """测试问答对创建的参数验证"""
        # 测试空问题
        invalid_qa = {
            "question": "",
            "answer": "测试答案",
            "category": "test"
        }
        response = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=invalid_qa)
        test_utils.assert_response_error(response, 422)
        
        # 测试空答案
        invalid_qa = {
            "question": "测试问题",
            "answer": "",
            "category": "test"
        }
        response = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=invalid_qa)
        test_utils.assert_response_error(response, 422)
    
    @pytest.mark.asyncio
    async def test_batch_create_qa_pairs(self, test_client: TestClient, test_utils: TestUtils, sample_qa_pairs: List[Dict]):
        """测试批量创建问答对"""
        batch_request = {
            "qa_pairs": sample_qa_pairs,
            "skip_duplicate_check": False
        }
        
        response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        batch_data = data["data"]
        assert "added_count" in batch_data
        assert "qa_ids" in batch_data
        assert batch_data["added_count"] > 0
        
        return batch_data["qa_ids"]
    
    @pytest.mark.asyncio
    async def test_query_qa(self, test_client: TestClient, test_utils: TestUtils):
        """测试问答查询"""
        # 先创建一些测试数据
        qa_pair = {
            "question": "什么是测试查询？",
            "answer": "测试查询是验证查询功能的方法",
            "category": "测试",
            "confidence": 1.0
        }
        
        create_response = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_pair)
        test_utils.assert_response_success(create_response)
        
        # 执行查询
        query_request = {
            "question": "什么是测试查询",
            "top_k": 5,
            "min_similarity": 0.7
        }
        
        response = await test_client.post(API_ENDPOINTS["qa"]["query"], json_data=query_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "found" in data
        assert "response_time" in data
        
        if data["found"]:
            assert "answer" in data
            assert "similarity" in data
            assert "qa_id" in data
    
    @pytest.mark.asyncio
    async def test_batch_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试批量查询"""
        query_request = {
            "questions": [
                "什么是人工智能？",
                "机器学习是什么？",
                "深度学习的应用有哪些？"
            ],
            "top_k": 3,
            "parallel": True,
            "timeout": 60
        }
        
        response = await test_client.post(API_ENDPOINTS["qa"]["query_batch"], json_data=query_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        batch_data = data["data"]
        assert "total_queries" in batch_data
        assert "results" in batch_data
        assert len(batch_data["results"]) == len(query_request["questions"])
    
    @pytest.mark.asyncio
    async def test_get_qa_statistics(self, test_client: TestClient, test_utils: TestUtils):
        """测试获取问答统计信息"""
        response = await test_client.get(API_ENDPOINTS["qa"]["statistics"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        stats = data["data"]
        assert "total_pairs" in stats
        assert "categories" in stats
        assert isinstance(stats["total_pairs"], int)
        assert isinstance(stats["categories"], dict)
    
    @pytest.mark.asyncio
    async def test_delete_qa_pair(self, test_client: TestClient, test_utils: TestUtils):
        """测试删除单个问答对"""
        # 先创建一个问答对
        qa_pair = {
            "question": "这是要删除的问题",
            "answer": "这是要删除的答案",
            "category": "删除测试"
        }
        
        create_response = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_pair)
        test_utils.assert_response_success(create_response)
        
        qa_id = create_response.json()["data"]["qa_id"]
        
        # 删除问答对
        response = await test_client.delete(f"{API_ENDPOINTS['qa']['pairs']}/{qa_id}")
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        delete_data = data["data"]
        assert "deleted_count" in delete_data
        assert delete_data["deleted_count"] == 1
    
    @pytest.mark.asyncio
    async def test_batch_delete_qa_pairs(self, test_client: TestClient, test_utils: TestUtils):
        """测试批量删除问答对"""
        # 先创建多个问答对
        qa_pairs = [
            {
                "question": f"批量删除测试问题{i}",
                "answer": f"批量删除测试答案{i}",
                "category": "批量删除测试"
            }
            for i in range(3)
        ]
        
        batch_request = {"qa_pairs": qa_pairs}
        create_response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_request)
        test_utils.assert_response_success(create_response)
        
        qa_ids = create_response.json()["data"]["qa_ids"]
        
        # 批量删除
        delete_request = {"qa_ids": qa_ids}
        response = await test_client.delete(API_ENDPOINTS["qa"]["pairs"], json_data=delete_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        delete_data = data["data"]
        assert "deleted_count" in delete_data
        assert delete_data["deleted_count"] == len(qa_ids)
    
    @pytest.mark.asyncio
    async def test_delete_category(self, test_client: TestClient, test_utils: TestUtils):
        """测试删除分类"""
        # 先创建一些测试分类的问答对
        category_name = f"test_category_{test_utils.generate_test_id()}"
        qa_pairs = [
            {
                "question": f"分类测试问题{i}",
                "answer": f"分类测试答案{i}",
                "category": category_name
            }
            for i in range(2)
        ]
        
        batch_request = {"qa_pairs": qa_pairs}
        create_response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_request)
        test_utils.assert_response_success(create_response)
        
        # 删除分类
        response = await test_client.delete(f"{API_ENDPOINTS['qa']['categories']}/{category_name}")
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        delete_data = data["data"]
        assert "deleted_count" in delete_data
        assert "category" in delete_data
        assert delete_data["category"] == category_name
    
    @pytest.mark.asyncio
    async def test_qa_import_export(self, test_client: TestClient, test_utils: TestUtils, temp_dir):
        """测试问答数据导入导出"""
        # 测试导出
        response = await test_client.get(API_ENDPOINTS["qa"]["export"], params={"format": "json"})
        assert response.status_code == 200
        
        # 检查响应头
        assert "application/json" in response.headers.get("content-type", "")
        
        # 测试导入（需要文件上传）
        test_data = {
            "qa_pairs": [
                {
                    "question": "导入测试问题",
                    "answer": "导入测试答案",
                    "category": "导入测试"
                }
            ]
        }
        
        # 创建测试文件
        test_file = test_utils.create_test_file(
            json.dumps(test_data, ensure_ascii=False, indent=2),
            "test_import.json",
            temp_dir
        )
        
        with open(test_file, 'rb') as f:
            files = {"file": ("test_import.json", f, "application/json")}
            data = {
                "file_type": "json",
                "default_category": "imported",
                "overwrite_existing": "false"
            }
            
            response = await test_client.post(API_ENDPOINTS["qa"]["import"], data=data, files=files)
            test_utils.assert_response_success(response)
    
    @pytest.mark.asyncio
    async def test_clear_qa_data(self, test_client: TestClient, test_utils: TestUtils):
        """测试清空问答数据（谨慎测试）"""
        # 注意：这个测试会清空所有数据，通常在测试环境中运行
        # 在生产环境中应该跳过此测试
        
        # 先获取当前统计信息
        stats_response = await test_client.get(API_ENDPOINTS["qa"]["statistics"])
        test_utils.assert_response_success(stats_response)
        
        initial_count = stats_response.json()["data"]["total_pairs"]
        
        # 如果有数据，则测试清空功能
        if initial_count > 0:
            response = await test_client.delete(API_ENDPOINTS["qa"]["clear"])
            test_utils.assert_response_success(response)
            
            # 验证数据已清空
            stats_response = await test_client.get(API_ENDPOINTS["qa"]["statistics"])
            test_utils.assert_response_success(stats_response)
            
            final_count = stats_response.json()["data"]["total_pairs"]
            assert final_count == 0, "数据未完全清空"


class TestQASystemEdgeCases:
    """问答系统边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_duplicate_question_handling(self, test_client: TestClient, test_utils: TestUtils):
        """测试重复问题处理"""
        qa_pair = {
            "question": "这是重复问题测试",
            "answer": "第一个答案",
            "category": "重复测试",
            "skip_duplicate_check": False
        }
        
        # 创建第一个问答对
        response1 = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_pair)
        test_utils.assert_response_success(response1)
        
        # 尝试创建相同问题的问答对
        qa_pair["answer"] = "第二个答案"
        response2 = await test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_pair)
        
        # 应该被拒绝或返回重复警告
        data = response2.json()
        if not data.get("success", True):
            assert "重复" in data.get("message", "") or "duplicate" in data.get("message", "").lower()
    
    @pytest.mark.asyncio
    async def test_large_batch_processing(self, test_client: TestClient, test_utils: TestUtils):
        """测试大批量处理"""
        # 创建大量问答对（但不要太多，避免测试时间过长）
        large_batch = [
            {
                "question": f"大批量测试问题{i}",
                "answer": f"大批量测试答案{i}",
                "category": "大批量测试",
                "confidence": 0.8
            }
            for i in range(50)  # 50个问答对
        ]
        
        batch_request = {
            "qa_pairs": large_batch,
            "skip_duplicate_check": True  # 跳过重复检查以提高速度
        }
        
        response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        batch_data = data["data"]
        assert batch_data["added_count"] == len(large_batch)
    
    @pytest.mark.asyncio
    async def test_query_with_no_results(self, test_client: TestClient, test_utils: TestUtils):
        """测试无结果查询"""
        query_request = {
            "question": "这是一个不存在的问题xyz123",
            "top_k": 5,
            "min_similarity": 0.9  # 高相似度阈值
        }
        
        response = await test_client.post(API_ENDPOINTS["qa"]["query"], json_data=query_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "found" in data
        # 可能找到也可能找不到，但不应该出错

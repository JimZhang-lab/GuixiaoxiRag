"""
查询系统测试
测试查询系统的所有功能，包括智能查询、批量查询、不同模式等
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from conftest import TestClient, TestUtils, API_ENDPOINTS


class TestQuerySystem:
    """查询系统测试类"""
    
    @pytest.mark.asyncio
    async def test_get_query_modes(self, test_client: TestClient, test_utils: TestUtils):
        """测试获取查询模式列表"""
        response = await test_client.get(API_ENDPOINTS["query"]["modes"])
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        modes_data = data["data"]
        assert "modes" in modes_data or isinstance(modes_data, list)
    
    @pytest.mark.asyncio
    async def test_basic_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试基本查询功能"""
        # 先插入一些测试文档
        test_document = {
            "text": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。AI包括机器学习、深度学习、自然语言处理等多个子领域。",
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        # 插入文档
        doc_response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=test_document)
        test_utils.assert_response_success(doc_response)
        
        # 等待一段时间让文档被处理
        await asyncio.sleep(2)
        
        # 执行查询
        query_request = {
            "query": "什么是人工智能？",
            "mode": "hybrid",
            "top_k": 5,
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        query_data = data["data"]
        assert "answer" in query_data or "context" in query_data
    
    @pytest.mark.asyncio
    async def test_query_modes(self, test_client: TestClient, test_utils: TestUtils):
        """测试不同查询模式"""
        query_modes = ["local", "global", "hybrid", "naive", "mix"]
        
        base_query = {
            "query": "机器学习的应用有哪些？",
            "top_k": 3,
            "knowledge_base": "test_kb"
        }
        
        for mode in query_modes:
            query_request = {**base_query, "mode": mode}
            
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            # 某些模式可能不可用，但不应该导致服务器错误
            assert response.status_code in [200, 400, 404], f"Mode {mode} failed with status {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                assert "data" in data
                print(f"Mode {mode} succeeded")
    
    @pytest.mark.asyncio
    async def test_query_performance_modes(self, test_client: TestClient, test_utils: TestUtils):
        """测试不同性能模式"""
        performance_modes = ["fast", "balanced", "quality"]
        
        base_query = {
            "query": "深度学习的原理是什么？",
            "mode": "hybrid",
            "top_k": 3
        }
        
        for perf_mode in performance_modes:
            query_request = {**base_query, "performance_mode": perf_mode}
            
            start_time = time.time()
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                print(f"Performance mode {perf_mode}: {response_time:.2f}s")
                
                data = response.json()
                assert "data" in data
    
    @pytest.mark.asyncio
    async def test_batch_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试批量查询"""
        queries = [
            "什么是人工智能？",
            "机器学习有哪些类型？",
            "深度学习的应用领域有哪些？",
            "自然语言处理的主要任务是什么？",
            "计算机视觉技术有什么用途？"
        ]
        
        batch_request = {
            "queries": queries,
            "mode": "hybrid",
            "top_k": 3,
            "parallel": True,
            "timeout": 120
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["batch"], json_data=batch_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        batch_data = data["data"]
        assert "results" in batch_data
        assert len(batch_data["results"]) == len(queries)
        
        # 检查每个查询的结果
        for i, result in enumerate(batch_data["results"]):
            assert "query" in result
            assert result["query"] == queries[i]
            # 结果可能成功也可能失败，但应该有状态指示
            assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_optimized_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试优化参数查询"""
        optimized_request = {
            "query": "人工智能的发展历史",
            "mode": "hybrid",
            "performance_mode": "balanced",
            "custom_params": {
                "max_tokens": 2000,
                "temperature": 0.7,
                "enable_context_enhancement": True
            }
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["optimized"], json_data=optimized_request)
        # 优化查询可能不是所有系统都支持
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_query_with_context(self, test_client: TestClient, test_utils: TestUtils):
        """测试带上下文的查询"""
        query_request = {
            "query": "它的主要应用有哪些？",
            "mode": "hybrid",
            "context": "我们刚才讨论了机器学习的基本概念",
            "top_k": 5
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
    
    @pytest.mark.asyncio
    async def test_query_with_filters(self, test_client: TestClient, test_utils: TestUtils):
        """测试带过滤条件的查询"""
        query_request = {
            "query": "人工智能技术",
            "mode": "hybrid",
            "top_k": 10,
            "filters": {
                "category": "AI基础",
                "min_confidence": 0.8,
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                }
            }
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        # 过滤功能可能不是所有系统都支持
        assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_streaming_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试流式查询"""
        query_request = {
            "query": "请详细解释深度学习的工作原理",
            "mode": "hybrid",
            "stream": True,
            "top_k": 3
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        # 流式查询可能需要特殊处理
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            # 检查是否是流式响应
            content_type = response.headers.get("content-type", "")
            if "stream" in content_type or "event-stream" in content_type:
                print("Streaming response detected")
            else:
                # 可能是普通响应
                data = response.json()
                assert "data" in data
    
    @pytest.mark.asyncio
    async def test_query_timeout_handling(self, test_client: TestClient, test_utils: TestUtils):
        """测试查询超时处理"""
        # 设置一个很短的超时时间
        query_request = {
            "query": "请详细分析人工智能在各个行业的应用情况，包括技术实现、商业价值、发展趋势等多个方面",
            "mode": "quality",  # 使用质量模式，可能更慢
            "top_k": 20,
            "timeout": 1  # 1秒超时
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        # 可能超时也可能正常完成
        assert response.status_code in [200, 408, 504]
    
    @pytest.mark.asyncio
    async def test_multilingual_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试多语言查询"""
        # 先插入多语言文档
        documents = [
            {
                "text": "Artificial Intelligence is a branch of computer science that aims to create intelligent machines.",
                "language": "English",
                "knowledge_base": "test_kb"
            },
            {
                "text": "人工智能是计算机科学的一个分支，旨在创造智能机器。",
                "language": "中文",
                "knowledge_base": "test_kb"
            }
        ]
        
        for doc in documents:
            doc_response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=doc)
            test_utils.assert_response_success(doc_response)
        
        await asyncio.sleep(2)  # 等待处理
        
        # 测试不同语言的查询
        queries = [
            {"query": "What is artificial intelligence?", "language": "English"},
            {"query": "什么是人工智能？", "language": "中文"}
        ]
        
        for query_data in queries:
            query_request = {
                "query": query_data["query"],
                "mode": "hybrid",
                "language": query_data["language"],
                "top_k": 3
            }
            
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            test_utils.assert_response_success(response)


class TestQueryEdgeCases:
    """查询系统边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_empty_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试空查询"""
        query_request = {
            "query": "",
            "mode": "hybrid"
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        test_utils.assert_response_error(response, 422)
    
    @pytest.mark.asyncio
    async def test_very_long_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试超长查询"""
        very_long_query = "人工智能" * 1000  # 3000个字符
        
        query_request = {
            "query": very_long_query,
            "mode": "hybrid",
            "top_k": 3
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        # 可能成功也可能因为长度限制失败
        assert response.status_code in [200, 413, 422]
    
    @pytest.mark.asyncio
    async def test_special_characters_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试包含特殊字符的查询"""
        special_queries = [
            "AI & ML 技术？",
            "深度学习 (Deep Learning) 是什么？",
            "人工智能 vs 机器学习",
            "AI技术@2024年",
            "什么是AI？🤖",
            "SELECT * FROM ai_knowledge;",  # SQL注入测试
            "<script>alert('test')</script>",  # XSS测试
        ]
        
        for query_text in special_queries:
            query_request = {
                "query": query_text,
                "mode": "hybrid",
                "top_k": 3
            }
            
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            # 应该能处理特殊字符，不应该导致服务器错误
            assert response.status_code in [200, 400, 422], f"Query '{query_text}' caused server error"
    
    @pytest.mark.asyncio
    async def test_concurrent_queries(self, test_client: TestClient, test_utils: TestUtils):
        """测试并发查询"""
        queries = [
            "什么是人工智能？",
            "机器学习的类型有哪些？",
            "深度学习如何工作？",
            "自然语言处理的应用？",
            "计算机视觉技术？"
        ]
        
        # 创建并发查询任务
        tasks = []
        for query_text in queries:
            query_request = {
                "query": query_text,
                "mode": "hybrid",
                "top_k": 3
            }
            task = test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            tasks.append(task)
        
        # 等待所有查询完成
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        success_count = 0
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"并发查询 {i} 异常: {response}")
            else:
                if response.status_code == 200:
                    success_count += 1
                print(f"查询 {i} 状态码: {response.status_code}")
        
        # 至少应该有一些成功的查询
        assert success_count > 0, "所有并发查询都失败了"
    
    @pytest.mark.asyncio
    async def test_invalid_parameters(self, test_client: TestClient, test_utils: TestUtils):
        """测试无效参数"""
        invalid_requests = [
            # 无效的top_k
            {"query": "测试", "top_k": -1},
            {"query": "测试", "top_k": 0},
            {"query": "测试", "top_k": 10000},
            
            # 无效的模式
            {"query": "测试", "mode": "invalid_mode"},
            
            # 无效的性能模式
            {"query": "测试", "performance_mode": "invalid_performance"},
            
            # 无效的超时
            {"query": "测试", "timeout": -1},
        ]
        
        for invalid_request in invalid_requests:
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=invalid_request)
            test_utils.assert_response_error(response, 422)
    
    @pytest.mark.asyncio
    async def test_query_without_knowledge_base(self, test_client: TestClient, test_utils: TestUtils):
        """测试在没有知识库数据时的查询"""
        # 使用一个不存在的知识库
        query_request = {
            "query": "这个查询应该找不到任何结果",
            "mode": "hybrid",
            "knowledge_base": "nonexistent_kb",
            "top_k": 5
        }
        
        response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
        # 可能返回空结果也可能返回错误
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # 应该指示没有找到结果
            assert "data" in data

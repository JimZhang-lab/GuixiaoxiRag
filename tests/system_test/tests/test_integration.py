"""
集成测试
测试完整的业务流程，验证各个模块之间的协作
"""

import pytest
import asyncio
import json
import time
from typing import List, Dict, Any
from pathlib import Path
from conftest import TestClient, TestUtils, API_ENDPOINTS


class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    @pytest.mark.asyncio
    async def test_complete_knowledge_management_workflow(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试完整的知识管理工作流"""
        
        # 1. 系统健康检查
        health_response = await test_client.get(API_ENDPOINTS["system"]["health"])
        test_utils.assert_response_success(health_response)
        print("✓ 系统健康检查通过")
        
        # 2. 创建测试知识库
        kb_name = f"integration_test_kb_{test_utils.generate_test_id()}"
        kb_request = {
            "name": kb_name,
            "description": "集成测试知识库",
            "language": "中文",
            "config": {
                "chunk_size": 512,
                "chunk_overlap": 50
            }
        }
        
        kb_response = await test_client.post(API_ENDPOINTS["knowledge_base"]["create"], json_data=kb_request)
        if kb_response.status_code == 200:
            print("✓ 知识库创建成功")
        else:
            print("⚠ 知识库创建失败，使用默认知识库")
            kb_name = "default"
        
        # 3. 切换到测试知识库
        if kb_response.status_code == 200:
            switch_request = {"name": kb_name}
            switch_response = await test_client.post(API_ENDPOINTS["knowledge_base"]["switch"], json_data=switch_request)
            if switch_response.status_code == 200:
                print("✓ 知识库切换成功")
        
        # 4. 插入文档数据
        documents = [
            {
                "text": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。AI技术包括机器学习、深度学习、自然语言处理、计算机视觉等多个领域。",
                "doc_id": "ai_intro",
                "knowledge_base": kb_name,
                "language": "中文"
            },
            {
                "text": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。机器学习算法包括监督学习、无监督学习和强化学习三大类。",
                "doc_id": "ml_intro", 
                "knowledge_base": kb_name,
                "language": "中文"
            },
            {
                "text": "深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的工作方式。深度学习在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
                "doc_id": "dl_intro",
                "knowledge_base": kb_name,
                "language": "中文"
            }
        ]
        
        for doc in documents:
            doc_response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=doc)
            test_utils.assert_response_success(doc_response)
        
        print("✓ 文档插入完成")
        
        # 5. 等待文档处理
        await asyncio.sleep(3)
        
        # 6. 添加问答对
        qa_pairs = [
            {
                "question": "什么是人工智能？",
                "answer": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
                "category": "AI基础",
                "confidence": 1.0
            },
            {
                "question": "机器学习有哪些类型？",
                "answer": "机器学习主要包括监督学习、无监督学习和强化学习三大类。",
                "category": "机器学习",
                "confidence": 0.95
            }
        ]
        
        batch_qa_request = {"qa_pairs": qa_pairs}
        qa_response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_qa_request)
        test_utils.assert_response_success(qa_response)
        print("✓ 问答对添加完成")
        
        # 7. 执行查询测试
        queries = [
            "什么是人工智能？",
            "机器学习的分类有哪些？",
            "深度学习的应用领域？"
        ]
        
        for query in queries:
            # 文档查询
            doc_query_request = {
                "query": query,
                "mode": "hybrid",
                "top_k": 3,
                "knowledge_base": kb_name
            }
            
            doc_query_response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=doc_query_request)
            test_utils.assert_response_success(doc_query_response)
            
            # 问答查询
            qa_query_request = {
                "question": query,
                "top_k": 3,
                "min_similarity": 0.7
            }
            
            qa_query_response = await test_client.post(API_ENDPOINTS["qa"]["query"], json_data=qa_query_request)
            test_utils.assert_response_success(qa_query_response)
        
        print("✓ 查询测试完成")
        
        # 8. 获取系统统计信息
        qa_stats_response = await test_client.get(API_ENDPOINTS["qa"]["statistics"])
        test_utils.assert_response_success(qa_stats_response)
        
        system_metrics_response = await test_client.get(API_ENDPOINTS["system"]["metrics"])
        test_utils.assert_response_success(system_metrics_response)
        
        print("✓ 统计信息获取完成")
        
        # 9. 清理测试数据（可选）
        if kb_response.status_code == 200:
            # 删除测试知识库
            delete_response = await test_client.delete(f"/api/v1/knowledge-bases/{kb_name}")
            if delete_response.status_code == 200:
                print("✓ 测试知识库清理完成")
        
        print("🎉 完整工作流测试成功")
    
    @pytest.mark.asyncio
    async def test_file_upload_to_query_workflow(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试文件上传到查询的完整流程"""
        
        # 1. 创建测试文件
        test_content = """
# AI技术指南

## 概述
人工智能技术正在快速发展，包括以下主要领域：

## 机器学习
- 监督学习：使用标记数据训练模型
- 无监督学习：从未标记数据中发现模式
- 强化学习：通过试错学习最优策略

## 深度学习
- 神经网络：模拟人脑神经元结构
- 卷积神经网络：专门用于图像处理
- 循环神经网络：处理序列数据

## 自然语言处理
- 文本分析：理解文本内容和情感
- 机器翻译：自动翻译不同语言
- 对话系统：构建智能聊天机器人

## 应用场景
1. 医疗诊断
2. 自动驾驶
3. 金融风控
4. 智能推荐
        """
        
        test_file = test_utils.create_test_file(test_content, "ai_guide.md", temp_dir)
        
        # 2. 上传文件
        with open(test_file, 'rb') as f:
            files = {"file": ("ai_guide.md", f, "text/markdown")}
            data = {
                "knowledge_base": "test_kb",
                "language": "中文",
                "extract_metadata": "true"
            }
            
            upload_response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            test_utils.assert_response_success(upload_response)
        
        print("✓ 文件上传成功")
        
        # 3. 等待文件处理
        await asyncio.sleep(5)
        
        # 4. 执行相关查询
        queries = [
            "什么是监督学习？",
            "深度学习包括哪些技术？",
            "AI在医疗领域的应用？",
            "自然语言处理的主要任务？"
        ]
        
        successful_queries = 0
        for query in queries:
            query_request = {
                "query": query,
                "mode": "hybrid",
                "top_k": 5
            }
            
            response = await test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_request)
            if response.status_code == 200:
                successful_queries += 1
                data = response.json()
                print(f"✓ 查询 '{query}' 成功")
        
        assert successful_queries > 0, "所有查询都失败了"
        print(f"✓ {successful_queries}/{len(queries)} 个查询成功")
    
    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self, test_client: TestClient, test_utils: TestUtils):
        """测试批量处理工作流"""
        
        # 1. 批量插入文档
        texts = [
            f"这是测试文档{i}，包含关于人工智能技术的内容。" for i in range(10)
        ]
        
        batch_text_request = {
            "texts": texts,
            "doc_ids": [f"batch_doc_{i}" for i in range(10)],
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        batch_insert_response = await test_client.post(API_ENDPOINTS["document"]["insert_texts"], json_data=batch_text_request)
        test_utils.assert_response_success(batch_insert_response)
        print("✓ 批量文档插入成功")
        
        # 2. 批量添加问答对
        qa_pairs = [
            {
                "question": f"批量测试问题{i}？",
                "answer": f"这是批量测试答案{i}",
                "category": "批量测试",
                "confidence": 0.8
            }
            for i in range(5)
        ]
        
        batch_qa_request = {"qa_pairs": qa_pairs}
        batch_qa_response = await test_client.post(API_ENDPOINTS["qa"]["pairs_batch"], json_data=batch_qa_request)
        test_utils.assert_response_success(batch_qa_response)
        print("✓ 批量问答对添加成功")
        
        # 3. 批量查询
        queries = [f"批量测试问题{i}" for i in range(5)]
        
        batch_query_request = {
            "queries": queries,
            "mode": "hybrid",
            "top_k": 3,
            "parallel": True
        }
        
        batch_query_response = await test_client.post(API_ENDPOINTS["query"]["batch"], json_data=batch_query_request)
        test_utils.assert_response_success(batch_query_response)
        print("✓ 批量查询成功")
        
        # 4. 批量问答查询
        qa_batch_query_request = {
            "questions": queries,
            "top_k": 3,
            "parallel": True
        }
        
        qa_batch_response = await test_client.post(API_ENDPOINTS["qa"]["query_batch"], json_data=qa_batch_query_request)
        test_utils.assert_response_success(qa_batch_response)
        print("✓ 批量问答查询成功")
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, test_client: TestClient, test_utils: TestUtils):
        """测试错误恢复工作流"""
        
        # 1. 尝试无效操作
        invalid_requests = [
            # 无效的文档插入
            {
                "endpoint": API_ENDPOINTS["document"]["insert_text"],
                "method": "POST",
                "data": {"text": "", "knowledge_base": "test_kb"}
            },
            # 无效的查询
            {
                "endpoint": API_ENDPOINTS["query"]["query"],
                "method": "POST", 
                "data": {"query": "", "mode": "invalid_mode"}
            },
            # 无效的问答对
            {
                "endpoint": API_ENDPOINTS["qa"]["pairs"],
                "method": "POST",
                "data": {"question": "", "answer": ""}
            }
        ]
        
        for req in invalid_requests:
            if req["method"] == "POST":
                response = await test_client.post(req["endpoint"], json_data=req["data"])
            else:
                response = await test_client.get(req["endpoint"])
            
            # 应该返回错误，但不应该导致系统崩溃
            assert response.status_code >= 400
        
        print("✓ 错误处理正常")
        
        # 2. 验证系统仍然正常工作
        health_response = await test_client.get(API_ENDPOINTS["system"]["health"])
        test_utils.assert_response_success(health_response)
        print("✓ 系统恢复正常")
        
        # 3. 执行正常操作验证功能
        valid_doc = {
            "text": "这是错误恢复测试文档",
            "knowledge_base": "test_kb"
        }
        
        doc_response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=valid_doc)
        test_utils.assert_response_success(doc_response)
        print("✓ 正常功能验证成功")


class TestConcurrentOperations:
    """并发操作测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_document_and_query(self, test_client: TestClient, test_utils: TestUtils):
        """测试并发文档操作和查询"""
        
        # 创建并发任务
        tasks = []
        
        # 文档插入任务
        for i in range(5):
            doc_data = {
                "text": f"并发测试文档{i}，包含AI相关内容",
                "doc_id": f"concurrent_doc_{i}",
                "knowledge_base": "test_kb"
            }
            task = test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=doc_data)
            tasks.append(("insert", task))
        
        # 查询任务
        for i in range(3):
            query_data = {
                "query": f"并发查询测试{i}",
                "mode": "hybrid",
                "top_k": 3
            }
            task = test_client.post(API_ENDPOINTS["query"]["query"], json_data=query_data)
            tasks.append(("query", task))
        
        # 问答任务
        for i in range(2):
            qa_data = {
                "question": f"并发问答测试{i}？",
                "answer": f"并发问答答案{i}",
                "category": "并发测试"
            }
            task = test_client.post(API_ENDPOINTS["qa"]["pairs"], json_data=qa_data)
            tasks.append(("qa", task))
        
        # 执行所有任务
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # 统计结果
        success_count = 0
        error_count = 0
        exception_count = 0
        
        for i, result in enumerate(results):
            task_type = tasks[i][0]
            if isinstance(result, Exception):
                exception_count += 1
                print(f"任务 {task_type} 异常: {result}")
            elif result.status_code == 200:
                success_count += 1
            else:
                error_count += 1
                print(f"任务 {task_type} 错误: {result.status_code}")
        
        print(f"并发测试结果: 成功={success_count}, 错误={error_count}, 异常={exception_count}")
        
        # 大部分操作应该成功
        total_tasks = len(tasks)
        success_rate = success_count / total_tasks
        assert success_rate >= 0.6, f"并发操作成功率过低: {success_rate:.2%}"
    
    @pytest.mark.asyncio
    async def test_system_stability_under_load(self, test_client: TestClient, test_utils: TestUtils):
        """测试负载下的系统稳定性"""
        
        # 持续发送请求一段时间
        duration = 10  # 10秒
        start_time = time.time()
        request_count = 0
        success_count = 0
        
        while time.time() - start_time < duration:
            # 发送健康检查请求
            try:
                response = await test_client.get(API_ENDPOINTS["system"]["health"])
                request_count += 1
                if response.status_code == 200:
                    success_count += 1
            except Exception as e:
                print(f"请求异常: {e}")
                request_count += 1
            
            # 短暂延迟
            await asyncio.sleep(0.1)
        
        print(f"负载测试: {request_count} 个请求, {success_count} 个成功")
        
        # 计算成功率
        if request_count > 0:
            success_rate = success_count / request_count
            assert success_rate >= 0.8, f"负载下成功率过低: {success_rate:.2%}"
        
        # 验证系统仍然响应
        final_health = await test_client.get(API_ENDPOINTS["system"]["health"])
        test_utils.assert_response_success(final_health)
        print("✓ 系统在负载后仍然稳定")

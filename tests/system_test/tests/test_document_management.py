"""
文档管理测试
测试文档管理的所有功能，包括文本插入、文件上传、批量处理等
"""

import pytest
import asyncio
import json
import tempfile
from typing import List, Dict, Any
from pathlib import Path
from conftest import TestClient, TestUtils, API_ENDPOINTS


class TestDocumentManagement:
    """文档管理测试类"""
    
    @pytest.mark.asyncio
    async def test_insert_single_text(self, test_client: TestClient, test_utils: TestUtils, sample_documents: List[Dict]):
        """测试插入单个文本文档"""
        document = sample_documents[0]
        
        response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=document)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        doc_data = data["data"]
        assert "track_id" in doc_data
        assert "doc_id" in doc_data
        
        return doc_data["track_id"]
    
    @pytest.mark.asyncio
    async def test_insert_text_validation(self, test_client: TestClient, test_utils: TestUtils):
        """测试文本插入的参数验证"""
        # 测试空文本
        invalid_doc = {
            "text": "",
            "knowledge_base": "test_kb"
        }
        response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=invalid_doc)
        test_utils.assert_response_error(response, 422)
        
        # 测试过长文本（如果有限制）
        very_long_text = "a" * 200000  # 200KB文本
        long_doc = {
            "text": very_long_text,
            "knowledge_base": "test_kb"
        }
        response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=long_doc)
        # 可能成功也可能失败，取决于系统限制
        assert response.status_code in [200, 413, 422]
    
    @pytest.mark.asyncio
    async def test_insert_multiple_texts(self, test_client: TestClient, test_utils: TestUtils, sample_documents: List[Dict]):
        """测试批量插入文本文档"""
        texts_request = {
            "texts": [doc["text"] for doc in sample_documents],
            "doc_ids": [doc["doc_id"] for doc in sample_documents],
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        response = await test_client.post(API_ENDPOINTS["document"]["insert_texts"], json_data=texts_request)
        test_utils.assert_response_success(response)
        
        data = response.json()
        assert "data" in data
        batch_data = data["data"]
        assert "track_id" in batch_data
        
        return batch_data["track_id"]
    
    @pytest.mark.asyncio
    async def test_insert_file_txt(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试上传TXT文件"""
        # 创建测试TXT文件
        test_content = """
        这是一个测试文档。
        
        内容包括：
        1. 人工智能基础知识
        2. 机器学习算法
        3. 深度学习应用
        
        这些内容将被处理并存储到知识库中。
        """
        
        test_file = test_utils.create_test_file(test_content, "test_document.txt", temp_dir)
        
        with open(test_file, 'rb') as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "knowledge_base": "test_kb",
                "language": "中文",
                "extract_metadata": "true"
            }
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            test_utils.assert_response_success(response)
            
            response_data = response.json()
            assert "data" in response_data
            file_data = response_data["data"]
            assert "track_id" in file_data
            assert "file_info" in file_data
    
    @pytest.mark.asyncio
    async def test_insert_file_json(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试上传JSON文件"""
        # 创建测试JSON文件
        test_data = {
            "title": "AI知识库",
            "content": "这是一个包含人工智能知识的JSON文档",
            "topics": ["机器学习", "深度学习", "自然语言处理"],
            "metadata": {
                "author": "测试用户",
                "created_date": "2024-01-01",
                "version": "1.0"
            }
        }
        
        test_file = test_utils.create_test_file(
            json.dumps(test_data, ensure_ascii=False, indent=2),
            "test_data.json",
            temp_dir
        )
        
        with open(test_file, 'rb') as f:
            files = {"file": ("test_data.json", f, "application/json")}
            data = {
                "knowledge_base": "test_kb",
                "language": "中文",
                "extract_metadata": "true"
            }
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            test_utils.assert_response_success(response)
    
    @pytest.mark.asyncio
    async def test_insert_file_markdown(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试上传Markdown文件"""
        # 创建测试Markdown文件
        markdown_content = """
# 人工智能指南

## 概述
人工智能（AI）是计算机科学的一个重要分支。

## 主要领域

### 机器学习
- 监督学习
- 无监督学习
- 强化学习

### 深度学习
- 神经网络
- 卷积神经网络
- 循环神经网络

### 自然语言处理
- 文本分析
- 语言生成
- 机器翻译

## 应用场景
1. 图像识别
2. 语音识别
3. 推荐系统
4. 自动驾驶

## 总结
AI技术正在快速发展，为各行各业带来变革。
        """
        
        test_file = test_utils.create_test_file(markdown_content, "ai_guide.md", temp_dir)
        
        with open(test_file, 'rb') as f:
            files = {"file": ("ai_guide.md", f, "text/markdown")}
            data = {
                "knowledge_base": "test_kb",
                "language": "中文",
                "extract_metadata": "true"
            }
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            test_utils.assert_response_success(response)
    
    @pytest.mark.asyncio
    async def test_insert_multiple_files(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试批量上传文件"""
        # 创建多个测试文件
        files_data = [
            ("file1.txt", "这是第一个测试文件的内容。", "text/plain"),
            ("file2.txt", "这是第二个测试文件的内容。", "text/plain"),
            ("file3.md", "# 第三个文件\n这是Markdown格式的内容。", "text/markdown")
        ]
        
        test_files = []
        for filename, content, content_type in files_data:
            test_file = test_utils.create_test_file(content, filename, temp_dir)
            test_files.append((filename, test_file, content_type))
        
        # 准备文件上传
        files = []
        for filename, file_path, content_type in test_files:
            with open(file_path, 'rb') as f:
                files.append(("files", (filename, f.read(), content_type)))
        
        data = {
            "knowledge_base": "test_kb",
            "language": "中文",
            "extract_metadata": "true"
        }
        
        # 重新打开文件进行上传
        file_handles = []
        try:
            for filename, file_path, content_type in test_files:
                f = open(file_path, 'rb')
                file_handles.append(f)
                files.append(("files", (filename, f, content_type)))
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_files"], data=data, files=dict(files))
            test_utils.assert_response_success(response)
            
            response_data = response.json()
            assert "data" in response_data
            
        finally:
            # 关闭文件句柄
            for f in file_handles:
                f.close()
    
    @pytest.mark.asyncio
    async def test_insert_directory(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试从目录插入文件"""
        # 创建测试目录结构
        test_dir = temp_dir / "test_documents"
        test_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        sub_dir = test_dir / "subdirectory"
        sub_dir.mkdir(exist_ok=True)
        
        # 创建测试文件
        files_to_create = [
            (test_dir / "doc1.txt", "这是根目录的文档1"),
            (test_dir / "doc2.md", "# 根目录文档2\n这是Markdown内容"),
            (sub_dir / "subdoc1.txt", "这是子目录的文档1"),
            (sub_dir / "subdoc2.json", '{"title": "子目录JSON文档", "content": "JSON内容"}')
        ]
        
        for file_path, content in files_to_create:
            file_path.write_text(content, encoding='utf-8')
        
        # 测试目录插入
        directory_request = {
            "directory_path": str(test_dir),
            "knowledge_base": "test_kb",
            "language": "中文",
            "recursive": True,
            "file_patterns": ["*.txt", "*.md", "*.json"]
        }
        
        response = await test_client.post(API_ENDPOINTS["document"]["insert_directory"], json_data=directory_request)
        test_utils.assert_response_success(response)
        
        response_data = response.json()
        assert "data" in response_data
        dir_data = response_data["data"]
        assert "processed_files" in dir_data or "track_id" in dir_data
    
    @pytest.mark.asyncio
    async def test_file_format_support(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试不同文件格式支持"""
        # 测试支持的格式
        supported_formats = [
            ("test.txt", "纯文本内容", "text/plain"),
            ("test.md", "# Markdown内容", "text/markdown"),
            ("test.json", '{"key": "JSON内容"}', "application/json"),
            ("test.csv", "列1,列2\n值1,值2", "text/csv"),
            ("test.xml", '<?xml version="1.0"?><root><item>XML内容</item></root>', "application/xml")
        ]
        
        for filename, content, content_type in supported_formats:
            test_file = test_utils.create_test_file(content, filename, temp_dir)
            
            with open(test_file, 'rb') as f:
                files = {"file": (filename, f, content_type)}
                data = {
                    "knowledge_base": "test_kb",
                    "extract_metadata": "true"
                }
                
                response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
                # 某些格式可能不支持，但不应该导致服务器错误
                assert response.status_code in [200, 415, 422], f"Unexpected status for {filename}: {response.status_code}"
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试大文件处理"""
        # 创建一个较大的文件（但不要太大，避免测试时间过长）
        large_content = "这是一个大文件的内容。\n" * 10000  # 约250KB
        
        test_file = test_utils.create_test_file(large_content, "large_file.txt", temp_dir)
        
        with open(test_file, 'rb') as f:
            files = {"file": ("large_file.txt", f, "text/plain")}
            data = {
                "knowledge_base": "test_kb",
                "language": "中文",
                "extract_metadata": "true"
            }
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            # 可能成功也可能因为大小限制失败
            assert response.status_code in [200, 413, 422]
    
    @pytest.mark.asyncio
    async def test_unsupported_file_format(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试不支持的文件格式"""
        # 创建一个不支持的文件格式
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        
        test_file = temp_dir / "test_image.png"
        test_file.write_bytes(binary_content)
        
        with open(test_file, 'rb') as f:
            files = {"file": ("test_image.png", f, "image/png")}
            data = {
                "knowledge_base": "test_kb",
                "extract_metadata": "true"
            }
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            # 应该返回不支持的格式错误
            test_utils.assert_response_error(response, 415)


class TestDocumentEdgeCases:
    """文档管理边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_empty_file_upload(self, test_client: TestClient, test_utils: TestUtils, temp_dir: Path):
        """测试上传空文件"""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
        
        with open(empty_file, 'rb') as f:
            files = {"file": ("empty.txt", f, "text/plain")}
            data = {"knowledge_base": "test_kb"}
            
            response = await test_client.post(API_ENDPOINTS["document"]["insert_file"], data=data, files=files)
            # 可能成功也可能失败，取决于系统策略
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_special_characters_in_content(self, test_client: TestClient, test_utils: TestUtils):
        """测试包含特殊字符的内容"""
        special_content = {
            "text": "这是包含特殊字符的文本：\n🚀 emoji\n中文字符\n\"引号\"\n'单引号'\n<标签>\n&符号\n数学符号：∑∏∫",
            "knowledge_base": "test_kb",
            "language": "中文"
        }
        
        response = await test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=special_content)
        test_utils.assert_response_success(response)
    
    @pytest.mark.asyncio
    async def test_concurrent_document_insertion(self, test_client: TestClient, test_utils: TestUtils):
        """测试并发文档插入"""
        # 创建多个并发任务
        tasks = []
        for i in range(5):
            document = {
                "text": f"并发测试文档{i}的内容",
                "doc_id": f"concurrent_doc_{i}",
                "knowledge_base": "test_kb"
            }
            task = test_client.post(API_ENDPOINTS["document"]["insert_text"], json_data=document)
            tasks.append(task)
        
        # 等待所有任务完成
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        success_count = 0
        for response in responses:
            if isinstance(response, Exception):
                print(f"并发请求异常: {response}")
            else:
                if response.status_code == 200:
                    success_count += 1
        
        # 至少应该有一些成功的请求
        assert success_count > 0, "所有并发请求都失败了"

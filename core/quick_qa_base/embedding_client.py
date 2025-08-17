"""
Embedding客户端

使用真实的embedding模型进行文本向量化
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Embedding客户端
    
    使用OpenAI兼容的API进行文本向量化
    """
    
    def __init__(self, 
                 api_base: str = None,
                 api_key: str = None,
                 model: str = None,
                 embedding_dim: int = None,
                 max_token_size: int = None,
                 timeout: int = 30):
        """
        初始化Embedding客户端
        
        Args:
            api_base: API基础URL
            api_key: API密钥
            model: 模型名称
            embedding_dim: 向量维度
            max_token_size: 最大token数
            timeout: 请求超时时间
        """
        # 从环境变量获取配置
        self.api_base = api_base or os.getenv("OPENAI_EMBEDDING_API_BASE", "http://localhost:8200/v1")
        self.api_key = api_key or os.getenv("OPENAI_EMBEDDING_API_KEY", "sk-8a2b5c9d-e1f3-4g7h-6i2j-k3l4m5n6o7p8")
        self.model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "embedding_qwen")
        self.embedding_dim = embedding_dim or int(os.getenv("EMBEDDING_DIM", "2560"))
        self.max_token_size = max_token_size or int(os.getenv("MAX_TOKEN_SIZE", "8192"))
        self.timeout = timeout
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_texts": 0,
            "total_time": 0.0,
            "avg_time_per_request": 0.0,
            "avg_time_per_text": 0.0
        }
        
        logger.info(f"EmbeddingClient initialized:")
        logger.info(f"  API Base: {self.api_base}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Embedding Dim: {self.embedding_dim}")
        logger.info(f"  Max Token Size: {self.max_token_size}")
    
    async def __call__(self, texts: List[str], _priority: int = 1) -> List[List[float]]:
        """
        向量化文本列表
        
        Args:
            texts: 文本列表
            _priority: 优先级（兼容参数）
            
        Returns:
            向量列表
        """
        return await self.embed_texts(texts)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        向量化文本列表
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        if not texts:
            return []
        
        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["total_texts"] += len(texts)
        
        try:
            # 准备请求数据
            request_data = {
                "input": texts,
                "model": self.model
            }
            
            # 发送请求
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                url = f"{self.api_base}/embeddings"
                
                async with session.post(url, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # 提取向量
                        embeddings = []
                        for item in result.get("data", []):
                            embedding = item.get("embedding", [])
                            embeddings.append(embedding)
                        
                        # 验证向量维度
                        if embeddings and len(embeddings[0]) != self.embedding_dim:
                            logger.warning(f"Expected embedding dim {self.embedding_dim}, got {len(embeddings[0])}")
                        
                        # 更新统计
                        request_time = time.time() - start_time
                        self.stats["successful_requests"] += 1
                        self.stats["total_time"] += request_time
                        self._update_avg_stats()
                        
                        logger.debug(f"Successfully embedded {len(texts)} texts in {request_time:.3f}s")
                        return embeddings
                    
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
        
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"Error embedding texts: {e}")
            raise
    
    async def embed_single_text(self, text: str) -> List[float]:
        """
        向量化单个文本
        
        Args:
            text: 文本
            
        Returns:
            向量
        """
        embeddings = await self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def _update_avg_stats(self):
        """更新平均统计信息"""
        if self.stats["successful_requests"] > 0:
            self.stats["avg_time_per_request"] = self.stats["total_time"] / self.stats["successful_requests"]
        
        if self.stats["total_texts"] > 0:
            self.stats["avg_time_per_text"] = self.stats["total_time"] / self.stats["total_texts"]
    
    async def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_text = "测试连接"
            embedding = await self.embed_single_text(test_text)
            
            if embedding and len(embedding) == self.embedding_dim:
                logger.info(f"Connection test successful. Embedding dim: {len(embedding)}")
                return True
            else:
                logger.error(f"Connection test failed. Expected dim: {self.embedding_dim}, got: {len(embedding) if embedding else 0}")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "config": {
                "api_base": self.api_base,
                "model": self.model,
                "embedding_dim": self.embedding_dim,
                "max_token_size": self.max_token_size
            },
            "stats": self.stats.copy()
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_texts": 0,
            "total_time": 0.0,
            "avg_time_per_request": 0.0,
            "avg_time_per_text": 0.0
        }
        logger.info("Statistics reset")


class MockEmbeddingClient:
    """
    模拟Embedding客户端
    
    用于测试和开发环境
    """
    
    def __init__(self, embedding_dim: int = 2560):
        """
        初始化模拟客户端
        
        Args:
            embedding_dim: 向量维度
        """
        self.embedding_dim = embedding_dim
        self.stats = {
            "total_requests": 0,
            "total_texts": 0
        }
        
        logger.info(f"MockEmbeddingClient initialized with dim: {embedding_dim}")
    
    async def __call__(self, texts: List[str], _priority: int = 1) -> List[List[float]]:
        """向量化文本列表"""
        return await self.embed_texts(texts)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        模拟向量化文本列表
        
        Args:
            texts: 文本列表
            
        Returns:
            模拟向量列表
        """
        import numpy as np
        import hashlib
        
        self.stats["total_requests"] += 1
        self.stats["total_texts"] += len(texts)
        
        embeddings = []
        for text in texts:
            # 使用文本哈希生成一致的向量
            hash_obj = hashlib.md5(text.encode())
            seed = int(hash_obj.hexdigest()[:8], 16)
            np.random.seed(seed)
            embedding = np.random.rand(self.embedding_dim).tolist()
            embeddings.append(embedding)
        
        # 模拟处理时间
        await asyncio.sleep(0.01 * len(texts))
        
        return embeddings
    
    async def embed_single_text(self, text: str) -> List[float]:
        """模拟向量化单个文本"""
        embeddings = await self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    async def test_connection(self) -> bool:
        """模拟测试连接"""
        return True
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return {
            "config": {
                "type": "mock",
                "embedding_dim": self.embedding_dim
            },
            "stats": self.stats.copy()
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            "total_requests": 0,
            "total_texts": 0
        }


def create_embedding_client(use_mock: bool = False) -> EmbeddingClient:
    """
    创建embedding客户端
    
    Args:
        use_mock: 是否使用模拟客户端
        
    Returns:
        Embedding客户端实例
    """
    if use_mock:
        return MockEmbeddingClient()
    else:
        return EmbeddingClient()

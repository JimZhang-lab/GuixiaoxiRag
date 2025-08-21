from core.common.llm_client import create_embedding_function
from typing import Callable, Optional, List
import numpy as np
from functools import lru_cache

class SimilarityCalculator:
    """相似度计算器"""
    
    def __init__(self):
        self.embedding_func = None
        self._embedding_cache = {}
        
    async def _ensure_embedding_func(self):
        """确保embedding函数已初始化"""
        if self.embedding_func is None:
            self.embedding_func = await create_embedding_function()
    
    async def get_vector_embedding(self, text: str) -> np.ndarray:
        """获取文本的向量嵌入"""
        # 缓存检查
        if text in self._embedding_cache:
            return self._embedding_cache[text]
            
        await self._ensure_embedding_func()
        embedding = await self.embedding_func([text])
        
        result = np.array(embedding[0], dtype=np.float32)
        # 归一化向量
        result = result / np.linalg.norm(result)
        
        # 缓存结果
        self._embedding_cache[text] = result
        return result
    
    async def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """计算两个文本的余弦相似度"""
        embedding_a = await self.get_vector_embedding(text_a)
        embedding_b = await self.get_vector_embedding(text_b)
        
        # 由于向量已归一化，直接点积即为余弦相似度
        score = np.dot(embedding_a, embedding_b)
        return float(np.clip(score, 0, 1))
    
    async def batch_calculate_similarity(self, texts: List[str], reference_text: str) -> List[float]:
        """批量计算相似度，提高效率"""
        await self._ensure_embedding_func()
        
        # 批量获取embeddings
        all_texts = texts + [reference_text]
        embeddings = await self.embedding_func(all_texts)
        
        # 归一化所有向量
        embeddings = np.array(embeddings, dtype=np.float32)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # 计算相似度
        reference_embedding = embeddings[-1]
        similarities = np.dot(embeddings[:-1], reference_embedding)
        
        return [float(np.clip(sim, 0, 1)) for sim in similarities]
    
    def clear_cache(self):
        """清空缓存"""
        self._embedding_cache.clear()
        

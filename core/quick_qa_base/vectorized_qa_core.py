"""
向量化问答对存储核心模块

专注于向量化存储和检索功能的精简实现：
1. 问题自动向量化并存储
2. 答案以文本格式与向量化问题一同存放
3. 高效的相似度搜索和检索
"""

import asyncio
import json
import os
import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QAPair:
    """问答对数据结构"""
    id: str
    question: str
    answer: str
    question_vector: Optional[np.ndarray] = None
    category: str = "general"
    confidence: float = 1.0
    keywords: List[str] = field(default_factory=list)
    source: str = "manual"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        vector_data = None
        if self.question_vector is not None:
            if hasattr(self.question_vector, 'tolist'):
                vector_data = self.question_vector.tolist()
            elif isinstance(self.question_vector, list):
                vector_data = self.question_vector
            else:
                vector_data = list(self.question_vector)
        
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "question_vector": vector_data,
            "category": self.category,
            "confidence": self.confidence,
            "keywords": self.keywords,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QAPair':
        """从字典创建QAPair对象"""
        qa_pair = cls(
            id=data["id"],
            question=data["question"],
            answer=data["answer"],
            category=data.get("category", "general"),
            confidence=data.get("confidence", 1.0),
            keywords=data.get("keywords", []),
            source=data.get("source", "manual"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
        
        if data.get("question_vector"):
            qa_pair.question_vector = np.array(data["question_vector"])
        
        return qa_pair


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    qa_pair: QAPair
    similarity: float
    rank: int


class VectorizedQAStorage:
    """
    向量化问答对存储系统
    
    核心功能：
    - 问题自动向量化存储
    - 答案文本格式保存
    - 向量化问题和答案一同存放
    - 高效相似度搜索
    """
    
    def __init__(self, 
                 storage_file: str,
                 embedding_func,
                 similarity_threshold: float = 0.85,
                 max_results: int = 10):
        """
        初始化向量化Q&A存储
        
        Args:
            storage_file: 存储文件路径
            embedding_func: 向量化函数
            similarity_threshold: 相似度阈值
            max_results: 最大返回结果数
        """
        self.storage_file = storage_file
        self.embedding_func = embedding_func
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        
        # 内存中的Q&A对存储
        self.qa_pairs: Dict[str, QAPair] = {}
        
        # 向量索引（用于快速搜索）
        self.question_vectors: Optional[np.ndarray] = None
        self.vector_to_id: List[str] = []
        
        # 统计信息
        self.stats = {
            "total_pairs": 0,
            "total_queries": 0,
            "successful_queries": 0,
            "vector_rebuilds": 0,
            "total_query_time": 0.0
        }
        
        logger.info(f"VectorizedQAStorage initialized with file: {storage_file}")
    
    async def initialize(self) -> bool:
        """初始化存储系统"""
        try:
            # 创建存储目录
            storage_dir = os.path.dirname(self.storage_file)
            if storage_dir:
                os.makedirs(storage_dir, exist_ok=True)
            
            # 加载现有数据
            if os.path.exists(self.storage_file):
                await self.load_from_file()
            
            logger.info("VectorizedQAStorage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorizedQAStorage: {e}")
            return False
    
    def _generate_id(self, question: str) -> str:
        """生成问题的唯一ID"""
        import hashlib
        hash_obj = hashlib.md5(question.encode('utf-8'))
        return f"qa_{hash_obj.hexdigest()[:16]}"
    
    async def add_qa_pair(self, 
                         question: str, 
                         answer: str,
                         category: str = "general",
                         confidence: float = 1.0,
                         keywords: List[str] = None,
                         source: str = "manual") -> str:
        """
        添加单个问答对
        
        Args:
            question: 问题文本
            answer: 答案文本
            category: 分类
            confidence: 置信度
            keywords: 关键词列表
            source: 来源
            
        Returns:
            问答对的ID
        """
        try:
            # 生成ID
            qa_id = self._generate_id(question)
            
            # 检查是否已存在
            if qa_id in self.qa_pairs:
                logger.warning(f"Q&A pair already exists: {question[:50]}...")
                return qa_id
            
            # 向量化问题
            question_embedding = await self.embedding_func([question])
            question_vector = np.array(question_embedding[0])
            
            # 创建Q&A对象
            qa_pair = QAPair(
                id=qa_id,
                question=question,
                answer=answer,
                question_vector=question_vector,
                category=category,
                confidence=confidence,
                keywords=keywords or [],
                source=source
            )
            
            # 添加到内存存储
            self.qa_pairs[qa_id] = qa_pair
            
            # 重建向量索引
            await self._rebuild_vector_index()
            
            # 更新统计
            self.stats["total_pairs"] = len(self.qa_pairs)
            
            logger.info(f"Added Q&A pair: {question[:50]}...")
            return qa_id
            
        except Exception as e:
            logger.error(f"Error adding Q&A pair: {e}")
            raise
    
    async def add_qa_pairs_batch(self, qa_data: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加问答对
        
        Args:
            qa_data: 问答对数据列表
            
        Returns:
            添加的问答对ID列表
        """
        try:
            added_ids = []
            questions = []
            qa_objects = []
            
            # 准备数据
            for qa_item in qa_data:
                question = qa_item.get("question", "").strip()
                answer = qa_item.get("answer", "").strip()
                
                if not question or not answer:
                    logger.warning("Skipping Q&A pair with empty question or answer")
                    continue
                
                qa_id = self._generate_id(question)
                
                # 检查是否已存在
                if qa_id in self.qa_pairs:
                    logger.warning(f"Q&A pair already exists: {question[:50]}...")
                    continue
                
                qa_pair = QAPair(
                    id=qa_id,
                    question=question,
                    answer=answer,
                    category=qa_item.get("category", "general"),
                    confidence=qa_item.get("confidence", 1.0),
                    keywords=qa_item.get("keywords", []),
                    source=qa_item.get("source", "batch_import")
                )
                
                questions.append(question)
                qa_objects.append(qa_pair)
                added_ids.append(qa_id)
            
            if not questions:
                logger.warning("No valid Q&A pairs to add")
                return []
            
            # 批量向量化
            logger.info(f"Vectorizing {len(questions)} questions...")
            question_embeddings = await self.embedding_func(questions)
            
            # 添加向量到Q&A对象并存储
            for i, qa_pair in enumerate(qa_objects):
                qa_pair.question_vector = np.array(question_embeddings[i])
                self.qa_pairs[qa_pair.id] = qa_pair
            
            # 重建向量索引
            await self._rebuild_vector_index()
            
            # 更新统计
            self.stats["total_pairs"] = len(self.qa_pairs)
            
            logger.info(f"Successfully added {len(added_ids)} Q&A pairs")
            return added_ids
            
        except Exception as e:
            logger.error(f"Error in batch adding Q&A pairs: {e}")
            raise
    
    async def _rebuild_vector_index(self):
        """重建向量索引以支持快速搜索"""
        try:
            if not self.qa_pairs:
                self.question_vectors = None
                self.vector_to_id = []
                return
            
            # 收集所有问题向量
            vectors = []
            ids = []
            
            for qa_id, qa_pair in self.qa_pairs.items():
                if qa_pair.question_vector is not None:
                    vectors.append(qa_pair.question_vector)
                    ids.append(qa_id)
            
            if vectors:
                self.question_vectors = np.array(vectors)
                self.vector_to_id = ids
                self.stats["vector_rebuilds"] += 1
                logger.debug(f"Rebuilt vector index with {len(vectors)} vectors")
            
        except Exception as e:
            logger.error(f"Error rebuilding vector index: {e}")
            raise

    async def search_similar_questions(self,
                                     query: str,
                                     top_k: int = None,
                                     min_similarity: float = None) -> List[SearchResult]:
        """
        搜索相似问题

        Args:
            query: 查询文本
            top_k: 返回结果数量
            min_similarity: 最小相似度阈值

        Returns:
            搜索结果列表
        """
        try:
            start_time = time.time()
            self.stats["total_queries"] += 1

            if not self.qa_pairs or self.question_vectors is None:
                return []

            # 使用默认值
            top_k = top_k or self.max_results
            min_similarity = min_similarity or self.similarity_threshold

            # 向量化查询
            query_embedding = await self.embedding_func([query])
            query_vector = np.array(query_embedding[0])

            # 计算相似度
            similarities = self._compute_similarities(query_vector, self.question_vectors)

            # 获取满足阈值的结果
            valid_indices = np.where(similarities >= min_similarity)[0]

            if len(valid_indices) == 0:
                return []

            # 排序并获取top_k
            sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]]
            top_indices = sorted_indices[:top_k]

            # 构建结果
            results = []
            for rank, idx in enumerate(top_indices):
                qa_id = self.vector_to_id[idx]
                qa_pair = self.qa_pairs[qa_id]
                similarity = similarities[idx]

                result = SearchResult(
                    qa_pair=qa_pair,
                    similarity=float(similarity),
                    rank=rank + 1
                )
                results.append(result)

            # 更新统计
            query_time = time.time() - start_time
            self.stats["total_query_time"] += query_time
            if results:
                self.stats["successful_queries"] += 1

            logger.debug(f"Found {len(results)} similar questions above threshold {min_similarity}")
            return results

        except Exception as e:
            logger.error(f"Error searching similar questions: {e}")
            return []

    def _compute_similarities(self, query_vector: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """计算余弦相似度"""
        # 归一化向量
        query_norm = np.linalg.norm(query_vector)
        vectors_norm = np.linalg.norm(vectors, axis=1)

        # 避免除零
        if query_norm == 0:
            return np.zeros(len(vectors))

        valid_indices = vectors_norm > 0
        similarities = np.zeros(len(vectors))

        if np.any(valid_indices):
            # 计算余弦相似度
            dot_products = np.dot(vectors[valid_indices], query_vector)
            similarities[valid_indices] = dot_products / (vectors_norm[valid_indices] * query_norm)

        return similarities

    async def get_best_match(self, query: str) -> Optional[SearchResult]:
        """
        获取最佳匹配

        Args:
            query: 查询文本

        Returns:
            最佳匹配结果或None
        """
        results = await self.search_similar_questions(query, top_k=1)
        return results[0] if results else None

    async def save_to_file(self, file_path: str = None) -> bool:
        """
        保存到文件

        Args:
            file_path: 文件路径（可选，默认使用初始化时的路径）

        Returns:
            True if successful, False otherwise
        """
        try:
            target_file = file_path or self.storage_file

            # 准备数据
            data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": time.time(),
                    "total_pairs": len(self.qa_pairs),
                    "similarity_threshold": self.similarity_threshold,
                    "embedding_dim": self.question_vectors.shape[1] if self.question_vectors is not None else 0
                },
                "qa_pairs": [qa_pair.to_dict() for qa_pair in self.qa_pairs.values()],
                "stats": self.stats
            }

            # 创建目录
            target_dir = os.path.dirname(target_file)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)

            # 保存文件
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.qa_pairs)} Q&A pairs to {target_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            return False

    async def load_from_file(self, file_path: str = None) -> bool:
        """
        从文件加载

        Args:
            file_path: 文件路径（可选，默认使用初始化时的路径）

        Returns:
            True if successful, False otherwise
        """
        try:
            source_file = file_path or self.storage_file

            if not os.path.exists(source_file):
                logger.warning(f"File not found: {source_file}")
                return False

            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载Q&A对
            qa_pairs_data = data.get("qa_pairs", [])
            self.qa_pairs = {}

            for qa_data in qa_pairs_data:
                qa_pair = QAPair.from_dict(qa_data)
                self.qa_pairs[qa_pair.id] = qa_pair

            # 加载统计信息
            if "stats" in data:
                self.stats.update(data["stats"])

            # 重建向量索引
            await self._rebuild_vector_index()

            logger.info(f"Loaded {len(self.qa_pairs)} Q&A pairs from {source_file}")
            return True

        except Exception as e:
            logger.error(f"Error loading from file: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        categories = {}
        confidence_sum = 0

        for qa_pair in self.qa_pairs.values():
            # 统计分类
            category = qa_pair.category
            categories[category] = categories.get(category, 0) + 1

            # 统计置信度
            confidence_sum += qa_pair.confidence

        avg_confidence = confidence_sum / len(self.qa_pairs) if self.qa_pairs else 0
        avg_query_time = self.stats["total_query_time"] / self.stats["total_queries"] if self.stats["total_queries"] > 0 else 0
        success_rate = (self.stats["successful_queries"] / self.stats["total_queries"] * 100) if self.stats["total_queries"] > 0 else 0

        return {
            "total_pairs": len(self.qa_pairs),
            "categories": categories,
            "average_confidence": round(avg_confidence, 3),
            "similarity_threshold": self.similarity_threshold,
            "vector_index_size": len(self.vector_to_id) if self.vector_to_id else 0,
            "embedding_dim": self.question_vectors.shape[1] if self.question_vectors is not None else 0,
            "query_stats": {
                **self.stats,
                "avg_query_time_ms": round(avg_query_time * 1000, 2),
                "success_rate_percent": round(success_rate, 2)
            }
        }

    async def cleanup(self):
        """清理资源"""
        # 保存数据
        await self.save_to_file()
        logger.info("VectorizedQAStorage cleanup completed")

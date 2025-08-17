"""
简化的Q&A管理器

专注于向量化存储和检索功能的高级接口
"""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional, Union
import logging

try:
    from .vectorized_qa_core import VectorizedQAStorage, QAPair, SearchResult
    from .embedding_client import EmbeddingClient, MockEmbeddingClient, create_embedding_client
except ImportError:
    from vectorized_qa_core import VectorizedQAStorage, QAPair, SearchResult
    from embedding_client import EmbeddingClient, MockEmbeddingClient, create_embedding_client

logger = logging.getLogger(__name__)


class QAManager:
    """
    简化的Q&A管理器
    
    提供向量化问答对存储和检索的高级接口：
    - 问题自动向量化存储
    - 答案文本格式保存
    - 智能语义搜索
    - 批量操作支持
    """
    
    def __init__(self, 
                 storage_file: str = "qa_storage.json",
                 embedding_client = None,
                 similarity_threshold: float = 0.85,
                 max_results: int = 10,
                 use_mock_embedding: bool = False):
        """
        初始化Q&A管理器
        
        Args:
            storage_file: 存储文件路径
            embedding_client: embedding客户端
            similarity_threshold: 相似度阈值
            max_results: 最大返回结果数
            use_mock_embedding: 是否使用模拟embedding
        """
        self.storage_file = storage_file
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        
        # 创建embedding客户端
        if embedding_client:
            self.embedding_client = embedding_client
        else:
            self.embedding_client = create_embedding_client(use_mock=use_mock_embedding)
        
        # 创建存储实例
        self.storage = VectorizedQAStorage(
            storage_file=storage_file,
            embedding_func=self.embedding_client,
            similarity_threshold=similarity_threshold,
            max_results=max_results
        )
        
        self.initialized = False
        
        # 查询统计
        self.query_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0
        }
        
        logger.info(f"QAManager initialized with storage: {storage_file}")
    
    async def initialize(self) -> bool:
        """
        初始化管理器
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # 测试embedding连接
            if hasattr(self.embedding_client, 'test_connection'):
                connection_ok = await self.embedding_client.test_connection()
                if not connection_ok:
                    logger.error("Embedding client connection test failed")
                    return False
            
            # 初始化存储
            success = await self.storage.initialize()
            if success:
                self.initialized = True
                logger.info("QAManager initialized successfully")
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize QAManager: {e}")
            return False
    
    async def add_qa_pair(self, 
                         question: str, 
                         answer: str,
                         category: str = "general",
                         confidence: float = 1.0,
                         keywords: List[str] = None,
                         source: str = "manual") -> Optional[str]:
        """
        添加问答对
        
        Args:
            question: 问题文本
            answer: 答案文本
            category: 分类
            confidence: 置信度
            keywords: 关键词列表
            source: 来源
            
        Returns:
            问答对ID或None（如果失败）
        """
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return None
        
        try:
            qa_id = await self.storage.add_qa_pair(
                question=question,
                answer=answer,
                category=category,
                confidence=confidence,
                keywords=keywords,
                source=source
            )
            
            logger.info(f"Added Q&A pair: {question[:50]}...")
            return qa_id
            
        except Exception as e:
            logger.error(f"Error adding Q&A pair: {e}")
            return None
    
    async def add_qa_pairs_batch(self, qa_data: List[Dict[str, Any]]) -> List[str]:
        """
        批量添加问答对
        
        Args:
            qa_data: 问答对数据列表
            
        Returns:
            添加的问答对ID列表
        """
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return []
        
        try:
            added_ids = await self.storage.add_qa_pairs_batch(qa_data)
            logger.info(f"Batch added {len(added_ids)} Q&A pairs")
            return added_ids
            
        except Exception as e:
            logger.error(f"Error in batch adding Q&A pairs: {e}")
            return []
    
    async def import_from_json(self, json_file: str) -> bool:
        """
        从JSON文件导入问答对
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return False
        
        try:
            if not os.path.exists(json_file):
                logger.error(f"JSON file not found: {json_file}")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as f:
                qa_data = json.load(f)
            
            if not isinstance(qa_data, list):
                logger.error("JSON file must contain a list of Q&A pairs")
                return False
            
            # 批量添加
            added_ids = await self.add_qa_pairs_batch(qa_data)
            
            logger.info(f"Imported {len(added_ids)} Q&A pairs from {json_file}")
            return len(added_ids) > 0
            
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return False
    
    async def query(self, question: str, top_k: int = 1) -> Dict[str, Any]:
        """
        查询问答对
        
        Args:
            question: 问题文本
            top_k: 返回结果数量
            
        Returns:
            查询结果字典
        """
        start_time = time.time()
        self.query_stats["total_queries"] += 1
        
        if not self.initialized:
            return {
                "success": False,
                "error": "QA Manager not initialized",
                "response_time": time.time() - start_time
            }
        
        try:
            # 搜索相似问题
            results = await self.storage.search_similar_questions(
                query=question,
                top_k=top_k,
                min_similarity=self.similarity_threshold
            )
            
            response_time = time.time() - start_time
            self._update_query_stats(response_time, len(results) > 0)
            
            if results:
                # 返回最佳匹配
                best_match = results[0]
                return {
                    "success": True,
                    "found": True,
                    "answer": best_match.qa_pair.answer,
                    "question": best_match.qa_pair.question,
                    "similarity": best_match.similarity,
                    "confidence": best_match.qa_pair.confidence,
                    "category": best_match.qa_pair.category,
                    "qa_id": best_match.qa_pair.id,
                    "response_time": response_time,
                    "all_results": [
                        {
                            "answer": r.qa_pair.answer,
                            "question": r.qa_pair.question,
                            "similarity": r.similarity,
                            "confidence": r.qa_pair.confidence,
                            "category": r.qa_pair.category,
                            "qa_id": r.qa_pair.id
                        } for r in results
                    ]
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "message": f"No Q&A match found above threshold {self.similarity_threshold}",
                    "response_time": response_time
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self.query_stats["failed_queries"] += 1
            logger.error(f"Error in Q&A query: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def _update_query_stats(self, response_time: float, is_successful: bool):
        """更新查询统计"""
        if is_successful:
            self.query_stats["successful_queries"] += 1
        
        self.query_stats["total_response_time"] += response_time
        self.query_stats["avg_response_time"] = (
            self.query_stats["total_response_time"] / self.query_stats["total_queries"]
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        if not self.initialized:
            return {"error": "QA Manager not initialized"}
        
        storage_stats = self.storage.get_statistics()
        embedding_stats = self.embedding_client.get_statistics()
        
        # 计算成功率
        success_rate = 0.0
        if self.query_stats["total_queries"] > 0:
            success_rate = (self.query_stats["successful_queries"] / self.query_stats["total_queries"]) * 100
        
        return {
            "storage_stats": storage_stats,
            "embedding_stats": embedding_stats,
            "query_performance": {
                **self.query_stats,
                "success_rate_percent": round(success_rate, 2),
                "avg_response_time_ms": round(self.query_stats["avg_response_time"] * 1000, 2)
            },
            "configuration": {
                "similarity_threshold": self.similarity_threshold,
                "max_results": self.max_results,
                "storage_file": self.storage_file
            }
        }
    
    def list_qa_pairs(self, 
                     category: str = None,
                     min_confidence: float = None) -> List[Dict[str, Any]]:
        """
        列出问答对
        
        Args:
            category: 过滤分类
            min_confidence: 最小置信度
            
        Returns:
            问答对列表
        """
        if not self.initialized:
            return []
        
        results = []
        
        for qa_pair in self.storage.qa_pairs.values():
            # 分类过滤
            if category and qa_pair.category != category:
                continue
            
            # 置信度过滤
            if min_confidence and qa_pair.confidence < min_confidence:
                continue
            
            results.append({
                "id": qa_pair.id,
                "question": qa_pair.question,
                "answer": qa_pair.answer,
                "category": qa_pair.category,
                "confidence": qa_pair.confidence,
                "keywords": qa_pair.keywords,
                "source": qa_pair.source,
                "created_at": qa_pair.created_at,
                "updated_at": qa_pair.updated_at
            })
        
        # 按置信度排序
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results
    
    async def save_storage(self) -> bool:
        """
        保存存储
        
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
        
        return await self.storage.save_to_file()
    
    async def cleanup(self):
        """清理资源"""
        if self.initialized:
            await self.storage.cleanup()
            logger.info("QAManager cleanup completed")

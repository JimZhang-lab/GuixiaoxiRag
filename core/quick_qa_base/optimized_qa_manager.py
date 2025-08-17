"""
优化的Q&A管理器 - 基于RAG架构

使用统一的embedding配置和向量存储
"""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional, Union
import logging

from .qa_vector_storage import QAVectorStorage, QAPair
from core.common.llm_client import create_embedding_function
from core.rag.utils import EmbeddingFunc

logger = logging.getLogger(__name__)


class OptimizedQAManager:
    """
    优化的Q&A管理器
    
    基于RAG架构提供向量化问答对存储和检索：
    - 使用统一的embedding配置
    - 高效的向量存储和检索
    - 支持0.98相似度阈值的精确匹配
    - 批量操作支持
    """
    
    def __init__(self, 
                 workspace: str = "qa_base",
                 namespace: str = "default",
                 similarity_threshold: float = 0.98,
                 max_results: int = 10,
                 working_dir: str = "./Q&A_Base"):
        """
        初始化Q&A管理器
        
        Args:
            workspace: 工作空间名称
            namespace: 命名空间
            similarity_threshold: 相似度阈值（默认0.98）
            max_results: 最大返回结果数
            working_dir: 工作目录
        """
        self.workspace = workspace
        self.namespace = namespace
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        self.working_dir = working_dir
        
        # 创建存储目录
        os.makedirs(working_dir, exist_ok=True)
        
        # 全局配置
        self.global_config = {
            "working_dir": working_dir,
            "embedding_batch_num": 10,
            "vector_db_storage_cls_kwargs": {
                "cosine_better_than_threshold": 1.0 - similarity_threshold
            }
        }
        
        self.embedding_func = None
        self.storage = None
        self.initialized = False
    
    async def initialize(self) -> bool:
        """初始化管理器"""
        try:
            # 创建embedding函数
            self.embedding_func = await create_embedding_function()
            if not self.embedding_func:
                logger.error("Failed to create embedding function")
                return False
            
            # 包装embedding函数以符合EmbeddingFunc接口
            class EmbeddingFuncWrapper:
                def __init__(self, func):
                    self.func = func
                    self.embedding_dim = 1024  # 默认维度，实际会根据模型调整
                
                async def __call__(self, texts, **kwargs):
                    return await self.func(texts)
            
            wrapped_embedding_func = EmbeddingFuncWrapper(self.embedding_func)
            
            # 测试embedding并获取实际维度
            try:
                test_embedding = await self.embedding_func(["test"])
                wrapped_embedding_func.embedding_dim = len(test_embedding[0])
                logger.info(f"Embedding dimension: {wrapped_embedding_func.embedding_dim}")
            except Exception as e:
                logger.warning(f"Could not determine embedding dimension: {e}")
            
            # 创建存储
            self.storage = QAVectorStorage(
                namespace=self.namespace,
                workspace=self.workspace,
                global_config=self.global_config,
                embedding_func=wrapped_embedding_func,
                similarity_threshold=self.similarity_threshold
            )
            
            # 初始化存储
            success = await self.storage.initialize()
            if success:
                self.initialized = True
                logger.info("QA Manager initialized successfully")
                return True
            else:
                logger.error("Failed to initialize QA storage")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing QA Manager: {e}")
            return False
    
    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> Optional[str]:
        """添加问答对"""
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return None
        
        try:
            qa_id = await self.storage.add_qa_pair(question, answer, **kwargs)
            if qa_id:
                # 保存数据
                await self.storage.index_done_callback()
                logger.info(f"Added QA pair: {qa_id}")
            return qa_id
        except Exception as e:
            logger.error(f"Error adding QA pair: {e}")
            return None
    
    async def add_qa_pairs_batch(self, qa_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加问答对"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}
        
        added_count = 0
        failed_count = 0
        added_ids = []
        
        try:
            for qa_data in qa_pairs:
                question = qa_data.get("question")
                answer = qa_data.get("answer")

                if not question or not answer:
                    failed_count += 1
                    continue

                # 创建一个不包含question和answer的kwargs字典
                kwargs = {k: v for k, v in qa_data.items() if k not in ['question', 'answer']}
                qa_id = await self.storage.add_qa_pair(question, answer, **kwargs)
                if qa_id:
                    added_count += 1
                    added_ids.append(qa_id)
                else:
                    failed_count += 1
            
            # 保存数据
            await self.storage.index_done_callback()
            
            return {
                "success": True,
                "added_count": added_count,
                "failed_count": failed_count,
                "added_ids": added_ids
            }
            
        except Exception as e:
            logger.error(f"Error in batch add: {e}")
            return {"success": False, "error": str(e)}
    
    async def query(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """查询问答"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}
        
        if top_k is None:
            top_k = self.max_results
        
        try:
            start_time = time.time()
            result = await self.storage.query_qa(question, top_k)
            response_time = time.time() - start_time
            
            if result.get("success"):
                result["response_time"] = response_time
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying QA: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_batch(self, questions: List[str], top_k: Optional[int] = None, parallel: bool = True, timeout: int = 300) -> Dict[str, Any]:
        """批量查询"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}
        
        if top_k is None:
            top_k = self.max_results
        
        try:
            start_time = time.time()
            
            if parallel:
                # 并行查询
                tasks = [self.query(question, top_k) for question in questions]
                results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
            else:
                # 串行查询
                results = []
                for question in questions:
                    result = await self.query(question, top_k)
                    results.append(result)
            
            total_time = time.time() - start_time
            successful_queries = sum(1 for r in results if r.get("success", False))
            
            return {
                "success": True,
                "total_queries": len(questions),
                "successful_queries": successful_queries,
                "failed_queries": len(questions) - successful_queries,
                "total_time": total_time,
                "results": results
            }
            
        except asyncio.TimeoutError:
            return {"success": False, "error": "Batch query timeout"}
        except Exception as e:
            logger.error(f"Error in batch query: {e}")
            return {"success": False, "error": str(e)}
    
    def list_qa_pairs(self, category: str = None, min_confidence: float = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """列出问答对"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}
        
        try:
            all_pairs = self.storage.list_qa_pairs(category, min_confidence)
            
            # 分页
            total = len(all_pairs)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_pairs = all_pairs[start_idx:end_idx]
            
            return {
                "success": True,
                "data": {
                    "qa_pairs": page_pairs,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing QA pairs: {e}")
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}
        
        try:
            stats = self.storage.get_statistics()
            return {"success": True, "data": stats}
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self.initialized:
                return {
                    "success": False,
                    "status": "not_initialized",
                    "message": "QA Manager not initialized"
                }
            
            # 测试embedding
            embedding_status = "ready"
            try:
                await self.embedding_func(["test"])
            except Exception as e:
                embedding_status = f"error: {str(e)}"
            
            # 获取统计信息
            stats = self.storage.get_statistics()
            
            return {
                "success": True,
                "status": "healthy",
                "qa_storage_status": "ready",
                "embedding_status": embedding_status,
                "total_qa_pairs": stats["storage_stats"]["total_pairs"],
                "avg_response_time": 0.0,  # 可以添加实际统计
                "error_rate": 0.0
            }
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "success": False,
                "status": "error",
                "message": str(e)
            }
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.storage:
                await self.storage.index_done_callback()
            logger.info("QA Manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

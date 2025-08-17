"""
基于RAG架构的问答向量存储
"""

import asyncio
import json
import os
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
import logging

from core.rag.base import BaseVectorStorage
from nano_vectordb import NanoVectorDB

logger = logging.getLogger(__name__)


@dataclass
class QAPair:
    """问答对数据结构"""
    id: str
    question: str
    answer: str
    category: str = "general"
    confidence: float = 1.0
    keywords: List[str] = field(default_factory=list)
    source: str = "manual"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class QAVectorStorage(BaseVectorStorage):
    """基于RAG架构的问答向量存储"""

    def __init__(self, namespace: str, workspace: str, global_config: dict, embedding_func, similarity_threshold: float = 0.98):
        # 初始化父类字段
        self.namespace = namespace
        self.workspace = workspace
        self.global_config = global_config
        self.embedding_func = embedding_func
        self.cosine_better_than_threshold = 1.0 - similarity_threshold  # NanoVectorDB使用距离阈值
        self.meta_fields = {"qa_id", "question", "answer", "category", "confidence", "source"}  # 设置元数据字段
        self.similarity_threshold = similarity_threshold
        self.qa_pairs: Dict[str, QAPair] = {}
        self._client = None
        self._client_file_name = None
        self._max_batch_size = global_config.get("embedding_batch_num", 10)
        
        # 设置存储文件路径
        working_dir = global_config["working_dir"]
        if workspace:
            workspace_dir = os.path.join(working_dir, workspace)
            os.makedirs(workspace_dir, exist_ok=True)
            self._client_file_name = os.path.join(workspace_dir, f"qa_vdb_{namespace}.json")
            self.qa_storage_file = os.path.join(workspace_dir, f"qa_pairs_{namespace}.json")
        else:
            self._client_file_name = os.path.join(working_dir, f"qa_vdb_{namespace}.json")
            self.qa_storage_file = os.path.join(working_dir, f"qa_pairs_{namespace}.json")
        
        # 创建存储目录
        os.makedirs(os.path.dirname(self._client_file_name), exist_ok=True)
    
    async def initialize(self):
        """初始化存储"""
        try:
            # 初始化向量数据库
            self._client = NanoVectorDB(
                self.embedding_func.embedding_dim,
                storage_file=self._client_file_name,
            )
            
            # 加载问答对数据
            await self._load_qa_pairs()
            
            logger.info(f"QA vector storage initialized with {len(self.qa_pairs)} pairs")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize QA vector storage: {e}")
            return False
    
    async def _load_qa_pairs(self):
        """加载问答对数据"""
        if os.path.exists(self.qa_storage_file):
            try:
                with open(self.qa_storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for qa_data in data.get('qa_pairs', []):
                    qa_pair = QAPair(**qa_data)
                    self.qa_pairs[qa_pair.id] = qa_pair
                
                logger.info(f"Loaded {len(self.qa_pairs)} QA pairs from storage")
            except Exception as e:
                logger.error(f"Error loading QA pairs: {e}")
                self.qa_pairs = {}
    
    async def save_qa_pairs(self) -> bool:
        """保存问答对数据"""
        try:
            qa_data = []
            for qa_pair in self.qa_pairs.values():
                qa_dict = {
                    'id': qa_pair.id,
                    'question': qa_pair.question,
                    'answer': qa_pair.answer,
                    'category': qa_pair.category,
                    'confidence': qa_pair.confidence,
                    'keywords': qa_pair.keywords,
                    'source': qa_pair.source,
                    'created_at': qa_pair.created_at,
                    'updated_at': qa_pair.updated_at
                }
                qa_data.append(qa_dict)
            
            save_data = {
                'metadata': {
                    'version': '1.0',
                    'created_at': time.time(),
                    'total_pairs': len(qa_data)
                },
                'qa_pairs': qa_data
            }
            
            # 原子性写入
            temp_file = self.qa_storage_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_file, self.qa_storage_file)
            logger.info(f"Saved {len(qa_data)} QA pairs to storage")
            return True
            
        except Exception as e:
            logger.error(f"Error saving QA pairs: {e}")
            return False
    
    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> str:
        """添加问答对"""
        qa_id = kwargs.get('id', f"qa_{uuid.uuid4().hex[:8]}")
        
        # 创建问答对
        qa_pair = QAPair(
            id=qa_id,
            question=question,
            answer=answer,
            category=kwargs.get('category', 'general'),
            confidence=kwargs.get('confidence', 1.0),
            keywords=kwargs.get('keywords', []),
            source=kwargs.get('source', 'manual'),
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 添加到向量数据库
        vector_data = {
            qa_id: {
                "content": question,  # 使用问题作为向量化内容
                "qa_id": qa_id,
                "question": question,
                "answer": answer,
                "category": qa_pair.category,
                "confidence": qa_pair.confidence,
                "source": qa_pair.source
            }
        }
        
        try:
            await self.upsert(vector_data)
            self.qa_pairs[qa_id] = qa_pair
            return qa_id
        except Exception as e:
            logger.error(f"Error adding QA pair: {e}")
            return None
    
    async def query_qa(self, question: str, top_k: int = 1) -> Dict[str, Any]:
        """查询问答"""
        if not self.qa_pairs:
            return {
                "success": True,
                "found": False,
                "message": "No QA pairs available"
            }
        
        try:
            # 使用向量查询
            results = await self.query(question, top_k)
            
            if not results:
                return {
                    "success": True,
                    "found": False,
                    "message": "No matching QA pairs found"
                }
            
            # 检查最佳匹配的相似度
            best_result = results[0]
            similarity = 1.0 - best_result.get("distance", 1.0)  # 转换距离为相似度
            
            if similarity >= self.similarity_threshold:
                qa_id = best_result.get("qa_id")
                qa_pair = self.qa_pairs.get(qa_id)
                
                if qa_pair:
                    # 构建所有结果
                    all_results = []
                    for result in results:
                        result_qa_id = result.get("qa_id")
                        result_qa_pair = self.qa_pairs.get(result_qa_id)
                        if result_qa_pair:
                            result_similarity = 1.0 - result.get("distance", 1.0)
                            all_results.append({
                                "qa_id": result_qa_id,
                                "question": result_qa_pair.question,
                                "answer": result_qa_pair.answer,
                                "category": result_qa_pair.category,
                                "confidence": result_qa_pair.confidence,
                                "similarity": float(result_similarity)
                            })
                    
                    return {
                        "success": True,
                        "found": True,
                        "qa_id": qa_id,
                        "question": qa_pair.question,
                        "answer": qa_pair.answer,
                        "category": qa_pair.category,
                        "confidence": qa_pair.confidence,
                        "similarity": float(similarity),
                        "all_results": all_results
                    }
            
            return {
                "success": True,
                "found": False,
                "message": f"No QA pair found with similarity >= {self.similarity_threshold}",
                "best_similarity": float(similarity)
            }
                
        except Exception as e:
            logger.error(f"Error querying QA: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_qa_pairs(self, category: str = None, min_confidence: float = None) -> List[Dict[str, Any]]:
        """列出问答对"""
        results = []
        for qa_pair in self.qa_pairs.values():
            # 应用过滤条件
            if category and qa_pair.category != category:
                continue
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
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        categories = {}
        total_confidence = 0
        
        for qa_pair in self.qa_pairs.values():
            categories[qa_pair.category] = categories.get(qa_pair.category, 0) + 1
            total_confidence += qa_pair.confidence
        
        avg_confidence = total_confidence / len(self.qa_pairs) if self.qa_pairs else 0
        
        return {
            "storage_stats": {
                "total_pairs": len(self.qa_pairs),
                "categories": categories,
                "average_confidence": avg_confidence,
                "similarity_threshold": self.similarity_threshold,
                "vector_index_size": len(self.qa_pairs),
                "embedding_dim": getattr(self.embedding_func, 'embedding_dim', 0),
                "query_stats": {
                    "total_queries": 0,  # 可以添加查询统计
                    "successful_queries": 0,
                    "avg_response_time": 0.0
                }
            }
        }

    # 实现BaseVectorStorage的抽象方法
    async def query(self, query: str, top_k: int, ids: list[str] | None = None) -> list[dict[str, Any]]:
        """查询向量存储"""
        if not self._client:
            return []

        # 生成查询向量
        embedding = await self.embedding_func([query])
        query_vector = embedding[0]

        # 执行查询
        results = self._client.query(
            query=query_vector,
            top_k=top_k,
            better_than_threshold=self.cosine_better_than_threshold,
        )

        # 转换结果格式
        formatted_results = []
        for result in results:
            formatted_results.append({
                **result,
                "id": result.get("__id__"),
                "distance": result.get("__metrics__"),
                "created_at": result.get("__created_at__"),
            })

        return formatted_results

    async def upsert(self, data: dict[str, dict[str, Any]]) -> None:
        """插入或更新向量"""
        if not data:
            return

        current_time = int(time.time())
        list_data = [
            {
                "__id__": k,
                "__created_at__": current_time,
                **{k1: v1 for k1, v1 in v.items() if k1 in self.meta_fields or k1 in ["qa_id", "question", "answer", "category", "confidence", "source"]},
            }
            for k, v in data.items()
        ]

        contents = [v["content"] for v in data.values()]
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]

        # 执行embedding
        embedding_tasks = [self.embedding_func(batch) for batch in batches]
        embeddings_list = await asyncio.gather(*embedding_tasks)

        embeddings = np.concatenate(embeddings_list)
        if len(embeddings) == len(list_data):
            for i, d in enumerate(list_data):
                d["__vector__"] = embeddings[i]

            results = self._client.upsert(datas=list_data)
            return results
        else:
            logger.error(f"Embedding count mismatch: {len(embeddings)} != {len(list_data)}")

    async def delete_entity(self, entity_name: str) -> None:
        """删除实体（QA系统中不适用）"""
        pass

    async def delete_entity_relation(self, entity_name: str) -> None:
        """删除实体关系（QA系统中不适用）"""
        pass

    async def get_by_id(self, id: str) -> dict[str, Any] | None:
        """根据ID获取向量数据"""
        if not self._client:
            return None

        result = self._client.get([id])
        if result:
            dp = result[0]
            return {
                **dp,
                "id": dp.get("__id__"),
                "created_at": dp.get("__created_at__"),
            }
        return None

    async def get_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        """根据ID列表获取向量数据"""
        if not ids or not self._client:
            return []

        results = self._client.get(ids)
        return [
            {
                **dp,
                "id": dp.get("__id__"),
                "created_at": dp.get("__created_at__"),
            }
            for dp in results
        ]

    async def delete(self, ids: list[str]):
        """删除向量数据"""
        if not ids or not self._client:
            return

        try:
            self._client.delete(ids)
            # 同时删除问答对数据
            for qa_id in ids:
                if qa_id in self.qa_pairs:
                    del self.qa_pairs[qa_id]

            logger.debug(f"Deleted {len(ids)} QA pairs")
        except Exception as e:
            logger.error(f"Error deleting QA pairs: {e}")

    async def index_done_callback(self) -> None:
        """索引完成回调"""
        try:
            # 保存向量数据库
            if self._client:
                self._client.save()

            # 保存问答对数据
            await self.save_qa_pairs()

            logger.debug("QA storage index done callback completed")
        except Exception as e:
            logger.error(f"Error in index done callback: {e}")

    async def drop(self) -> dict[str, str]:
        """清空所有数据"""
        try:
            # 清空问答对数据
            self.qa_pairs.clear()

            # 删除存储文件
            if os.path.exists(self._client_file_name):
                os.remove(self._client_file_name)
            if os.path.exists(self.qa_storage_file):
                os.remove(self.qa_storage_file)

            # 重新初始化向量数据库
            self._client = NanoVectorDB(
                self.embedding_func.embedding_dim,
                storage_file=self._client_file_name,
            )

            logger.info("QA storage dropped successfully")
            return {"status": "success", "message": "data dropped"}
        except Exception as e:
            logger.error(f"Error dropping QA storage: {e}")
            return {"status": "error", "message": str(e)}

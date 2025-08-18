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
        # NanoVectorDB使用距离阈值：距离 = 1 - 相似度
        # 相似度阈值0.98对应距离阈值0.02
        self.cosine_better_than_threshold = 1.0 - similarity_threshold
        self.meta_fields = {"qa_id", "question", "answer", "category", "confidence", "source", "content"}  # 设置元数据字段，包含content
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
    
    async def check_duplicate_question(self, question: str, similarity_threshold: float = 0.98) -> dict:
        """检查是否存在相似的问题

        Args:
            question: 要检查的问题
            similarity_threshold: 相似度阈值，默认0.98

        Returns:
            dict: 包含检查结果的字典
                - is_duplicate: bool, 是否存在重复
                - similar_qa: dict, 最相似的问答对信息（如果存在）
                - similarity: float, 最高相似度
        """
        try:
            # 如果没有数据，直接返回不重复
            if not self.qa_pairs:
                return {
                    "is_duplicate": False,
                    "similar_qa": None,
                    "similarity": 0.0
                }

            # 查询最相似的问题
            results = await self.query(question, top_k=1, better_than_threshold=None)

            if not results:
                return {
                    "is_duplicate": False,
                    "similar_qa": None,
                    "similarity": 0.0
                }

            # 获取最相似的结果
            best_result = results[0]
            distance = best_result.get("distance", 1.0)
            similarity = 1.0 - distance  # 转换距离为相似度

            # 检查是否超过阈值
            is_duplicate = similarity >= similarity_threshold

            similar_qa = None
            if is_duplicate:
                qa_id = best_result.get("qa_id")
                qa_pair = self.qa_pairs.get(qa_id)
                if qa_pair:
                    similar_qa = {
                        "qa_id": qa_id,
                        "question": qa_pair.question,
                        "answer": qa_pair.answer,
                        "category": qa_pair.category,
                        "confidence": qa_pair.confidence,
                        "source": qa_pair.source
                    }

            return {
                "is_duplicate": is_duplicate,
                "similar_qa": similar_qa,
                "similarity": float(similarity)
            }

        except Exception as e:
            logger.error(f"Error checking duplicate question: {e}")
            return {
                "is_duplicate": False,
                "similar_qa": None,
                "similarity": 0.0
            }

    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> str:
        """添加问答对（带重复检查）"""
        # 检查是否允许跳过重复检查
        skip_duplicate_check = kwargs.get('skip_duplicate_check', False)
        duplicate_threshold = kwargs.get('duplicate_threshold', 0.98)

        # 执行重复检查
        if not skip_duplicate_check:
            duplicate_check = await self.check_duplicate_question(question, duplicate_threshold)

            if duplicate_check["is_duplicate"]:
                similar_qa = duplicate_check["similar_qa"]
                similarity = duplicate_check["similarity"]

                logger.warning(f"Duplicate question detected: similarity={similarity:.4f}, "
                             f"existing_qa_id={similar_qa['qa_id']}")

                # 返回特殊的错误标识
                return f"DUPLICATE:{similar_qa['qa_id']}:{similarity:.4f}"

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
            logger.info(f"Added QA pair: {qa_id}, question: '{question[:50]}...'")
            return qa_id
        except Exception as e:
            logger.error(f"Error adding QA pair: {e}")
            return None

    async def add_qa_pairs_batch(self, qa_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加问答对（带重复检查）"""
        added_ids = []
        skipped_duplicates = []
        failed_items = []

        try:
            # 获取批量设置
            skip_duplicate_check = qa_data_list[0].get('skip_duplicate_check', False) if qa_data_list else False
            duplicate_threshold = qa_data_list[0].get('duplicate_threshold', 0.98) if qa_data_list else 0.98

            # 准备批量向量数据
            vector_data = {}

            for qa_data in qa_data_list:
                question = qa_data.get("question")
                answer = qa_data.get("answer")

                if not question or not answer:
                    failed_items.append({
                        "data": qa_data,
                        "reason": "Missing question or answer"
                    })
                    continue

                qa_id = qa_data.get('id', f"qa_{uuid.uuid4().hex[:8]}")

                # 执行重复检查
                if not skip_duplicate_check:
                    duplicate_check = await self.check_duplicate_question(question, duplicate_threshold)

                    if duplicate_check["is_duplicate"]:
                        similar_qa = duplicate_check["similar_qa"]
                        similarity = duplicate_check["similarity"]

                        logger.info(f"Skipping duplicate question: '{question[:50]}...', "
                                  f"similarity={similarity:.4f}, existing_qa_id={similar_qa['qa_id']}")

                        skipped_duplicates.append({
                            "question": question,
                            "similarity": similarity,
                            "existing_qa_id": similar_qa['qa_id'],
                            "existing_question": similar_qa['question']
                        })
                        continue

                # 创建问答对
                qa_pair = QAPair(
                    id=qa_id,
                    question=question,
                    answer=answer,
                    category=qa_data.get('category', 'general'),
                    confidence=qa_data.get('confidence', 1.0),
                    keywords=qa_data.get('keywords', []),
                    source=qa_data.get('source', 'manual'),
                    created_at=time.time(),
                    updated_at=time.time()
                )

                # 添加到向量数据 - 确保使用问题进行向量化
                vector_data[qa_id] = {
                    "content": question,  # 明确：使用问题作为向量化内容，不是答案！
                    "qa_id": qa_id,
                    "question": question,
                    "answer": answer,
                    "category": qa_pair.category,
                    "confidence": qa_pair.confidence,
                    "source": qa_pair.source
                }

                # 调试日志：确认向量化内容
                logger.debug(f"Vectorizing QA {qa_id}: question='{question[:50]}...', content='{question[:50]}...'")
                if question != vector_data[qa_id]["content"]:
                    logger.error(f"CRITICAL: Content mismatch for QA {qa_id}!")

                # 添加到内存
                self.qa_pairs[qa_id] = qa_pair
                added_ids.append(qa_id)

            # 批量插入向量数据库
            if vector_data:
                await self.upsert(vector_data)
                logger.info(f"Batch added {len(added_ids)} QA pairs, skipped {len(skipped_duplicates)} duplicates")

            return {
                "added_ids": added_ids,
                "added_count": len(added_ids),
                "skipped_duplicates": skipped_duplicates,
                "skipped_count": len(skipped_duplicates),
                "failed_items": failed_items,
                "failed_count": len(failed_items)
            }

        except Exception as e:
            logger.error(f"Error in batch add QA pairs: {e}")
            return {
                "added_ids": added_ids,
                "added_count": len(added_ids),
                "skipped_duplicates": skipped_duplicates,
                "skipped_count": len(skipped_duplicates),
                "failed_items": failed_items,
                "failed_count": len(failed_items),
                "error": str(e)
            }

    async def query_qa(self, question: str, top_k: int = 1, min_similarity: Optional[float] = None, category: Optional[str] = None, better_than_threshold: Optional[float] = None) -> Dict[str, Any]:
        """查询问答
        - min_similarity: 覆盖默认相似度阈值（按次查询）
        - category: 仅在该分类内检索匹配
        """
        if not self.qa_pairs:
            return {
                "success": True,
                "found": False,
                "message": "No QA pairs available"
            }

        try:
            # 使用向量查询
            results = await self.query(question, top_k, better_than_threshold=better_than_threshold)

            # 可选：按分类过滤
            if category:
                filtered = []
                for r in results:
                    qid = r.get("qa_id")
                    qp = self.qa_pairs.get(qid)
                    if qp and qp.category == category:
                        filtered.append(r)
                results = filtered

            if not results:
                return {
                    "success": True,
                    "found": False,
                    "message": "No matching QA pairs found" + (f" in category '{category}'" if category else "")
                }

            # 动态相似度阈值
            similarity_threshold = self.similarity_threshold if min_similarity is None else float(min_similarity)

            # 检查最佳匹配的相似度（现在query方法已经返回正确的相似度）
            best_result = results[0]
            raw_similarity = best_result.get("similarity", 0.0)  # 直接使用相似度
            # 修复浮点数精度问题：确保相似度在[0.0, 1.0]范围内
            similarity = max(0.0, min(1.0, float(raw_similarity)))

            if similarity >= similarity_threshold:
                qa_id = best_result.get("qa_id")
                qa_pair = self.qa_pairs.get(qa_id)

                if qa_pair:
                    # 构建所有结果（保持与阈值无关的完整结果，但已应用分类过滤）
                    all_results = []
                    for result in results:
                        result_qa_id = result.get("qa_id")
                        result_qa_pair = self.qa_pairs.get(result_qa_id)
                        if result_qa_pair:
                            raw_similarity = result.get("similarity", 0.0)  # 直接使用相似度
                            # 修复浮点数精度问题：确保相似度在[0.0, 1.0]范围内
                            result_similarity = max(0.0, min(1.0, float(raw_similarity)))
                            all_results.append({
                                "qa_id": result_qa_id,
                                "question": result_qa_pair.question,
                                "answer": result_qa_pair.answer,
                                "category": result_qa_pair.category,
                                "confidence": result_qa_pair.confidence,
                                "similarity": result_similarity
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
                else:
                    # qa_pair不存在，可能是数据不一致
                    logger.warning(f"QA pair {qa_id} not found in storage but exists in vector DB")
                    return {
                        "success": True,
                        "found": False,
                        "message": f"QA pair data inconsistency for ID: {qa_id}"
                    }

            return {
                "success": True,
                "found": False,
                "message": f"No QA pair found with similarity >= {similarity_threshold}",
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
    async def query(self, query: str, top_k: int, ids: list[str] | None = None, better_than_threshold: Optional[float] = None) -> list[dict[str, Any]]:
        """查询向量存储"""
        if not self._client:
            return []

        # 生成查询向量
        embedding = await self.embedding_func([query])
        query_vector = embedding[0]

        # 动态阈值（用于按次查询）
        # better_than_threshold应该是距离阈值，如果传入的是相似度阈值，需要转换
        if better_than_threshold is None:
            dyn_threshold = self.cosine_better_than_threshold
        else:
            # 如果better_than_threshold > 1，说明传入的可能是错误值，使用默认值
            if better_than_threshold > 1.0:
                logger.warning(f"Invalid better_than_threshold: {better_than_threshold}, using default")
                dyn_threshold = self.cosine_better_than_threshold
            else:
                # 假设传入的是距离阈值
                dyn_threshold = better_than_threshold

        # 执行查询
        results = self._client.query(
            query=query_vector,
            top_k=top_k,
            better_than_threshold=dyn_threshold,
        )

        # 转换结果格式，确保字段名一致（修复NanoVectorDB字段含义）
        formatted_results = []
        for result in results:
            # 重要修复：NanoVectorDB的__metrics__字段存储的是相似度，不是距离！
            raw_similarity = result.get("__metrics__", 0.0)  # NanoVectorDB返回的相似度值

            # 修复浮点数精度问题：确保相似度在[0.0, 1.0]范围内
            similarity = max(0.0, min(1.0, float(raw_similarity)))
            distance = 1.0 - similarity  # 距离 = 1 - 相似度
            qa_id = result.get("__id__")

            formatted_results.append({
                **result,
                "id": qa_id,
                "qa_id": qa_id,  # 确保qa_id字段存在
                "distance": distance,
                "similarity": similarity,  # 使用截断后的相似度
                "created_at": result.get("__created_at__"),
            })

        logger.debug(f"Query returned {len(formatted_results)} results")
        return formatted_results

    async def upsert(self, data: dict[str, dict[str, Any]]) -> None:
        """插入或更新向量（参考RAG系统实现）"""
        if not data:
            return

        logger.debug(f"Inserting {len(data)} vectors to QA storage")

        current_time = int(time.time())
        list_data = [
            {
                "__id__": k,
                "__created_at__": current_time,
                **{k1: v1 for k1, v1 in v.items() if k1 in self.meta_fields},
            }
            for k, v in data.items()
        ]

        contents = [v["content"] for v in data.values()]
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]

        # 执行embedding（在锁外执行以避免长时间锁定）
        embedding_tasks = [self.embedding_func(batch) for batch in batches]
        embeddings_list = await asyncio.gather(*embedding_tasks)

        # 使用numpy.concatenate来正确合并embeddings（参考RAG实现）
        embeddings = np.concatenate(embeddings_list)

        if len(embeddings) == len(list_data):
            for i, d in enumerate(list_data):
                # 直接使用embedding，不需要转换为numpy数组
                d["__vector__"] = embeddings[i]

            # 添加调试信息
            logger.debug(f"About to upsert {len(list_data)} items")
            logger.debug(f"First item keys: {list(list_data[0].keys()) if list_data else 'No data'}")
            logger.debug(f"First item has __vector__: {'__vector__' in list_data[0] if list_data else 'No data'}")
            
            results = self._client.upsert(datas=list_data)

            # 立即保存向量数据到文件（与RAG系统不同，我们需要立即保存）
            try:
                self._client.save()
                logger.debug(f"Vector data saved to {self._client_file_name}")
            except Exception as e:
                logger.error(f"Failed to save vector data: {e}")

            logger.info(f"Successfully upserted {len(list_data)} vectors")
            return results
        else:
            # 参考RAG系统的错误处理
            logger.error(f"Embedding count mismatch: {len(embeddings)} != {len(list_data)}")
            logger.error(f"Embeddings list structure: {[len(batch) for batch in embeddings_list]}")
            return None

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

"""
基于分类的问答存储管理器
按照category将问答对分别存储到不同的文件夹中
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
from .qa_vector_storage import QAPair

logger = logging.getLogger(__name__)


class CategoryQAStorage:
    """基于分类的问答存储管理器"""
    
    def __init__(self, namespace: str, workspace: str, global_config: dict, embedding_func, similarity_threshold: float = 0.98):
        self.namespace = namespace
        self.workspace = workspace
        self.global_config = global_config
        self.embedding_func = embedding_func
        self.similarity_threshold = similarity_threshold
        
        # 设置基础存储路径
        working_dir = global_config["working_dir"]
        # 如果working_dir已经以Q_A_Base结尾，直接使用，否则添加Q_A_Base
        if working_dir.endswith("Q_A_Base"):
            self.base_storage_path = working_dir
        else:
            self.base_storage_path = os.path.join(working_dir, "Q_A_Base")
        os.makedirs(self.base_storage_path, exist_ok=True)
        
        # 分类存储管理
        self.category_storages: Dict[str, 'QAVectorStorage'] = {}
        self.qa_pairs: Dict[str, QAPair] = {}  # 全局问答对索引
        self.initialized = False
    
    async def initialize(self) -> bool:
        """初始化存储"""
        try:
            # 扫描现有的分类文件夹
            await self._scan_existing_categories()
            self.initialized = True
            logger.info(f"Category QA Storage initialized with {len(self.category_storages)} categories")
            return True
        except Exception as e:
            logger.error(f"Error initializing Category QA Storage: {e}")
            return False
    
    async def _scan_existing_categories(self):
        """扫描现有的分类文件夹"""
        if not os.path.exists(self.base_storage_path):
            return
        
        for item in os.listdir(self.base_storage_path):
            category_path = os.path.join(self.base_storage_path, item)
            if os.path.isdir(category_path):
                # 检查是否有问答对文件
                qa_file = os.path.join(category_path, f"qa_pairs_{self.namespace}.json")
                if os.path.exists(qa_file):
                    await self._load_category_storage(item)
    
    async def _load_category_storage(self, category: str):
        """加载特定分类的存储"""
        try:
            from .qa_vector_storage import QAVectorStorage

            # 创建分类专用的配置，working_dir指向分类文件夹
            category_config = self.global_config.copy()
            category_config["working_dir"] = os.path.join(self.base_storage_path, category)

            # 创建分类专用的存储
            storage = QAVectorStorage(
                namespace=self.namespace,
                workspace="",  # 空字符串，因为working_dir已经指向分类文件夹
                global_config=category_config,
                embedding_func=self.embedding_func,
                similarity_threshold=self.similarity_threshold
            )
            
            # 初始化存储
            success = await storage.initialize()
            if success:
                self.category_storages[category] = storage
                # 将问答对添加到全局索引
                for qa_id, qa_pair in storage.qa_pairs.items():
                    self.qa_pairs[qa_id] = qa_pair
                logger.info(f"Loaded category '{category}' with {len(storage.qa_pairs)} QA pairs")
            else:
                logger.error(f"Failed to initialize storage for category '{category}'")
                
        except Exception as e:
            logger.error(f"Error loading category storage '{category}': {e}")
    
    async def _get_or_create_category_storage(self, category: str):
        """获取或创建分类存储"""
        if category not in self.category_storages:
            await self._load_category_storage(category)
        return self.category_storages.get(category)
    
    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> Optional[str]:
        """添加问答对到指定分类"""
        category = kwargs.get('category', 'general')
        
        try:
            # 获取或创建分类存储
            storage = await self._get_or_create_category_storage(category)
            if not storage:
                logger.error(f"Failed to get storage for category '{category}'")
                return None
            
            # 添加问答对
            qa_id = await storage.add_qa_pair(question, answer, **kwargs)
            if qa_id:
                # 添加到全局索引
                qa_pair = storage.qa_pairs.get(qa_id)
                if qa_pair:
                    self.qa_pairs[qa_id] = qa_pair
                
                # 保存数据
                await storage.index_done_callback()
                logger.info(f"Added QA pair {qa_id} to category '{category}'")
            
            return qa_id
            
        except Exception as e:
            logger.error(f"Error adding QA pair to category '{category}': {e}")
            return None
    
    async def add_qa_pairs_batch(self, qa_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加问答对"""
        added_ids = []
        skipped_duplicates = []
        failed_items = []

        # 按分类分组
        category_groups = {}
        for qa_item in qa_data:
            category = qa_item.get('category', 'general')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(qa_item)

        # 为每个分类批量添加
        for category, items in category_groups.items():
            try:
                storage = await self._get_or_create_category_storage(category)
                if storage:
                    # 调用存储的批量添加方法（现在返回字典）
                    result = await storage.add_qa_pairs_batch(items)

                    # 处理结果
                    if isinstance(result, dict):
                        # 新的返回格式
                        batch_ids = result.get("added_ids", [])
                        added_ids.extend(batch_ids)
                        skipped_duplicates.extend(result.get("skipped_duplicates", []))
                        failed_items.extend(result.get("failed_items", []))
                    else:
                        # 旧的返回格式（向后兼容）
                        batch_ids = result if isinstance(result, list) else []
                        added_ids.extend(batch_ids)

                    # 更新全局索引
                    for qa_id in batch_ids:
                        qa_pair = storage.qa_pairs.get(qa_id)
                        if qa_pair:
                            self.qa_pairs[qa_id] = qa_pair

                    # 保存数据
                    await storage.index_done_callback()
                    logger.info(f"Added {len(batch_ids)} QA pairs to category '{category}'")

            except Exception as e:
                logger.error(f"Error batch adding QA pairs to category '{category}': {e}")
                failed_items.append({
                    "category": category,
                    "error": str(e)
                })

        return {
            "added_ids": added_ids,
            "added_count": len(added_ids),
            "skipped_duplicates": skipped_duplicates,
            "skipped_count": len(skipped_duplicates),
            "failed_items": failed_items,
            "failed_count": len(failed_items)
        }
    
    async def query_qa(self, question: str, top_k: int = 1, min_similarity: Optional[float] = None, category: Optional[str] = None, better_than_threshold: Optional[float] = None) -> Dict[str, Any]:
        """查询问答"""
        if not self.qa_pairs:
            return {
                "success": True,
                "found": False,
                "message": "No QA pairs available"
            }
        
        try:
            if category:
                # 在指定分类中查询
                storage = self.category_storages.get(category)
                if not storage:
                    return {
                        "success": True,
                        "found": False,
                        "message": f"Category '{category}' not found"
                    }
                return await storage.query_qa(question, top_k, min_similarity, None, better_than_threshold)
            else:
                # 全局查询：在所有分类中查询并合并结果
                all_results = []

                for cat_name, storage in self.category_storages.items():
                    try:
                        # 使用很低的阈值获取所有可能的结果
                        result = await storage.query_qa(question, top_k=10, min_similarity=0.0, category=None, better_than_threshold=None)

                        # 收集所有结果，不管是否找到
                        if "all_results" in result and result["all_results"]:
                            all_results.extend(result["all_results"])
                        elif result.get("found", False):
                            # 单个结果
                            all_results.append({
                                "qa_id": result.get("qa_id"),
                                "question": result.get("question"),
                                "answer": result.get("answer"),
                                "category": result.get("category"),
                                "confidence": result.get("confidence"),
                                "similarity": result.get("similarity")
                            })
                    except Exception as e:
                        logger.error(f"Error querying category '{cat_name}': {e}")
                        continue
                
                if not all_results:
                    return {
                        "success": True,
                        "found": False,
                        "message": "No matching QA pairs found in any category"
                    }
                
                # 按相似度排序
                all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
                
                # 应用相似度阈值
                similarity_threshold = self.similarity_threshold if min_similarity is None else float(min_similarity)
                filtered_results = [r for r in all_results if r.get("similarity", 0) >= similarity_threshold]

                if not filtered_results:
                    best_similarity = all_results[0].get("similarity", 0) if all_results else 0
                    return {
                        "success": True,
                        "found": False,
                        "message": f"No QA pair found with similarity >= {similarity_threshold}",
                        "best_similarity": float(best_similarity)
                    }
                
                # 返回最佳结果
                best_result = filtered_results[0]
                return {
                    "success": True,
                    "found": True,
                    "qa_id": best_result.get("qa_id"),
                    "question": best_result.get("question"),
                    "answer": best_result.get("answer"),
                    "category": best_result.get("category"),
                    "confidence": best_result.get("confidence"),
                    "similarity": best_result.get("similarity"),
                    "all_results": filtered_results[:top_k]
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
        
        if category:
            # 列出指定分类的问答对
            storage = self.category_storages.get(category)
            if storage:
                return storage.list_qa_pairs(None, min_confidence)
        else:
            # 列出所有分类的问答对
            for qa_pair in self.qa_pairs.values():
                # 应用过滤条件
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
    
    def get_categories(self) -> List[str]:
        """获取所有分类列表"""
        return list(self.category_storages.keys())
    
    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取各分类的统计信息"""
        stats = {}
        for category, storage in self.category_storages.items():
            stats[category] = {
                "total_pairs": len(storage.qa_pairs),
                "storage_path": storage.qa_storage_file
            }
        return stats

    async def index_done_callback(self):
        """索引完成回调，保存所有分类的数据"""
        try:
            for category, storage in self.category_storages.items():
                await storage.index_done_callback()
            logger.info("All category storages saved successfully")
        except Exception as e:
            logger.error(f"Error in index_done_callback: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_pairs = len(self.qa_pairs)
        categories_count = len(self.category_storages)

        category_breakdown = {}
        for category, storage in self.category_storages.items():
            category_breakdown[category] = len(storage.qa_pairs)

        return {
            "total_qa_pairs": total_pairs,
            "total_categories": categories_count,
            "category_breakdown": category_breakdown,
            "storage_type": "CategoryQAStorage"
        }

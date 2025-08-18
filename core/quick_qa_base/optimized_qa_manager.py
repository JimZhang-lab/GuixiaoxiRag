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
from .category_qa_storage import CategoryQAStorage
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
                 working_dir: str = "./Q_A_Base",
                 qa_storage_dir: str = None):
        """
        初始化Q&A管理器

        Args:
            workspace: 工作空间名称
            namespace: 命名空间
            similarity_threshold: 相似度阈值（默认0.98）
            max_results: 最大返回结果数
            working_dir: 工作目录
            qa_storage_dir: QA存储目录（如果提供，将覆盖working_dir）
        """
        self.workspace = workspace
        self.namespace = namespace
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results

        # 使用 qa_storage_dir 如果提供，否则使用 working_dir
        self.working_dir = qa_storage_dir or working_dir

        # 创建存储目录
        os.makedirs(self.working_dir, exist_ok=True)

        # 全局配置
        self.global_config = {
            "working_dir": self.working_dir,
            "qa_storage_dir": qa_storage_dir,  # 传递 qa_storage_dir 配置
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
            
            # 创建分类存储
            self.storage = CategoryQAStorage(
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
    
    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> Dict[str, Any]:
        """添加问答对（带重复检查）"""
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return {
                "success": False,
                "error": "QA Manager not initialized"
            }

        try:
            qa_id = await self.storage.add_qa_pair(question, answer, **kwargs)

            # 检查是否是重复问题
            if qa_id and qa_id.startswith("DUPLICATE:"):
                parts = qa_id.split(":")
                existing_qa_id = parts[1]
                similarity = float(parts[2])

                return {
                    "success": False,
                    "is_duplicate": True,
                    "message": f"问题与现有问答对相似度过高: {similarity:.4f}",
                    "existing_qa_id": existing_qa_id,
                    "similarity": similarity
                }

            if qa_id:
                # 保存数据
                await self.storage.index_done_callback()
                logger.info(f"Added QA pair: {qa_id}")
                return {
                    "success": True,
                    "qa_id": qa_id,
                    "message": "问答对添加成功"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to add QA pair"
                }

        except Exception as e:
            logger.error(f"Error adding QA pair: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_qa_pairs_batch(self, qa_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加问答对"""
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}

        try:
            # 验证数据
            valid_qa_pairs = []
            failed_count = 0

            for qa_data in qa_pairs:
                question = qa_data.get("question")
                answer = qa_data.get("answer")

                if not question or not answer:
                    failed_count += 1
                    continue

                valid_qa_pairs.append(qa_data)

            # 使用存储的批量添加方法（现在返回详细结果）
            result = await self.storage.add_qa_pairs_batch(valid_qa_pairs)

            # 保存数据
            await self.storage.index_done_callback()

            return {
                "success": True,
                "added_count": result.get("added_count", 0),
                "skipped_count": result.get("skipped_count", 0),
                "failed_count": failed_count + result.get("failed_count", 0),
                "added_ids": result.get("added_ids", []),
                "skipped_duplicates": result.get("skipped_duplicates", []),
                "failed_items": result.get("failed_items", [])
            }

        except Exception as e:
            logger.error(f"Error in batch add: {e}")
            return {"success": False, "error": str(e)}
    
    async def query(self, question: str, top_k: Optional[int] = None, min_similarity: Optional[float] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """查询问答
        - min_similarity: 覆盖默认相似度阈值（按次查询）
        - category: 仅在该分类内检索匹配
        """
        if not self.initialized:
            return {"success": False, "error": "QA Manager not initialized"}

        if top_k is None:
            top_k = self.max_results

        try:
            start_time = time.time()
            # 将 min_similarity 转换为 NanoVectorDB 的距离阈值（1 - sim）传入底层查询，减少无意义结果
            better_than_threshold = None if min_similarity is None else (1.0 - float(min_similarity))
            result = await self.storage.query_qa(question, top_k, min_similarity=min_similarity, category=category, better_than_threshold=better_than_threshold)
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
    
    def get_categories(self) -> List[str]:
        """获取所有分类列表"""
        if not self.initialized:
            return []
        return self.storage.get_categories()

    def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取各分类的统计信息"""
        if not self.initialized:
            return {}
        return self.storage.get_category_stats()

    async def import_from_json(self, json_file: str) -> bool:
        """从JSON文件导入问答对"""
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return False

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 支持两种JSON格式
            qa_pairs = []
            if 'qa_pairs' in data:
                # 格式1: {"qa_pairs": [...]}
                qa_pairs = data['qa_pairs']
            elif isinstance(data, list):
                # 格式2: [...]
                qa_pairs = data
            else:
                logger.error("Invalid JSON format: expected 'qa_pairs' key or array")
                return False

            if not qa_pairs:
                logger.warning("No QA pairs found in JSON file")
                return True

            # 批量添加问答对
            result = await self.add_qa_pairs_batch(qa_pairs)

            if result.get("success"):
                added_count = result.get("added_count", 0)
                skipped_count = result.get("skipped_count", 0)
                failed_count = result.get("failed_count", 0)

                logger.info(f"JSON import completed: {added_count} added, {skipped_count} skipped, {failed_count} failed")
                return True
            else:
                logger.error(f"JSON import failed: {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return False

    async def import_from_csv(self, csv_file: str) -> bool:
        """从CSV文件导入问答对"""
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return False

        try:
            import pandas as pd

            # 读取CSV文件
            df = pd.read_csv(csv_file)

            # 检查必需的列
            required_columns = ['question', 'answer']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"CSV file missing required columns: {missing_columns}")
                return False

            # 转换为问答对列表
            qa_pairs = []
            for _, row in df.iterrows():
                qa_pair = {
                    'question': str(row['question']).strip(),
                    'answer': str(row['answer']).strip()
                }

                # 添加可选字段
                if 'category' in df.columns and pd.notna(row['category']):
                    qa_pair['category'] = str(row['category']).strip()
                if 'confidence' in df.columns and pd.notna(row['confidence']):
                    qa_pair['confidence'] = float(row['confidence'])
                if 'keywords' in df.columns and pd.notna(row['keywords']):
                    # 分号分隔的关键词
                    keywords = str(row['keywords']).split(';')
                    qa_pair['keywords'] = [kw.strip() for kw in keywords if kw.strip()]
                if 'source' in df.columns and pd.notna(row['source']):
                    qa_pair['source'] = str(row['source']).strip()

                # 跳过空的问答对
                if qa_pair['question'] and qa_pair['answer']:
                    qa_pairs.append(qa_pair)

            if not qa_pairs:
                logger.warning("No valid QA pairs found in CSV file")
                return True

            # 批量添加问答对
            result = await self.add_qa_pairs_batch(qa_pairs)

            if result.get("success"):
                added_count = result.get("added_count", 0)
                skipped_count = result.get("skipped_count", 0)
                failed_count = result.get("failed_count", 0)

                logger.info(f"CSV import completed: {added_count} added, {skipped_count} skipped, {failed_count} failed")
                return True
            else:
                logger.error(f"CSV import failed: {result.get('error')}")
                return False

        except ImportError:
            logger.error("pandas is required for CSV import")
            return False
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return False

    async def import_from_excel(self, excel_file: str) -> bool:
        """从Excel文件导入问答对"""
        if not self.initialized:
            logger.error("QA Manager not initialized")
            return False

        try:
            import pandas as pd

            # 读取Excel文件（默认第一个工作表）
            df = pd.read_excel(excel_file)

            # 检查必需的列
            required_columns = ['question', 'answer']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Excel file missing required columns: {missing_columns}")
                return False

            # 转换为问答对列表
            qa_pairs = []
            for _, row in df.iterrows():
                qa_pair = {
                    'question': str(row['question']).strip(),
                    'answer': str(row['answer']).strip()
                }

                # 添加可选字段
                if 'category' in df.columns and pd.notna(row['category']):
                    qa_pair['category'] = str(row['category']).strip()
                if 'confidence' in df.columns and pd.notna(row['confidence']):
                    qa_pair['confidence'] = float(row['confidence'])
                if 'keywords' in df.columns and pd.notna(row['keywords']):
                    # 分号分隔的关键词
                    keywords = str(row['keywords']).split(';')
                    qa_pair['keywords'] = [kw.strip() for kw in keywords if kw.strip()]
                if 'source' in df.columns and pd.notna(row['source']):
                    qa_pair['source'] = str(row['source']).strip()

                # 跳过空的问答对
                if qa_pair['question'] and qa_pair['answer']:
                    qa_pairs.append(qa_pair)

            if not qa_pairs:
                logger.warning("No valid QA pairs found in Excel file")
                return True

            # 批量添加问答对
            result = await self.add_qa_pairs_batch(qa_pairs)

            if result.get("success"):
                added_count = result.get("added_count", 0)
                skipped_count = result.get("skipped_count", 0)
                failed_count = result.get("failed_count", 0)

                logger.info(f"Excel import completed: {added_count} added, {skipped_count} skipped, {failed_count} failed")
                return True
            else:
                logger.error(f"Excel import failed: {result.get('error')}")
                return False

        except ImportError:
            logger.error("pandas and openpyxl are required for Excel import")
            return False
        except Exception as e:
            logger.error(f"Error importing from Excel: {e}")
            return False

    async def cleanup(self):
        """清理资源"""
        try:
            if self.storage:
                # 对于CategoryQAStorage，需要清理所有分类存储
                if hasattr(self.storage, 'category_storages'):
                    for storage in self.storage.category_storages.values():
                        await storage.index_done_callback()
                else:
                    await self.storage.index_done_callback()
            logger.info("QA Manager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

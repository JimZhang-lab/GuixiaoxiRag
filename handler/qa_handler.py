"""
问答系统处理器
"""

import asyncio
import json
import os
import time
from typing import List, Optional, Dict, Any
import logging

from common.logging_utils import logger_manager
from common.config import settings
from core.common.llm_client import create_embedding_function

logger = logger_manager.get_logger(__name__)


class QAHandler:
    """问答系统处理器"""
    
    def __init__(self):
        self.qa_manager = None
        self.embedding_function = None
        self.initialized = False
        
        # 配置参数（支持独立的 QA 存储目录）
        self.qa_storage_dir = settings.qa_storage_dir or os.path.join(settings.working_dir, "Q_A_Base")
        self.qa_storage_file = os.path.join(self.qa_storage_dir, "qa_pairs.json")
        self.similarity_threshold = getattr(settings, 'qa_similarity_threshold', 0.98)  # 使用0.98高精度阈值
        self.max_results = getattr(settings, 'qa_max_results', 10)
        
        logger.info("QAHandler initialized")
    
    async def initialize(self) -> bool:
        """初始化问答系统"""
        try:
            # 创建存储目录
            os.makedirs(self.qa_storage_dir, exist_ok=True)
            
            # 导入并创建优化的QAManager
            from core.quick_qa_base.optimized_qa_manager import OptimizedQAManager

            self.qa_manager = OptimizedQAManager(
                workspace="qa_base",
                namespace="default",
                similarity_threshold=self.similarity_threshold,
                max_results=self.max_results,
                working_dir=self.qa_storage_dir,
                qa_storage_dir=self.qa_storage_dir  # 明确传递 QA 存储目录
            )
            
            # 初始化QAManager
            success = await self.qa_manager.initialize()
            if success:
                self.initialized = True
                logger.info("QA Handler initialized successfully")
                
                # 加载默认问答对
                await self._load_default_qa_pairs()
                
                return True
            else:
                logger.error("Failed to initialize QA Manager")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing QA Handler: {e}")
            return False
    
    async def _load_default_qa_pairs(self):
        """加载默认问答对"""
        try:
            # 检查是否已有问答对
            stats = self.qa_manager.get_statistics()
            if stats.get("success") and stats.get("data", {}).get("storage_stats", {}).get("total_pairs", 0) > 0:
                logger.info(f"QA storage already has {stats['data']['storage_stats']['total_pairs']} pairs")
                return

            # 尝试从文件加载默认问答对
            default_file = os.path.join(self.qa_storage_dir, "default_qa_pairs.json")
            if os.path.exists(default_file):
                try:
                    with open(default_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    qa_pairs = data.get('qa_pairs', [])
                    if qa_pairs:
                        result = await self.qa_manager.add_qa_pairs_batch(qa_pairs)
                        if result.get("success"):
                            logger.info(f"Loaded {result.get('added_count', 0)} default QA pairs from file")
                        else:
                            logger.error(f"Failed to load default QA pairs: {result.get('error')}")
                        return
                except Exception as e:
                    logger.error(f"Error reading default QA pairs file: {e}")
            
            # 默认问答对数据
            default_qa_pairs = [
                {
                    "question": "什么是GuiXiaoXiRag？",
                    "answer": "GuiXiaoXiRag是一个基于FastAPI的智能知识问答系统，集成了知识图谱、向量检索、意图识别等多种AI技术，提供强大的知识管理和智能查询功能。",
                    "category": "system",
                    "confidence": 1.0,
                    "keywords": ["GuiXiaoXiRag", "系统介绍", "知识问答"],
                    "source": "system_default"
                },
                {
                    "question": "如何使用问答系统？",
                    "answer": "您可以通过API接口向问答系统提交问题，系统会使用向量相似度匹配找到最相关的答案。支持单个查询和批量查询，也可以添加新的问答对来扩展知识库。",
                    "category": "usage",
                    "confidence": 1.0,
                    "keywords": ["使用方法", "API", "查询"],
                    "source": "system_default"
                },
                {
                    "question": "问答系统支持哪些功能？",
                    "answer": "问答系统支持：1) 智能问答查询；2) 问答对的增删改查；3) 批量导入导出；4) 相似度搜索；5) 分类管理；6) 统计分析；7) 数据备份恢复等功能。",
                    "category": "features",
                    "confidence": 1.0,
                    "keywords": ["功能", "特性", "能力"],
                    "source": "system_default"
                },
                {
                    "question": "如何提高问答匹配的准确性？",
                    "answer": "提高匹配准确性的方法：1) 添加更多高质量的问答对；2) 优化问题的表述，使用清晰准确的语言；3) 合理设置相似度阈值；4) 为问答对添加相关关键词；5) 定期更新和维护问答库。",
                    "category": "optimization",
                    "confidence": 0.9,
                    "keywords": ["准确性", "优化", "匹配"],
                    "source": "system_default"
                }
            ]
            
            # 临时禁用内置默认问答对的自动添加，避免重复数据
            # 因为我们已经在数据文件中有了这些问答对
            logger.info("Skipping built-in default QA pairs addition to avoid duplicates")

            # 如果需要重新启用，可以取消下面的注释
            """
            # 批量添加默认问答对
            result = await self.qa_manager.add_qa_pairs_batch(default_qa_pairs)
            if result.get("success"):
                logger.info(f"Added {result.get('added_count', 0)} built-in default QA pairs")
            else:
                logger.error(f"Failed to add built-in default QA pairs: {result.get('error')}")
            """
            
            
        except Exception as e:
            logger.warning(f"Failed to load default QA pairs: {e}")
    
    async def add_qa_pair(self, question: str, answer: str, **kwargs) -> Optional[str]:
        """添加问答对"""
        if not self.initialized:
            logger.error("QA Handler not initialized")
            return None
        
        return await self.qa_manager.add_qa_pair(question, answer, **kwargs)
    
    async def add_qa_pairs_batch(self, qa_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量添加问答对"""
        if not self.initialized:
            logger.error("QA Handler not initialized")
            return {"success": False, "error": "QA Handler not initialized"}

        return await self.qa_manager.add_qa_pairs_batch(qa_data)
    
    async def query(self, question: str, top_k: int = 1) -> Dict[str, Any]:
        """查询问答"""
        if not self.initialized:
            return {
                "success": False,
                "error": "QA Handler not initialized"
            }
        
        return await self.qa_manager.query(question, top_k)
    
    async def batch_query(self, questions: List[str], **kwargs) -> List[Dict[str, Any]]:
        """批量查询"""
        if not self.initialized:
            return []
        
        results = []
        for question in questions:
            result = await self.query(question, **kwargs)
            results.append(result)
        
        return results
    
    def list_qa_pairs(self, **kwargs) -> List[Dict[str, Any]]:
        """列出问答对"""
        if not self.initialized:
            return []
        
        return self.qa_manager.list_qa_pairs(**kwargs)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.initialized:
            return {"error": "QA Handler not initialized"}
        
        return self.qa_manager.get_statistics()
    
    async def save_storage(self) -> bool:
        """保存存储"""
        if not self.initialized:
            return False
        
        return await self.qa_manager.save_storage()
    
    async def import_from_json(self, json_file: str) -> bool:
        """从JSON文件导入"""
        if not self.initialized:
            return False

        return await self.qa_manager.import_from_json(json_file)

    async def import_from_csv(self, csv_file: str) -> bool:
        """从CSV文件导入"""
        if not self.initialized:
            return False

        return await self.qa_manager.import_from_csv(csv_file)

    async def import_from_excel(self, excel_file: str) -> bool:
        """从Excel文件导入"""
        if not self.initialized:
            return False

        return await self.qa_manager.import_from_excel(excel_file)
    
    async def export_to_json(self, json_file: str) -> bool:
        """导出到JSON文件"""
        if not self.initialized:
            return False
        
        try:
            qa_pairs = self.list_qa_pairs()
            
            # 创建导出目录
            export_dir = os.path.dirname(json_file)
            if export_dir:
                os.makedirs(export_dir, exist_ok=True)
            
            # 导出数据
            export_data = {
                "metadata": {
                    "export_time": time.time(),
                    "total_pairs": len(qa_pairs),
                    "version": "1.0"
                },
                "qa_pairs": qa_pairs
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(qa_pairs)} QA pairs to {json_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting QA pairs: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        if self.initialized and self.qa_manager:
            await self.qa_manager.cleanup()
            logger.info("QA Handler cleanup completed")

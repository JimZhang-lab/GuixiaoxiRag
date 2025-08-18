"""
问答系统API处理器
"""

import asyncio
import json
import os
import time
from typing import List, Optional, Dict, Any
import logging

from model.qa_models import (
    QAPairCreate, QAPairUpdate, QAPairResponse, QAPairBatchCreate,
    QAQueryRequest, QAQueryResponse, QAListRequest, QAListResponse,
    QAImportRequest, QAImportResponse, QAExportRequest,
    QAStatistics, QAHealthCheck, QAConfigUpdate,
    QABatchQueryRequest, QABatchQueryResponse,
    QABackupRequest, QABackupResponse, QARestoreRequest, QARestoreResponse
)
from model.base_models import BaseResponse
from common.logging_utils import logger_manager
from common.config import settings

logger = logger_manager.get_logger(__name__)


class QAAPIHandler:
    """问答系统API处理器"""
    
    def __init__(self):
        self.qa_manager = None
        self.initialized = False
        
        # 配置参数（使用统一的 QA 存储目录）
        self.qa_storage_dir = settings.qa_storage_dir or os.path.join(settings.working_dir, "Q_A_Base")
        self.qa_storage_file = os.path.join(self.qa_storage_dir, "qa_pairs.json")
        self.backup_dir = os.path.join(self.qa_storage_dir, "backups")
        
        # 统计信息
        self.api_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
        
        logger.info("QAAPIHandler initialized")
    
    async def initialize(self) -> bool:
        """初始化问答系统"""
        try:
            # 导入QAManager
            from handler.qa_handler import QAHandler
            
            # 创建QA处理器
            self.qa_handler = QAHandler()
            success = await self.qa_handler.initialize()
            
            if success:
                self.qa_manager = self.qa_handler.qa_manager
                self.initialized = True
                logger.info("QA API Handler initialized successfully")
                return True
            else:
                logger.error("Failed to initialize QA Handler")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing QA API Handler: {e}")
            return False
    
    def _update_stats(self, success: bool, response_time: float):
        """更新统计信息"""
        self.api_stats["total_requests"] += 1
        if success:
            self.api_stats["successful_requests"] += 1
        else:
            self.api_stats["failed_requests"] += 1
        
        # 更新平均响应时间
        total_time = self.api_stats["avg_response_time"] * (self.api_stats["total_requests"] - 1)
        self.api_stats["avg_response_time"] = (total_time + response_time) / self.api_stats["total_requests"]
    
    async def create_qa_pair(self, request: QAPairCreate) -> BaseResponse:
        """创建问答对"""
        start_time = time.time()
        
        if not self.initialized:
            return BaseResponse(
                success=False,
                message="问答系统未初始化",
                error_code="QA_NOT_INITIALIZED"
            )
        
        try:
            result = await self.qa_manager.add_qa_pair(
                question=request.question,
                answer=request.answer,
                category=request.category,
                confidence=request.confidence,
                keywords=request.keywords,
                source=request.source,
                skip_duplicate_check=request.skip_duplicate_check,
                duplicate_threshold=request.duplicate_threshold
            )

            response_time = time.time() - start_time

            if result.get("success"):
                self._update_stats(True, response_time)

                return BaseResponse(
                    success=True,
                    message=result.get("message", "问答对创建成功"),
                    data={"qa_id": result.get("qa_id")}
                )
            else:
                self._update_stats(False, response_time)

                # 检查是否是重复问题
                if result.get("is_duplicate"):
                    return BaseResponse(
                        success=False,
                        message=result.get("message", "问题重复"),
                        error_code="QA_DUPLICATE",
                        data={
                            "existing_qa_id": result.get("existing_qa_id"),
                            "similarity": result.get("similarity")
                        }
                    )
                else:
                    return BaseResponse(
                        success=False,
                        message=result.get("error", "问答对创建失败"),
                        error_code="QA_CREATE_FAILED"
                    )
                
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error creating QA pair: {e}")
            
            return BaseResponse(
                success=False,
                message=f"创建问答对时发生错误: {str(e)}",
                error_code="QA_CREATE_ERROR"
            )
    
    async def create_qa_pairs_batch(self, request: QAPairBatchCreate) -> BaseResponse:
        """批量创建问答对"""
        start_time = time.time()
        
        if not self.initialized:
            return BaseResponse(
                success=False,
                message="问答系统未初始化",
                error_code="QA_NOT_INITIALIZED"
            )
        
        try:
            # 转换为字典格式
            qa_data = []
            for qa_pair in request.qa_pairs:
                qa_data.append({
                    "question": qa_pair.question,
                    "answer": qa_pair.answer,
                    "category": qa_pair.category,
                    "confidence": qa_pair.confidence,
                    "keywords": qa_pair.keywords,
                    "source": qa_pair.source,
                    "skip_duplicate_check": qa_pair.skip_duplicate_check,
                    "duplicate_threshold": qa_pair.duplicate_threshold
                })
            
            result = await self.qa_manager.add_qa_pairs_batch(qa_data)

            response_time = time.time() - start_time
            self._update_stats(True, response_time)

            added_count = result.get("added_count", 0)
            skipped_count = result.get("skipped_count", 0)
            failed_count = result.get("failed_count", 0)

            message_parts = []
            if added_count > 0:
                message_parts.append(f"成功添加 {added_count} 个问答对")
            if skipped_count > 0:
                message_parts.append(f"跳过 {skipped_count} 个重复问题")
            if failed_count > 0:
                message_parts.append(f"失败 {failed_count} 个")

            message = "批量创建完成：" + "，".join(message_parts) if message_parts else "批量创建完成"

            return BaseResponse(
                success=True,
                message=message,
                data={
                    "added_count": added_count,
                    "skipped_count": skipped_count,
                    "failed_count": failed_count,
                    "qa_ids": result.get("added_ids", []),
                    "skipped_duplicates": result.get("skipped_duplicates", []),
                    "failed_items": result.get("failed_items", [])
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error batch creating QA pairs: {e}")
            
            return BaseResponse(
                success=False,
                message=f"批量创建问答对时发生错误: {str(e)}",
                error_code="QA_BATCH_CREATE_ERROR"
            )
    
    async def query_qa(self, request: QAQueryRequest) -> QAQueryResponse:
        """查询问答"""
        start_time = time.time()
        
        if not self.initialized:
            return QAQueryResponse(
                success=False,
                response_time=time.time() - start_time,
                error="问答系统未初始化"
            )
        
        try:
            # 执行查询（支持按请求覆盖相似度阈值与分类过滤）
            result = await self.qa_manager.query(
                question=request.question,
                top_k=request.top_k,
                min_similarity=request.min_similarity,
                category=request.category,
            )
            
            response_time = time.time() - start_time
            self._update_stats(result.get("success", False), response_time)
            
            # 转换为响应模型
            if result.get("success") and result.get("found"):
                from model.qa_models import QASearchResult, QAPairResponse
                
                # 构建所有结果
                all_results = []
                for i, res in enumerate(result.get("all_results", [])):
                    qa_pair_response = QAPairResponse(
                        id=res["qa_id"],
                        question=res["question"],
                        answer=res["answer"],
                        category=res["category"],
                        confidence=res["confidence"],
                        keywords=[],  # 从存储中获取
                        source="",    # 从存储中获取
                        created_at=time.time(),  # 从存储中获取
                        updated_at=time.time()   # 从存储中获取
                    )
                    
                    search_result = QASearchResult(
                        qa_pair=qa_pair_response,
                        similarity=res["similarity"],
                        rank=i + 1
                    )
                    all_results.append(search_result)
                
                return QAQueryResponse(
                    success=True,
                    found=True,
                    answer=result["answer"],
                    question=result["question"],
                    similarity=result["similarity"],
                    confidence=result["confidence"],
                    category=result["category"],
                    qa_id=result["qa_id"],
                    response_time=response_time,
                    all_results=all_results
                )
            else:
                return QAQueryResponse(
                    success=result.get("success", True),
                    found=False,
                    response_time=response_time,
                    message=result.get("message", "未找到匹配的问答对")
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error querying QA: {e}")
            
            return QAQueryResponse(
                success=False,
                found=False,
                response_time=response_time,
                error=f"查询问答时发生错误: {str(e)}"
            )
    
    async def list_qa_pairs(self, request: QAListRequest) -> BaseResponse:
        """获取问答对列表"""
        start_time = time.time()
        
        if not self.initialized:
            return BaseResponse(
                success=False,
                message="问答系统未初始化",
                error_code="QA_NOT_INITIALIZED"
            )
        
        try:
            # 获取所有问答对（不分页，获取原始数据）
            qa_result = self.qa_manager.list_qa_pairs(
                category=request.category,
                min_confidence=request.min_confidence,
                page=1,
                page_size=10000  # 获取所有数据
            )

            # 检查结果
            if not qa_result.get("success", False):
                return BaseResponse(
                    success=False,
                    message=qa_result.get("error", "获取问答对失败"),
                    error_code="QA_LIST_ERROR"
                )

            # 获取问答对列表
            qa_pairs = qa_result.get("data", {}).get("qa_pairs", [])

            # 关键词过滤
            if request.keyword:
                keyword_lower = request.keyword.lower()
                filtered_pairs = []
                for qa_pair in qa_pairs:
                    if (keyword_lower in qa_pair["question"].lower() or
                        keyword_lower in qa_pair["answer"].lower() or
                        any(keyword_lower in kw.lower() for kw in qa_pair.get("keywords", []))):
                        filtered_pairs.append(qa_pair)
                qa_pairs = filtered_pairs

            # 分页处理
            total = len(qa_pairs)
            start_idx = (request.page - 1) * request.page_size
            end_idx = start_idx + request.page_size
            paginated_pairs = qa_pairs[start_idx:end_idx]
            
            # 转换为响应模型
            qa_responses = []
            for qa_pair in paginated_pairs:
                qa_response = QAPairResponse(
                    id=qa_pair["id"],
                    question=qa_pair["question"],
                    answer=qa_pair["answer"],
                    category=qa_pair["category"],
                    confidence=qa_pair["confidence"],
                    keywords=qa_pair.get("keywords", []),
                    source=qa_pair.get("source", ""),
                    created_at=qa_pair.get("created_at", time.time()),
                    updated_at=qa_pair.get("updated_at", time.time())
                )
                qa_responses.append(qa_response)
            
            total_pages = (total + request.page_size - 1) // request.page_size
            
            list_response = QAListResponse(
                qa_pairs=qa_responses,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=total_pages
            )
            
            response_time = time.time() - start_time
            self._update_stats(True, response_time)
            
            return BaseResponse(
                success=True,
                message=f"获取问答对列表成功，共 {total} 条记录",
                data=list_response.dict()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error listing QA pairs: {e}")
            
            return BaseResponse(
                success=False,
                message=f"获取问答对列表时发生错误: {str(e)}",
                error_code="QA_LIST_ERROR"
            )
    
    async def get_statistics(self) -> BaseResponse:
        """获取统计信息"""
        start_time = time.time()
        
        if not self.initialized:
            return BaseResponse(
                success=False,
                message="问答系统未初始化",
                error_code="QA_NOT_INITIALIZED"
            )
        
        try:
            stats = self.qa_manager.get_statistics()
            
            qa_statistics = QAStatistics(
                total_pairs=stats["storage_stats"]["total_pairs"],
                categories=stats["storage_stats"]["categories"],
                average_confidence=stats["storage_stats"]["average_confidence"],
                similarity_threshold=stats["storage_stats"]["similarity_threshold"],
                vector_index_size=stats["storage_stats"]["vector_index_size"],
                embedding_dim=stats["storage_stats"]["embedding_dim"],
                query_stats=stats["storage_stats"]["query_stats"]
            )
            
            response_time = time.time() - start_time
            self._update_stats(True, response_time)
            
            return BaseResponse(
                success=True,
                message="获取统计信息成功",
                data=qa_statistics.dict()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error getting QA statistics: {e}")
            
            return BaseResponse(
                success=False,
                message=f"获取统计信息时发生错误: {str(e)}",
                error_code="QA_STATS_ERROR"
            )
    
    async def health_check(self) -> BaseResponse:
        """健康检查"""
        start_time = time.time()
        
        try:
            if not self.initialized:
                health_check = QAHealthCheck(
                    status="unhealthy",
                    qa_storage_status="not_initialized",
                    embedding_status="unknown",
                    total_qa_pairs=0,
                    avg_response_time=0.0,
                    error_rate=100.0
                )
            else:
                stats = self.qa_manager.get_statistics()
                
                # 计算错误率
                total_requests = self.api_stats["total_requests"]
                error_rate = 0.0
                if total_requests > 0:
                    error_rate = (self.api_stats["failed_requests"] / total_requests) * 100
                
                health_check = QAHealthCheck(
                    status="healthy",
                    qa_storage_status="ready",
                    embedding_status="ready",
                    total_qa_pairs=stats["storage_stats"]["total_pairs"],
                    avg_response_time=self.api_stats["avg_response_time"],
                    error_rate=error_rate
                )
            
            response_time = time.time() - start_time
            self._update_stats(True, response_time)
            
            return BaseResponse(
                success=True,
                message="健康检查完成",
                data=health_check.dict()
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_stats(False, response_time)
            logger.error(f"Error in QA health check: {e}")
            
            return BaseResponse(
                success=False,
                message=f"健康检查时发生错误: {str(e)}",
                error_code="QA_HEALTH_CHECK_ERROR"
            )
    
    async def cleanup(self):
        """清理资源"""
        if self.initialized and self.qa_manager:
            await self.qa_manager.cleanup()
            logger.info("QA API Handler cleanup completed")

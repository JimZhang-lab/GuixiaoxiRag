"""
问答系统路由
"""

import asyncio
import os
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
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

logger = logger_manager.get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/qa", tags=["问答系统"])

# 全局API处理器实例
qa_api_handler = None


async def get_qa_api_handler():
    """获取问答API处理器实例"""
    global qa_api_handler
    if qa_api_handler is None:
        from api.qa_api import QAAPIHandler
        qa_api_handler = QAAPIHandler()
        await qa_api_handler.initialize()
    return qa_api_handler


@router.get("/health", response_model=BaseResponse, summary="问答系统健康检查")
async def health_check():
    """
    检查问答系统的健康状态
    
    Returns:
        BaseResponse: 健康检查结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.health_check()
    except Exception as e:
        logger.error(f"QA health check error: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post("/pairs", response_model=BaseResponse, summary="创建问答对")
async def create_qa_pair(request: QAPairCreate):
    """
    创建单个问答对
    
    Args:
        request: 问答对创建请求
        
    Returns:
        BaseResponse: 创建结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.create_qa_pair(request)
    except Exception as e:
        logger.error(f"Create QA pair error: {e}")
        raise HTTPException(status_code=500, detail=f"创建问答对失败: {str(e)}")


@router.post("/pairs/batch", response_model=BaseResponse, summary="批量创建问答对")
async def create_qa_pairs_batch(request: QAPairBatchCreate):
    """
    批量创建问答对
    
    Args:
        request: 批量创建请求
        
    Returns:
        BaseResponse: 创建结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.create_qa_pairs_batch(request)
    except Exception as e:
        logger.error(f"Batch create QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"批量创建问答对失败: {str(e)}")


@router.post("/query", response_model=QAQueryResponse, summary="问答查询")
async def query_qa(request: QAQueryRequest):
    """
    执行问答查询
    
    Args:
        request: 查询请求
        
    Returns:
        QAQueryResponse: 查询结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.query_qa(request)
    except Exception as e:
        logger.error(f"QA query error: {e}")
        raise HTTPException(status_code=500, detail=f"问答查询失败: {str(e)}")


@router.post("/query/batch", response_model=QABatchQueryResponse, summary="批量问答查询")
async def batch_query_qa(request: QABatchQueryRequest):
    """
    批量执行问答查询
    
    Args:
        request: 批量查询请求
        
    Returns:
        QABatchQueryResponse: 批量查询结果
    """
    try:
        handler = await get_qa_api_handler()
        start_time = time.time()
        
        # 执行批量查询
        results = []
        successful_queries = 0
        failed_queries = 0
        
        if request.parallel:
            # 并行处理
            tasks = []
            for question in request.questions:
                query_request = QAQueryRequest(
                    question=question,
                    top_k=request.top_k,
                    min_similarity=request.min_similarity
                )
                task = handler.query_qa(query_request)
                tasks.append(task)
            
            # 等待所有任务完成
            query_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(query_results):
                if isinstance(result, Exception):
                    failed_queries += 1
                    error_response = QAQueryResponse(
                        success=False,
                        found=False,
                        response_time=0.0,
                        error=f"查询失败: {str(result)}"
                    )
                    results.append(error_response)
                else:
                    if result.success:
                        successful_queries += 1
                    else:
                        failed_queries += 1
                    results.append(result)
        else:
            # 串行处理
            for question in request.questions:
                query_request = QAQueryRequest(
                    question=question,
                    top_k=request.top_k,
                    min_similarity=request.min_similarity
                )
                
                try:
                    result = await handler.query_qa(query_request)
                    if result.success:
                        successful_queries += 1
                    else:
                        failed_queries += 1
                    results.append(result)
                except Exception as e:
                    failed_queries += 1
                    error_response = QAQueryResponse(
                        success=False,
                        found=False,
                        response_time=0.0,
                        error=f"查询失败: {str(e)}"
                    )
                    results.append(error_response)
        
        total_time = time.time() - start_time
        average_time = total_time / len(request.questions) if request.questions else 0.0
        
        return QABatchQueryResponse(
            success=True,
            results=results,
            total_queries=len(request.questions),
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            total_time=total_time,
            average_time=average_time
        )
        
    except Exception as e:
        logger.error(f"Batch QA query error: {e}")
        raise HTTPException(status_code=500, detail=f"批量问答查询失败: {str(e)}")


@router.get("/pairs", response_model=BaseResponse, summary="获取问答对列表")
async def list_qa_pairs(
    category: Optional[str] = None,
    min_confidence: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None
):
    """
    获取问答对列表
    
    Args:
        category: 分类过滤
        min_confidence: 最小置信度
        page: 页码
        page_size: 每页数量
        keyword: 关键词搜索
        
    Returns:
        BaseResponse: 问答对列表
    """
    try:
        request = QAListRequest(
            category=category,
            min_confidence=min_confidence,
            page=page,
            page_size=page_size,
            keyword=keyword
        )
        
        handler = await get_qa_api_handler()
        return await handler.list_qa_pairs(request)
    except Exception as e:
        logger.error(f"List QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"获取问答对列表失败: {str(e)}")


@router.get("/statistics", response_model=BaseResponse, summary="获取问答系统统计信息")
async def get_qa_statistics():
    """
    获取问答系统的统计信息
    
    Returns:
        BaseResponse: 统计信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.get_statistics()
    except Exception as e:
        logger.error(f"Get QA statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/import", response_model=BaseResponse, summary="导入问答对")
async def import_qa_pairs(
    file: UploadFile = File(..., description="导入文件"),
    file_type: str = Form(..., description="文件类型"),
    overwrite_existing: bool = Form(False, description="是否覆盖已存在的问答对"),
    default_category: str = Form("imported", description="默认分类"),
    default_source: str = Form("file_import", description="默认来源")
):
    """
    从文件导入问答对
    
    Args:
        file: 上传的文件
        file_type: 文件类型 (json/csv/xlsx)
        overwrite_existing: 是否覆盖已存在的问答对
        default_category: 默认分类
        default_source: 默认来源
        
    Returns:
        BaseResponse: 导入结果
    """
    try:
        handler = await get_qa_api_handler()
        
        # 保存上传的文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            if file_type.lower() == "json":
                # 导入JSON文件
                success = await handler.qa_handler.import_from_json(temp_file_path)
                if success:
                    return BaseResponse(
                        success=True,
                        message="JSON文件导入成功"
                    )
                else:
                    return BaseResponse(
                        success=False,
                        message="JSON文件导入失败",
                        error_code="IMPORT_FAILED"
                    )
            else:
                return BaseResponse(
                    success=False,
                    message=f"暂不支持 {file_type} 格式的文件导入",
                    error_code="UNSUPPORTED_FORMAT"
                )
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Import QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"导入问答对失败: {str(e)}")


@router.get("/export", response_class=FileResponse, summary="导出问答对")
async def export_qa_pairs(
    format: str = "json",
    category: Optional[str] = None,
    min_confidence: Optional[float] = None,
    include_vectors: bool = False
):
    """
    导出问答对到文件
    
    Args:
        format: 导出格式 (json/csv/xlsx)
        category: 分类过滤
        min_confidence: 最小置信度
        include_vectors: 是否包含向量数据
        
    Returns:
        FileResponse: 导出的文件
    """
    try:
        handler = await get_qa_api_handler()
        
        # 创建临时导出文件
        import tempfile
        temp_dir = tempfile.mkdtemp()
        export_file = os.path.join(temp_dir, f"qa_pairs_export_{int(time.time())}.{format}")
        
        if format.lower() == "json":
            success = await handler.qa_handler.export_to_json(export_file)
            if success:
                return FileResponse(
                    path=export_file,
                    filename=f"qa_pairs_export_{int(time.time())}.json",
                    media_type="application/json"
                )
            else:
                raise HTTPException(status_code=500, detail="导出失败")
        else:
            raise HTTPException(status_code=400, detail=f"暂不支持 {format} 格式的导出")
            
    except Exception as e:
        logger.error(f"Export QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"导出问答对失败: {str(e)}")


@router.post("/backup", response_model=BaseResponse, summary="备份问答数据")
async def backup_qa_data(request: QABackupRequest):
    """
    备份问答系统数据
    
    Args:
        request: 备份请求
        
    Returns:
        BaseResponse: 备份结果
    """
    try:
        handler = await get_qa_api_handler()
        
        # 执行备份
        success = await handler.qa_handler.save_storage()
        
        if success:
            backup_file = handler.qa_handler.qa_storage_file
            backup_size = os.path.getsize(backup_file) if os.path.exists(backup_file) else 0
            stats = handler.qa_handler.get_statistics()
            
            backup_response = QABackupResponse(
                success=True,
                backup_file=backup_file,
                backup_size=backup_size,
                qa_pairs_count=stats.get("storage_stats", {}).get("total_pairs", 0),
                created_at=time.time(),
                message="备份创建成功"
            )
            
            return BaseResponse(
                success=True,
                message="问答数据备份成功",
                data=backup_response.dict()
            )
        else:
            return BaseResponse(
                success=False,
                message="问答数据备份失败",
                error_code="BACKUP_FAILED"
            )
            
    except Exception as e:
        logger.error(f"Backup QA data error: {e}")
        raise HTTPException(status_code=500, detail=f"备份问答数据失败: {str(e)}")


@router.delete("/clear", response_model=BaseResponse, summary="清空问答数据")
async def clear_qa_data():
    """
    清空所有问答数据
    
    Returns:
        BaseResponse: 清空结果
    """
    try:
        handler = await get_qa_api_handler()
        
        # 重新初始化存储（相当于清空）
        if handler.qa_handler and handler.qa_handler.qa_manager:
            handler.qa_handler.qa_manager.storage.qa_pairs.clear()
            await handler.qa_handler.qa_manager.storage._rebuild_vector_index()
            await handler.qa_handler.qa_manager.save_storage()
        
        return BaseResponse(
            success=True,
            message="问答数据已清空"
        )
        
    except Exception as e:
        logger.error(f"Clear QA data error: {e}")
        raise HTTPException(status_code=500, detail=f"清空问答数据失败: {str(e)}")


# 启动时初始化
@router.on_event("startup")
async def startup_event():
    """启动时初始化问答系统"""
    try:
        await get_qa_api_handler()
        logger.info("QA system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize QA system: {e}")


# 关闭时清理资源
@router.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    global qa_api_handler
    if qa_api_handler:
        await qa_api_handler.cleanup()
        logger.info("QA system cleanup completed")

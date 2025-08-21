"""
问答系统路由
"""

import asyncio
import os
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Path
from fastapi.responses import FileResponse
import logging

from model.qa_models import (
    QAPairCreate, QAPairUpdate, QAPairResponse, QAPairBatchCreate,
    QAQueryRequest, QAQueryResponse, QAListRequest, QAListResponse,
    QAImportRequest, QAImportResponse, QAExportRequest,
    QAStatistics, QAHealthCheck, QAConfigUpdate,
    QABatchQueryRequest, QABatchQueryResponse,
    QABackupRequest, QABackupResponse, QARestoreRequest, QARestoreResponse,
    QACategoryDeleteRequest, QACategoryDeleteResponse,
    QAPairsDeleteRequest, QAPairsDeleteResponse
)
from model.base_models import BaseResponse
from common.logging_utils import logger_manager

logger = logger_manager.get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/qa", tags=["问答系统"])

# 注意：QA API处理器实例现在由 initialize/service_initializer.py 管理


async def get_qa_api_handler():
    """获取问答API处理器实例"""
    from initialize.service_initializer import get_qa_api_handler as get_global_qa_handler
    handler = get_global_qa_handler()
    if handler is None:
        logger.error("QA API Handler not initialized in service initializer")
        raise HTTPException(status_code=500, detail="QA系统未初始化")
    return handler


@router.get(
    "/health",
    response_model=BaseResponse,
    summary="问答系统健康检查",
    description="""
    检查问答系统的整体健康状态和运行情况。

    **检查项目：**
    - QA存储状态
    - 向量化服务状态
    - 问答对数量统计
    - 平均响应时间
    - 错误率统计

    **健康状态：**
    - healthy: 系统运行正常
    - unhealthy: 系统存在问题
    - not_initialized: 系统未初始化

    **返回数据：**
    - status: 健康状态
    - qa_storage_status: 问答存储状态
    - embedding_status: 向量化服务状态
    - total_qa_pairs: 总问答对数量
    - avg_response_time: 平均响应时间
    - error_rate: 错误率百分比

    **使用场景：**
    - 系统监控和告警
    - 服务可用性检查
    - 性能指标监控
    """,
    responses={
        200: {
            "description": "健康检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "健康检查完成",
                        "data": {
                            "status": "healthy",
                            "qa_storage_status": "ready",
                            "embedding_status": "ready",
                            "total_qa_pairs": 150,
                            "avg_response_time": 0.25,
                            "error_rate": 2.5
                        }
                    }
                }
            }
        },
        500: {
            "description": "健康检查失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "健康检查失败: 系统未初始化"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    检查问答系统的健康状态

    Returns:
        BaseResponse: 健康检查结果，包含详细的系统状态信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.health_check()
    except Exception as e:
        logger.error(f"QA health check error: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post(
    "/pairs",
    response_model=BaseResponse,
    summary="创建问答对",
    description="""
    创建单个问答对到问答系统中。

    **功能特性：**
    - 自动重复检查（可配置）
    - 向量化存储
    - 分类管理
    - 置信度评分

    **参数说明：**
    - question: 问题文本（必填，1-2000字符）
    - answer: 答案文本（必填，1-10000字符）
    - category: 分类标签（可选，默认"general"）
    - confidence: 置信度（可选，0.0-1.0，默认1.0）
    - keywords: 关键词列表（可选）
    - source: 来源标识（可选，默认"manual"）
    - skip_duplicate_check: 跳过重复检查（可选，默认false）
    - duplicate_threshold: 重复检查阈值（可选，默认0.98）

    **重复检查：**
    - 系统会自动检查相似问题
    - 相似度超过阈值时会拒绝创建
    - 可通过skip_duplicate_check跳过检查

    **返回数据：**
    - qa_id: 创建的问答对ID
    - message: 操作结果消息
    """,
    responses={
        200: {
            "description": "创建成功",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "创建成功",
                            "value": {
                                "success": True,
                                "message": "问答对创建成功",
                                "data": {"qa_id": "qa_12345678"}
                            }
                        },
                        "duplicate": {
                            "summary": "重复问题",
                            "value": {
                                "success": False,
                                "message": "问题与现有问答对相似度过高: 0.9850",
                                "error_code": "QA_DUPLICATE",
                                "data": {
                                    "existing_qa_id": "qa_87654321",
                                    "similarity": 0.985
                                }
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "question"],
                                "msg": "文本内容不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "创建问答对失败: 系统未初始化"
                    }
                }
            }
        }
    }
)
async def create_qa_pair(request: QAPairCreate):
    """
    创建单个问答对

    Args:
        request: 问答对创建请求，包含问题、答案等信息

    Returns:
        BaseResponse: 创建结果，包含问答对ID或错误信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.create_qa_pair(request)
    except Exception as e:
        logger.error(f"Create QA pair error: {e}")
        raise HTTPException(status_code=500, detail=f"创建问答对失败: {str(e)}")


@router.post(
    "/pairs/batch",
    response_model=BaseResponse,
    summary="批量创建问答对",
    description="""
    批量创建多个问答对，支持高效的批量处理。

    **功能特性：**
    - 批量向量化处理
    - 自动重复检查
    - 事务性操作
    - 详细的处理统计

    **限制条件：**
    - 单次最多100个问答对
    - 每个问答对遵循单个创建的验证规则

    **处理逻辑：**
    - 按分类分组处理
    - 跳过重复问题
    - 记录失败项目
    - 返回详细统计

    **返回统计：**
    - added_count: 成功添加数量
    - skipped_count: 跳过重复数量
    - failed_count: 失败数量
    - added_ids: 成功添加的ID列表
    - skipped_duplicates: 跳过的重复项详情
    - failed_items: 失败项目详情
    """,
    responses={
        200: {
            "description": "批量处理完成",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "批量创建完成：成功添加 8 个问答对，跳过 2 个重复问题",
                        "data": {
                            "added_count": 8,
                            "skipped_count": 2,
                            "failed_count": 0,
                            "qa_ids": ["qa_12345678", "qa_87654321"],
                            "skipped_duplicates": [
                                {
                                    "question": "重复的问题",
                                    "similarity": 0.985,
                                    "existing_qa_id": "qa_existing"
                                }
                            ],
                            "failed_items": []
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "qa_pairs"],
                                "msg": "问答对列表不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_qa_pairs_batch(request: QAPairBatchCreate):
    """
    批量创建问答对

    Args:
        request: 批量创建请求，包含问答对列表

    Returns:
        BaseResponse: 批量创建结果，包含详细的处理统计信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.create_qa_pairs_batch(request)
    except Exception as e:
        logger.error(f"Batch create QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"批量创建问答对失败: {str(e)}")


@router.post(
    "/query",
    response_model=QAQueryResponse,
    summary="问答查询",
    description="""
    基于向量相似度的智能问答查询。

    **查询机制：**
    - 向量相似度匹配
    - 可配置相似度阈值
    - 支持分类过滤
    - 返回多个候选结果

    **参数说明：**
    - question: 查询问题（必填，1-2000字符）
    - top_k: 返回结果数量（可选，1-20，默认1）
    - min_similarity: 最小相似度阈值（可选，0.0-1.0）
    - category: 分类过滤（可选，仅在指定分类中查询）

    **相似度阈值：**
    - 系统默认阈值：0.98（高精度匹配）
    - 可通过min_similarity参数覆盖
    - 低于阈值的结果不会返回

    **返回结果：**
    - found: 是否找到匹配结果
    - answer: 最佳答案
    - similarity: 相似度分数
    - confidence: 置信度
    - qa_id: 问答对ID
    - all_results: 所有候选结果
    - response_time: 查询耗时

    **性能说明：**
    - 默认查询超时：240秒
    - 可通过.env的LLM_TIMEOUT配置调整
    - 向量检索通常在毫秒级完成
    """,
    responses={
        200: {
            "description": "查询成功",
            "content": {
                "application/json": {
                    "examples": {
                        "found": {
                            "summary": "找到匹配结果",
                            "value": {
                                "success": True,
                                "found": True,
                                "answer": "这是匹配的答案",
                                "question": "匹配的问题",
                                "similarity": 0.985,
                                "confidence": 1.0,
                                "category": "general",
                                "qa_id": "qa_12345678",
                                "response_time": 0.15,
                                "all_results": [
                                    {
                                        "qa_pair": {
                                            "id": "qa_12345678",
                                            "question": "匹配的问题",
                                            "answer": "这是匹配的答案",
                                            "category": "general"
                                        },
                                        "similarity": 0.985,
                                        "rank": 1
                                    }
                                ]
                            }
                        },
                        "not_found": {
                            "summary": "未找到匹配结果",
                            "value": {
                                "success": True,
                                "found": False,
                                "response_time": 0.08,
                                "message": "未找到匹配的问答对",
                                "best_similarity": 0.75
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "question"],
                                "msg": "查询问题不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def query_qa(request: QAQueryRequest):
    """
    执行问答查询

    Args:
        request: 查询请求，包含问题和查询参数

    Returns:
        QAQueryResponse: 查询结果，包含答案和相似度信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.query_qa(request)
    except Exception as e:
        logger.error(f"QA query error: {e}")
        raise HTTPException(status_code=500, detail=f"问答查询失败: {str(e)}")


@router.post("/query/batch", response_model=QABatchQueryResponse, summary="批量问答查询", description="单条 LLM 请求默认超时 240 秒；批量接口可通过 body.timeout 控制聚合等待超时")
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
            
            for result in query_results:
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


@router.get("/categories", response_model=BaseResponse, summary="获取问答分类列表")
async def get_qa_categories():
    """
    获取所有问答分类列表

    Returns:
        BaseResponse: 分类列表和统计信息
    """
    try:
        handler = await get_qa_api_handler()

        # 检查 QA 管理器是否已初始化
        if not handler.qa_manager:
            logger.error("QA manager is not initialized")
            raise HTTPException(status_code=500, detail="问答系统未初始化")

        categories = handler.qa_manager.get_categories()
        category_stats = handler.qa_manager.get_category_stats()

        return BaseResponse(
            success=True,
            message=f"获取分类列表成功，共 {len(categories)} 个分类",
            data={
                "categories": categories,
                "category_stats": category_stats,
                "total_categories": len(categories)
            }
        )
    except Exception as e:
        logger.error(f"Get QA categories error: {e}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")


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
            elif file_type.lower() == "csv":
                # 导入CSV文件
                success = await handler.qa_handler.import_from_csv(temp_file_path)
                if success:
                    return BaseResponse(
                        success=True,
                        message="CSV文件导入成功"
                    )
                else:
                    return BaseResponse(
                        success=False,
                        message="CSV文件导入失败",
                        error_code="IMPORT_FAILED"
                    )
            elif file_type.lower() == "xlsx":
                # 导入Excel文件
                success = await handler.qa_handler.import_from_excel(temp_file_path)
                if success:
                    return BaseResponse(
                        success=True,
                        message="Excel文件导入成功"
                    )
                else:
                    return BaseResponse(
                        success=False,
                        message="Excel文件导入失败",
                        error_code="IMPORT_FAILED"
                    )
            else:
                return BaseResponse(
                    success=False,
                    message=f"暂不支持 {file_type} 格式的文件导入，支持的格式: json, csv, xlsx",
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
            
            # 安全地获取统计信息
            storage_stats = stats.get("data", {}).get("storage_stats", {})
            qa_pairs_count = storage_stats.get("total_pairs", 0)

            backup_response = QABackupResponse(
                success=True,
                backup_file=backup_file,
                backup_size=backup_size,
                qa_pairs_count=qa_pairs_count,
                created_at=time.time(),
                message="备份创建成功"
            )
            
            return BaseResponse(
                success=True,
                message="问答数据备份成功",
                data=backup_response.model_dump()
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


@router.delete(
    "/clear",
    response_model=BaseResponse,
    summary="清空问答数据",
    description="""
    清空问答系统中的所有数据，包括问答对和向量索引。

    **⚠️ 危险操作警告：**
    - 此操作不可逆转
    - 将删除所有问答对
    - 将清空所有向量索引
    - 将重置所有分类

    **清空范围：**
    - 所有分类的问答对
    - 向量数据库索引
    - 问答对元数据
    - 统计信息重置

    **操作后果：**
    - 问答对数量归零
    - 查询将无法找到任何结果
    - 需要重新导入或创建数据

    **使用场景：**
    - 系统重置
    - 数据迁移前清理
    - 测试环境重置

    **建议操作：**
    - 操作前先备份数据
    - 确认业务影响
    - 在维护窗口执行
    """,
    responses={
        200: {
            "description": "清空成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "问答数据已清空"
                    }
                }
            }
        },
        500: {
            "description": "清空失败",
            "content": {
                "application/json": {
                    "examples": {
                        "not_initialized": {
                            "summary": "系统未初始化",
                            "value": {
                                "success": False,
                                "message": "问答系统未初始化",
                                "error_code": "QA_NOT_INITIALIZED"
                            }
                        },
                        "operation_failed": {
                            "summary": "操作失败",
                            "value": {
                                "success": False,
                                "message": "清空问答数据失败：存储访问错误",
                                "error_code": "HTTP_500"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def clear_qa_data():
    """
    清空所有问答数据

    Returns:
        BaseResponse: 清空结果，包含操作状态信息
    """
    try:
        handler = await get_qa_api_handler()

        # 检查处理器是否已初始化
        if not handler.initialized or not handler.qa_manager:
            return BaseResponse(
                success=False,
                message="问答系统未初始化",
                error_code="QA_NOT_INITIALIZED"
            )

        # 使用存储的drop方法清空所有数据
        if hasattr(handler.qa_manager, 'storage') and handler.qa_manager.storage:
            # 对于CategoryQAStorage，需要清空所有分类的数据
            if hasattr(handler.qa_manager.storage, 'category_storages'):
                # 清空所有分类存储
                for category, storage in handler.qa_manager.storage.category_storages.items():
                    await storage.drop()
                    logger.info(f"Cleared category '{category}' data")

                # 清空全局索引
                handler.qa_manager.storage.qa_pairs.clear()
                handler.qa_manager.storage.category_storages.clear()

                logger.info("All category data cleared")
            else:
                # 对于单一存储，直接调用drop方法
                await handler.qa_manager.storage.drop()
                logger.info("QA storage data cleared")

        return BaseResponse(
            success=True,
            message="问答数据已清空"
        )

    except Exception as e:
        logger.error(f"Clear QA data error: {e}")
        return BaseResponse(
            success=False,
            message=f"清空问答数据失败：{str(e)}",
            error_code="HTTP_500"
        )


# 注意：生命周期事件处理已移至 initialize/app_initializer.py 中的 lifespan 函数
# QA系统的初始化和清理现在由 initialize/service_initializer.py 管理


@router.delete(
    "/categories/{category}",
    response_model=BaseResponse,
    summary="删除特定分类的问答数据",
    description="""
    删除指定分类下的所有问答对和相关数据。

    **删除范围：**
    - 指定分类的所有问答对
    - 对应的向量索引
    - 分类统计信息

    **操作特点：**
    - 仅影响指定分类
    - 其他分类数据保持不变
    - 操作不可逆转

    **参数说明：**
    - category: 分类名称（路径参数，必填）

    **返回信息：**
    - deleted_count: 删除的问答对数量
    - category: 删除的分类名称
    - message: 操作结果描述

    **使用场景：**
    - 分类数据清理
    - 过时内容移除
    - 分类重构

    **注意事项：**
    - 分类名称区分大小写
    - 删除后分类将从列表中消失
    - 建议操作前确认分类内容
    """,
    responses={
        200: {
            "description": "删除成功",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "删除成功",
                            "value": {
                                "success": True,
                                "message": "成功删除分类 'test' 及其 5 个问答对",
                                "data": {
                                    "deleted_count": 5,
                                    "category": "test"
                                }
                            }
                        },
                        "not_found": {
                            "summary": "分类不存在",
                            "value": {
                                "success": False,
                                "message": "分类 'nonexistent' 不存在",
                                "data": {
                                    "deleted_count": 0,
                                    "category": "nonexistent"
                                }
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "删除失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "删除分类数据失败: 存储访问错误"
                    }
                }
            }
        }
    }
)
async def delete_category_data(
    category: str = Path(
        ...,
        description="要删除的分类名称",
        example="test",
        min_length=1,
        max_length=100
    )
):
    """
    删除特定分类的所有问答数据

    Args:
        category: 要删除的分类名称

    Returns:
        BaseResponse: 删除结果，包含删除统计信息
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.delete_category(category)
    except Exception as e:
        logger.error(f"Delete category data error: {e}")
        raise HTTPException(status_code=500, detail=f"删除分类数据失败: {str(e)}")


@router.delete("/pairs", response_model=BaseResponse, summary="批量删除问答对")
async def delete_qa_pairs(request: QAPairsDeleteRequest):
    """
    根据ID列表批量删除问答对

    Args:
        request: 删除请求，包含要删除的问答对ID列表

    Returns:
        BaseResponse: 删除结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.delete_qa_pairs_by_ids(request.qa_ids)
    except Exception as e:
        logger.error(f"Delete QA pairs error: {e}")
        raise HTTPException(status_code=500, detail=f"删除问答对失败: {str(e)}")


@router.delete("/pairs/{qa_id}", response_model=BaseResponse, summary="删除单个问答对")
async def delete_single_qa_pair(qa_id: str):
    """
    删除单个问答对

    Args:
        qa_id: 要删除的问答对ID

    Returns:
        BaseResponse: 删除结果
    """
    try:
        handler = await get_qa_api_handler()
        return await handler.delete_qa_pairs_by_ids([qa_id])
    except Exception as e:
        logger.error(f"Delete single QA pair error: {e}")
        raise HTTPException(status_code=500, detail=f"删除问答对失败: {str(e)}")




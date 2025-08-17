"""
意图识别路由 - 重构版本
使用分离的API逻辑和数据模型
"""
from fastapi import APIRouter, HTTPException

from common.logging_utils import logger_manager
from api.intent_recogition_api import (
    health_check_api, analyze_intent_api, safety_check_api,
    get_status_api, get_intent_types_api, get_safety_levels_api
)
from model.request_models import IntentAnalysisRequest, SafetyCheckRequest
from model.response_models import (
    IntentAnalysisResponse, SafetyCheckResponse, ProcessorStatusResponse
)

router = APIRouter(prefix="/api/v1/intent", tags=["意图识别"])
logger = logger_manager.get_logger("intent_router")

@router.get("/health", summary="健康检查", description="检查意图识别服务的健康状态")
async def health_check():
    """健康检查"""
    try:
        result = await health_check_api()
        return result
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post("/analyze",
             response_model=IntentAnalysisResponse,
             summary="意图分析",
             description="分析查询的意图类型、安全级别并提供增强建议")
async def analyze_intent(request: IntentAnalysisRequest):
    """分析查询意图"""
    try:
        result = await analyze_intent_api(
            query=request.query,
            context=request.context
        )
        return IntentAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"意图分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"意图分析失败: {str(e)}")


@router.post("/safety-check",
             response_model=SafetyCheckResponse,
             summary="安全检查",
             description="检查内容的安全性，识别潜在风险")
async def safety_check(request: SafetyCheckRequest):
    """内容安全检查"""
    try:
        result = await safety_check_api(
            content=request.content,
            check_type=request.check_type
        )
        return SafetyCheckResponse(**result)
    except Exception as e:
        logger.error(f"安全检查失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"安全检查失败: {str(e)}")


@router.get("/status",
            response_model=ProcessorStatusResponse,
            summary="处理器状态",
            description="获取意图识别处理器的状态信息")
async def get_status():
    """获取处理器状态"""
    try:
        result = await get_status_api()
        return ProcessorStatusResponse(**result)
    except Exception as e:
        logger.error(f"状态获取失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"状态获取失败: {str(e)}")


@router.get("/intent-types",
            summary="意图类型列表",
            description="获取支持的意图类型列表")
async def get_intent_types():
    """获取意图类型列表"""
    try:
        result = await get_intent_types_api()
        return result
    except Exception as e:
        logger.error(f"意图类型获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"意图类型获取失败: {str(e)}")


@router.get("/safety-levels",
            summary="安全级别列表",
            description="获取支持的安全级别列表")
async def get_safety_levels():
    """获取安全级别列表"""
    try:
        result = await get_safety_levels_api()
        return result
    except Exception as e:
        logger.error(f"安全级别获取失败: {e}")
        raise HTTPException(status_code=500, detail=f"安全级别获取失败: {str(e)}")


# 导出路由
__all__ = ["router"]
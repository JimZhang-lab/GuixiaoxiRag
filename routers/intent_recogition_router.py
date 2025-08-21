"""
意图识别路由 - 核心功能
提供意图分析、安全检查和状态查询功能

注意：意图类型和安全级别配置相关接口已移至 /api/v1/intent-config 路由
"""
from fastapi import APIRouter, HTTPException

from common.logging_utils import logger_manager
from api.intent_recogition_api import (
    health_check_api, analyze_intent_api, safety_check_api,
    get_status_api
)
from model.request_models import IntentAnalysisRequest, SafetyCheckRequest
from model.response_models import (
    IntentAnalysisResponse, SafetyCheckResponse, ProcessorStatusResponse
)

router = APIRouter(prefix="/api/v1/intent", tags=["意图识别"])
logger = logger_manager.get_logger("intent_router")

@router.get(
    "/health",
    summary="意图识别服务健康检查",
    description="""
    检查意图识别服务的健康状态和可用性。

    **🔍 检查项目：**
    - 🤖 意图分析模型状态
    - 🛡️ 安全检查服务状态
    - 📊 处理器性能指标
    - 💾 缓存系统状态
    - 🔗 依赖服务连接

    **📈 健康状态：**
    - **healthy**: 🟢 服务正常运行
    - **degraded**: 🟡 部分功能受限
    - **unhealthy**: 🔴 服务不可用

    **🎯 使用场景：**
    - 服务监控和告警
    - 负载均衡健康检查
    - 系统状态诊断
    """,
    responses={
        200: {
            "description": "健康检查成功",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-01T12:00:00Z",
                        "services": {
                            "intent_analyzer": "healthy",
                            "safety_checker": "healthy",
                            "model_loader": "healthy"
                        },
                        "performance": {
                            "avg_response_time": 0.15,
                            "requests_per_second": 25.5
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """检查意图识别服务的健康状态"""
    try:
        result = await health_check_api()
        return result
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post(
    "/analyze",
    response_model=IntentAnalysisResponse,
    summary="智能意图分析",
    description="""
    基于AI模型分析用户查询的意图类型、安全级别并提供智能增强建议。

    **🧠 分析能力：**
    - 🎯 多维度意图识别（信息查询、任务执行、创作生成等）
    - 🛡️ 智能安全风险评估
    - 📈 查询复杂度分析
    - 💡 查询优化建议
    - 🔍 上下文理解和关联

    **📊 意图类型：**
    - **information_query**: 信息查询类（最常见）
    - **task_execution**: 任务执行类
    - **creative_generation**: 创作生成类
    - **analysis_request**: 分析请求类
    - **conversation**: 对话交流类
    - **system_command**: 系统命令类

    **🛡️ 安全级别：**
    - **safe**: 🟢 安全内容，可正常处理
    - **caution**: 🟡 需要谨慎处理的内容
    - **warning**: 🟠 存在潜在风险
    - **danger**: 🔴 高风险内容，建议拒绝

    **🔧 参数说明：**
    - **query**: 用户查询内容（必填，1-2000字符）
    - **context**: 上下文信息（可选，提供更准确的分析）
      - 可包含对话历史、用户信息等
      - 有助于提高意图识别准确性

    **📈 返回信息：**
    - **intent_type**: 识别的意图类型
    - **confidence**: 识别置信度（0.0-1.0）
    - **safety_level**: 安全级别评估
    - **risk_factors**: 风险因素列表
    - **enhancement_suggestions**: 查询优化建议
    - **processing_recommendations**: 处理建议
    - **analysis_time**: 分析耗时

    **🎯 使用场景：**
    - 🤖 智能客服系统
    - 🛡️ 内容安全审核
    - 📊 用户行为分析
    - 🔍 查询路由和优化
    - 📈 服务质量监控
    """,
    responses={
        200: {
            "description": "意图分析成功",
            "content": {
                "application/json": {
                    "examples": {
                        "information_query": {
                            "summary": "信息查询",
                            "value": {
                                "intent_type": "information_query",
                                "confidence": 0.95,
                                "safety_level": "safe",
                                "risk_factors": [],
                                "enhancement_suggestions": [
                                    "可以添加更具体的关键词",
                                    "建议指定查询的时间范围"
                                ],
                                "processing_recommendations": {
                                    "suggested_mode": "hybrid",
                                    "estimated_complexity": "medium",
                                    "recommended_timeout": 30
                                },
                                "analysis_time": 0.08
                            }
                        },
                        "risky_content": {
                            "summary": "风险内容",
                            "value": {
                                "intent_type": "system_command",
                                "confidence": 0.88,
                                "safety_level": "warning",
                                "risk_factors": [
                                    "包含系统敏感操作",
                                    "可能影响系统安全"
                                ],
                                "enhancement_suggestions": [
                                    "建议重新表述查询内容",
                                    "避免使用系统命令语法"
                                ],
                                "processing_recommendations": {
                                    "action": "require_confirmation",
                                    "alternative_suggestions": [
                                        "如果您想了解系统信息，请使用状态查询接口"
                                    ]
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
                                "loc": ["body", "query"],
                                "msg": "查询内容不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def analyze_intent(request: IntentAnalysisRequest):
    """分析用户查询的意图类型和安全级别"""
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


# 注意：意图类型和安全级别列表已移至 /api/v1/intent-config 路由
# 这些接口在配置管理路由中提供更完整的信息


# 导出路由
__all__ = ["router"]
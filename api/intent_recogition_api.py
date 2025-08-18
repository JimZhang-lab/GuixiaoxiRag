"""
意图识别API - 核心业务逻辑
提供意图识别相关的业务逻辑处理

功能包括：
- 意图分析：分析查询的意图类型和安全级别
- 安全检查：检查内容的安全性
- 健康检查：检查服务状态
- 状态获取：获取处理器状态信息

注意：意图类型和安全级别的配置管理功能已移至 intent_config_api
"""
import time
import asyncio
from typing import Dict, Any

from common.logging_utils import logger_manager
from handler.query_processor import QueryProcessor
from core.intent_recognition import ProcessorConfig
from core.common.llm_client import create_llm_function

logger = logger_manager.get_logger("intent_api")

# 全局查询处理器实例
query_processor = None
# 全局LLM函数
_llm_func = None
# LLM初始化状态
_llm_initialized = False


async def initialize_llm():
    """初始化LLM函数"""
    global _llm_func, _llm_initialized
    if not _llm_initialized:
        try:
            _llm_func = await create_llm_function(chat_template_kwargs={"enable_thinking": False})
            _llm_initialized = True
            if _llm_func:
                logger.info("LLM函数初始化成功")
            else:
                logger.warning("LLM函数初始化失败，将使用DFA回退模式")
        except Exception as e:
            logger.error(f"LLM函数初始化异常: {e}")
            _llm_func = None
            _llm_initialized = True


def set_llm_function(llm_func):
    """设置LLM函数"""
    global _llm_func, query_processor, _llm_initialized
    _llm_func = llm_func
    _llm_initialized = True
    # 重置处理器，以便使用新的LLM函数
    query_processor = None
    logger.info(f"LLM函数已设置: {llm_func is not None}")


async def get_query_processor() -> QueryProcessor:
    """获取查询处理器实例"""
    global query_processor, _llm_func

    # 确保LLM已初始化
    await initialize_llm()

    if query_processor is None:
        # 创建配置 - 优先使用大模型，失败时回退到DFA
        config = ProcessorConfig(
            confidence_threshold=0.7,
            enable_llm=_llm_func is not None,  # 只有提供了LLM函数才启用
            enable_dfa_filter=True,  # 始终启用DFA作为回退
            enable_query_enhancement=True
        )
        query_processor = QueryProcessor(llm_func=_llm_func, config=config)

        if _llm_func is not None:
            logger.info("查询处理器初始化完成 - 启用大模型优先模式")
        else:
            logger.info("查询处理器初始化完成 - 使用DFA回退模式")
    return query_processor


async def health_check_api() -> Dict[str, Any]:
    """健康检查API逻辑"""
    return {
        "status": "healthy",
        "service": "intent_recognition",
        "version": "1.0.0",
        "timestamp": time.time()
    }


async def analyze_intent_api(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """意图分析API逻辑"""
    try:
        start_time = time.time()
        processor = await get_query_processor()
        
        # 处理查询
        result = await processor.process_query(
            query=query,
            context=context
        )
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "data": result,
            "message": "意图分析完成",
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"意图分析失败: {e}", exc_info=True)
        raise Exception(f"意图分析失败: {str(e)}")


async def safety_check_api(content: str, check_type: str = "comprehensive") -> Dict[str, Any]:
    """安全检查API逻辑"""
    try:
        start_time = time.time()
        processor = await get_query_processor()
        
        # 使用核心处理器进行安全检查
        safety_result = await processor.core_processor._safety_check(content)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "data": {
                "is_safe": safety_result.is_safe,
                "safety_level": safety_result.safety_level,
                "risk_factors": safety_result.risk_factors,
                "confidence": safety_result.confidence,
                "reason": safety_result.reason,
                "sensitive_words": safety_result.sensitive_words or [],
                "filtered_text": safety_result.filtered_text
            },
            "message": "安全检查完成",
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"安全检查失败: {e}", exc_info=True)
        raise Exception(f"安全检查失败: {str(e)}")


async def get_status_api() -> Dict[str, Any]:
    """获取处理器状态API逻辑"""
    try:
        processor = await get_query_processor()
        stats = processor.get_processor_stats()
        
        return {
            "success": True,
            "data": {
                "processor_status": "healthy",
                "dfa_filter_loaded": stats.get("dfa_stats") is not None,
                "llm_available": stats["config"]["enable_llm"],
                "config": stats["config"],
                "dfa_stats": stats.get("dfa_stats"),
                "intent_types": processor.get_intent_types(),
                "safety_levels": processor.get_safety_levels()
            },
            "message": "状态获取成功"
        }
        
    except Exception as e:
        logger.error(f"状态获取失败: {e}", exc_info=True)
        raise Exception(f"状态获取失败: {str(e)}")


# 注意：get_intent_types_api 和 get_safety_levels_api 已移至配置管理API
# 这些功能现在通过 /api/v1/intent-config/intent-types 和相关接口提供


# 导出所有API函数
__all__ = [
    "initialize_llm",
    "set_llm_function",
    "get_query_processor",
    "health_check_api",
    "analyze_intent_api",
    "safety_check_api",
    "get_status_api"
    # 注意：get_intent_types_api 和 get_safety_levels_api 已移至配置管理API
]

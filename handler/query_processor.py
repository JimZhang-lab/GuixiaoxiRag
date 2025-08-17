"""
查询处理器 - 基于大模型的意图识别、意图补充、意图修复和内容过滤
优化版本 - 整合核心模块，提升错误处理和性能
"""
import time
from typing import Dict, List, Optional, Any

from common.logging_utils import logger_manager
from core.intent_recognition import (
    IntentRecognitionProcessor, ProcessorConfig,
    QueryIntentType, ContentSafetyLevel, QueryAnalysisResult
)

# 意图类型映射（用于向后兼容）
INTENT_TYPES = {
    "knowledge_query": "知识查询",
    "factual_question": "事实性问题",
    "analytical_question": "分析性问题",
    "procedural_question": "程序性问题",
    "creative_request": "创意请求",
    "greeting": "问候",
    "unclear": "意图不明确",
    "illegal_content": "非法内容"
}

# 安全级别映射（用于向后兼容）
SAFETY_LEVELS = {
    "safe": "安全",
    "suspicious": "可疑",
    "unsafe": "不安全",
    "illegal": "非法"
}


class QueryProcessor:
    """基于大模型的查询处理器 - 优化版本"""

    def __init__(self, llm_func=None, config: ProcessorConfig = None):
        self.logger = logger_manager.setup_query_logger()

        # 初始化配置
        self.config = config or ProcessorConfig(
            confidence_threshold=0.7,
            enable_llm=llm_func is not None,
            enable_dfa_filter=True,
            enable_query_enhancement=True
        )

        # 初始化核心处理器
        self.core_processor = IntentRecognitionProcessor(
            config=self.config,
            llm_func=llm_func
        )

        self.logger.info("查询处理器初始化完成")

    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """基于大模型的查询处理 - 使用核心处理器"""
        start_time = time.time()

        try:
            self.logger.info(f"开始处理查询: {query[:50]}...")

            # 使用核心处理器进行处理
            result = await self.core_processor.process_query(query, context)

            # 转换为兼容格式
            return self._convert_to_legacy_format(result)

        except Exception as e:
            self.logger.error(f"查询处理失败: {str(e)}", exc_info=True)
            return {
                "original_query": query,
                "processed_query": query,
                "intent_type": "unclear",
                "safety_level": "suspicious",
                "confidence": 0.0,
                "suggestions": ["查询处理出现错误，请重试"],
                "risk_factors": ["处理异常"],
                "enhanced_query": None,
                "should_reject": True,
                "rejection_reason": "查询处理异常",
                "safety_tips": [],
                "safe_alternatives": [],
                "processing_time": time.time() - start_time
            }

    def _convert_to_legacy_format(self, result: QueryAnalysisResult) -> Dict[str, Any]:
        """转换为向后兼容的格式"""
        return {
            "original_query": result.original_query,
            "processed_query": result.processed_query,
            "intent_type": result.intent_type.value,
            "safety_level": result.safety_level.value,
            "confidence": result.confidence,
            "suggestions": result.suggestions,
            "risk_factors": result.risk_factors,
            "enhanced_query": result.enhanced_query,
            "should_reject": result.should_reject,
            "rejection_reason": result.rejection_reason,
            "safety_tips": result.safety_tips,
            "safe_alternatives": result.safe_alternatives,
            "processing_time": result.processing_time
        }

    # 向后兼容性方法
    def get_intent_types(self) -> Dict[str, str]:
        """获取意图类型映射"""
        return INTENT_TYPES

    def get_safety_levels(self) -> Dict[str, str]:
        """获取安全级别映射"""
        return SAFETY_LEVELS

    def get_processor_stats(self) -> Dict[str, Any]:
        """获取处理器统计信息"""
        return {
            "config": {
                "confidence_threshold": self.config.confidence_threshold,
                "enable_llm": self.config.enable_llm,
                "enable_dfa_filter": self.config.enable_dfa_filter,
                "enable_query_enhancement": self.config.enable_query_enhancement
            },
            "dfa_stats": (
                self.core_processor.sensitive_word_manager.dfa_filter.get_stats()
                if self.core_processor.sensitive_word_manager and
                   self.core_processor.sensitive_word_manager.dfa_filter
                else None
            )
        }






# 导出查询处理器
__all__ = ["QueryProcessor", "INTENT_TYPES", "SAFETY_LEVELS"]

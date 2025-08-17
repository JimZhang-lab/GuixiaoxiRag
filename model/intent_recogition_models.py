"""
意图识别数据模型
包含意图识别相关的核心数据模型定义
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from core.intent_recognition import QueryIntentType, ContentSafetyLevel


class IntentAnalysisResult(BaseModel):
    """意图分析结果模型"""
    original_query: str = Field(description="原始查询")
    processed_query: str = Field(description="处理后查询")
    intent_type: str = Field(description="意图类型")
    safety_level: str = Field(description="安全级别")
    confidence: float = Field(description="置信度", ge=0.0, le=1.0)
    suggestions: list = Field(default_factory=list, description="建议列表")
    risk_factors: list = Field(default_factory=list, description="风险因素")
    enhanced_query: Optional[str] = Field(default=None, description="增强查询")
    should_reject: bool = Field(default=False, description="是否应该拒绝")
    rejection_reason: Optional[str] = Field(default=None, description="拒绝原因")
    safety_tips: list = Field(default_factory=list, description="安全提示")
    safe_alternatives: list = Field(default_factory=list, description="安全替代建议")
    processing_time: float = Field(description="处理时间（秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_query": "什么是人工智能？",
                "processed_query": "什么是人工智能？",
                "intent_type": "knowledge_query",
                "safety_level": "safe",
                "confidence": 0.95,
                "suggestions": ["可以询问具体的AI应用领域"],
                "risk_factors": [],
                "enhanced_query": "请详细介绍人工智能的概念、发展历史和主要应用领域",
                "should_reject": False,
                "rejection_reason": None,
                "safety_tips": [],
                "safe_alternatives": [],
                "processing_time": 0.5
            }
        }


class SafetyCheckResult(BaseModel):
    """安全检查结果模型"""
    is_safe: bool = Field(description="是否安全")
    safety_level: str = Field(description="安全级别")
    risk_factors: list = Field(default_factory=list, description="风险因素")
    confidence: float = Field(description="置信度", ge=0.0, le=1.0)
    reason: str = Field(description="检查原因")
    intent_direction: Optional[str] = Field(default=None, description="意图方向")
    sensitive_words: list = Field(default_factory=list, description="敏感词列表")
    filtered_text: Optional[str] = Field(default=None, description="过滤后文本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_safe": True,
                "safety_level": "safe",
                "risk_factors": [],
                "confidence": 0.95,
                "reason": "内容安全，无风险因素",
                "intent_direction": "neutral",
                "sensitive_words": [],
                "filtered_text": None
            }
        }


class ProcessorStatus(BaseModel):
    """处理器状态模型"""
    processor_status: str = Field(description="处理器状态")
    dfa_filter_loaded: bool = Field(description="DFA过滤器是否已加载")
    llm_available: bool = Field(description="LLM是否可用")
    config: Dict[str, Any] = Field(description="配置信息")
    dfa_stats: Optional[Dict[str, Any]] = Field(default=None, description="DFA统计信息")
    intent_types: Dict[str, str] = Field(description="意图类型映射")
    safety_levels: Dict[str, str] = Field(description="安全级别映射")
    
    class Config:
        json_schema_extra = {
            "example": {
                "processor_status": "healthy",
                "dfa_filter_loaded": True,
                "llm_available": True,
                "config": {
                    "confidence_threshold": 0.7,
                    "enable_llm": True,
                    "enable_dfa_filter": True,
                    "enable_query_enhancement": True
                },
                "dfa_stats": {
                    "total_words": 79388,
                    "tree_nodes": 150000,
                    "case_sensitive": False,
                    "fuzzy_match": True
                },
                "intent_types": {
                    "knowledge_query": "知识查询",
                    "factual_question": "事实性问题"
                },
                "safety_levels": {
                    "safe": "安全",
                    "suspicious": "可疑"
                }
            }
        }


class IntentTypeInfo(BaseModel):
    """意图类型信息模型"""
    intent_types: Dict[str, str] = Field(description="意图类型映射")
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent_types": {
                    "knowledge_query": "知识查询",
                    "factual_question": "事实性问题",
                    "analytical_question": "分析性问题",
                    "procedural_question": "程序性问题",
                    "creative_request": "创意请求",
                    "greeting": "问候",
                    "unclear": "意图不明确",
                    "illegal_content": "非法内容"
                }
            }
        }


class SafetyLevelInfo(BaseModel):
    """安全级别信息模型"""
    safety_levels: Dict[str, str] = Field(description="安全级别映射")
    
    class Config:
        json_schema_extra = {
            "example": {
                "safety_levels": {
                    "safe": "安全",
                    "suspicious": "可疑",
                    "unsafe": "不安全",
                    "illegal": "非法"
                }
            }
        }


# 导出所有模型
__all__ = [
    "IntentAnalysisResult",
    "SafetyCheckResult", 
    "ProcessorStatus",
    "IntentTypeInfo",
    "SafetyLevelInfo"
]

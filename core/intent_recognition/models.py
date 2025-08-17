"""
意图识别核心数据模型
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


class QueryIntentType(Enum):
    """查询意图类型"""
    KNOWLEDGE_QUERY = "knowledge_query"  # 知识查询
    FACTUAL_QUESTION = "factual_question"  # 事实性问题
    ANALYTICAL_QUESTION = "analytical_question"  # 分析性问题
    PROCEDURAL_QUESTION = "procedural_question"  # 程序性问题
    CREATIVE_REQUEST = "creative_request"  # 创意请求
    GREETING = "greeting"  # 问候
    UNCLEAR = "unclear"  # 意图不明确
    ILLEGAL_CONTENT = "illegal_content"  # 非法内容


class ContentSafetyLevel(Enum):
    """内容安全级别"""
    SAFE = "safe"  # 安全
    SUSPICIOUS = "suspicious"  # 可疑
    UNSAFE = "unsafe"  # 不安全
    ILLEGAL = "illegal"  # 非法


@dataclass
class QueryAnalysisResult:
    """查询分析结果"""
    original_query: str
    processed_query: str
    intent_type: QueryIntentType
    safety_level: ContentSafetyLevel
    confidence: float
    suggestions: List[str]
    risk_factors: List[str]
    enhanced_query: Optional[str] = None
    should_reject: bool = False
    rejection_reason: Optional[str] = None
    safety_tips: List[str] = None
    safe_alternatives: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        """初始化后处理"""
        if self.safety_tips is None:
            self.safety_tips = []
        if self.safe_alternatives is None:
            self.safe_alternatives = []


@dataclass
class SafetyCheckResult:
    """安全检查结果"""
    is_safe: bool
    safety_level: str
    risk_factors: List[str]
    confidence: float
    reason: str
    intent_direction: Optional[str] = None
    sensitive_words: List[str] = None
    filtered_text: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.sensitive_words is None:
            self.sensitive_words = []


@dataclass
class IntentAnalysisResult:
    """意图分析结果"""
    intent_type: str
    confidence: float
    reason: str
    keywords: List[str]
    
    def __post_init__(self):
        """初始化后处理"""
        if self.keywords is None:
            self.keywords = []


@dataclass
class QueryEnhancementResult:
    """查询增强结果"""
    should_enhance: bool
    enhanced_query: Optional[str]
    enhancement_reason: str
    suggestions: List[str]
    
    def __post_init__(self):
        """初始化后处理"""
        if self.suggestions is None:
            self.suggestions = []


class ProcessorConfig:
    """处理器配置"""
    
    def __init__(self, 
                 confidence_threshold: float = 0.7,
                 enable_llm: bool = True,
                 enable_dfa_filter: bool = True,
                 enable_query_enhancement: bool = True,
                 sensitive_vocabulary_path: str = "core/intent_recognition/sensitive_vocabulary"):
        self.confidence_threshold = confidence_threshold
        self.enable_llm = enable_llm
        self.enable_dfa_filter = enable_dfa_filter
        self.enable_query_enhancement = enable_query_enhancement
        self.sensitive_vocabulary_path = sensitive_vocabulary_path


# 导出所有模型
__all__ = [
    "QueryIntentType",
    "ContentSafetyLevel", 
    "QueryAnalysisResult",
    "SafetyCheckResult",
    "IntentAnalysisResult",
    "QueryEnhancementResult",
    "ProcessorConfig"
]

"""
意图识别核心数据模型
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


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

    def __post_init__(self):
        """初始化后处理"""
        if self.safety_tips is None:
            self.safety_tips = []
        if self.safe_alternatives is None:
            self.safe_alternatives = []

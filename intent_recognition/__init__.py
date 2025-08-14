"""
意图识别服务模块

提供独立的查询意图识别、安全检查和查询增强功能
"""

from .core.processor import QueryProcessor
from .core.models import (
    QueryIntentType,
    ContentSafetyLevel,
    QueryAnalysisResult
)
from .api.server import create_intent_app
from .config.settings import IntentRecognitionConfig

__version__ = "1.0.0"
__author__ = "GuiXiaoXi Team"

__all__ = [
    "QueryProcessor",
    "QueryIntentType", 
    "ContentSafetyLevel",
    "QueryAnalysisResult",
    "create_intent_app",
    "IntentRecognitionConfig"
]

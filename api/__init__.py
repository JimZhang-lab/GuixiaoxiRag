"""
API处理器模块
统一导出所有API处理器
"""

# 导入所有API处理器
from .document_api import DocumentAPI
from .query_api import QueryAPI
from .knowledge_graph_api import KnowledgeGraphAPI
from .intent_recogition_api import (
    set_llm_function,
    get_query_processor,
    health_check_api,
    analyze_intent_api,
    safety_check_api,
    get_status_api
)
from .system_api import SystemAPI
from .knowledge_base_api import KnowledgeBaseAPI
from .cache_management_api import CacheManagementAPI

# 导出所有API处理器
__all__ = [
    "DocumentAPI",
    "QueryAPI",
    "KnowledgeGraphAPI",
    "SystemAPI",
    "KnowledgeBaseAPI",
    "CacheManagementAPI",
    # 意图识别API
    "set_llm_function",
    "get_query_processor",
    "health_check_api",
    "analyze_intent_api",
    "safety_check_api",
    "get_status_api"
]
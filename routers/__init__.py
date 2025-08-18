"""
路由模块
统一导出所有路由器
"""

# 导入所有路由器
from .document_router import router as document_router
from .query_router import router as query_router
from .knowledge_graph_router import router as knowledge_graph_router
from .system_router import router as system_router
from .knowledge_base_router import router as knowledge_base_router
from .intent_recogition_router import router as intent_recogition_router
from .intent_config_router import router as intent_config_router
from .cache_management_router import router as cache_management_router
from .qa_router import router as qa_router

# 导出所有路由器
__all__ = [
    "document_router",
    "query_router",
    "knowledge_graph_router",
    "system_router",
    "knowledge_base_router",
    "intent_recogition_router",
    "intent_config_router",
    "cache_management_router",
    "qa_router"
]
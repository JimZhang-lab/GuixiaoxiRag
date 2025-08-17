"""
业务逻辑处理层
统一导出所有处理器
"""

# 核心服务
from .guixiaoxirag_service import GuiXiaoXiRagService, guixiaoxirag_service

# 查询处理器
from .query_processor import QueryProcessor

# 知识库管理器
from .knowledge_base_manager import KnowledgeBaseManager, kb_manager

# 文档处理器
from .document_processor import DocumentProcessor, document_processor

# 导出所有处理器
__all__ = [
    # 核心服务
    "GuiXiaoXiRagService",
    "guixiaoxirag_service",

    # 查询处理器
    "QueryProcessor",

    # 知识库管理器
    "KnowledgeBaseManager",
    "kb_manager",

    # 文档处理器
    "DocumentProcessor",
    "document_processor"
]